import discord
from discord import app_commands
from discord.ext import commands
import os # used to define dev/prod token

# py files
import gcp_secrets # function to retrieve discord private key from gcp secret manager
import firestore # used to talk to firestore
import logger # used to write logs to google log explorer as well as to stdout


intents = discord.Intents.default()
intents.members = True # required for removing roles
intents.message_content = True # required for slash commands

# create connection
bot = commands.Bot(command_prefix="!", intents=intents)

# determine token based on environment variable
env = os.getenv('env')
# ID of the secret to create.
if env=='dev':
    secretName = "discord-role-bot-token-dev"
elif env=='prod':
    secretName = "discord-role-bot-token"
token = gcp_secrets.get_secret_contents(secretName)


@bot.event # decorator
async def on_ready():
    logger.write_log(
        env=env,
        payload='Bot is logged in.',
        severity='Info'
    )    
    try:
        # syncing is used for /commands
        # Its used to show /command options available for users in discord itself. They're called trees in discord
        # by not defining a guild_id its considered a global tree. it can take up to 24 hours to refresh on servers
        # BUG: I shouldn't have this here because every time the shard invalidates it re-syncs the functions.
        '''
        2023-04-20 22:36:42 INFO     discord.gateway Shard ID None session has been invalidated.
        2023-04-20 22:36:47 INFO     discord.gateway Shard ID None has connected to Gateway (Session ID: 08fa2f592630f7558353482ffbd1f724).
        bot is logged in
        synced 2 command(s)
        '''
        synced = await bot.tree.sync()
        logger.write_log(
            env=env,
            payload=f"synced {len(synced)} command(s)",
            severity='Info'
        )
    except Exception as e:
        logger.write_log(
            env=env,
            payload=str(e),
            severity='Error'
        )

# SLASH COMMANDS
'''
/ADD_ROLE:
Ask user for emote/role. Create a new record for that association in Firestore
BUG: Currently using custom emoji's does not work. the interaction receives a weird format for the emoji <yup:serverid?> but the assign roles sees :yup:
'''
@bot.tree.command(name="add_role", description="Create a new role/emote combination for this channel")
@app_commands.describe(emote="Emote used to gain that role")
@app_commands.describe(role="Name of role in discord")
async def add_role(interaction: discord.Interaction, emote: str, role: str):
    # all slash commands require a response otherwise it will error
    admin_user_id = gcp_secrets.get_secret_contents('discord-bot-admin-user-id')
    if interaction.user.id != int(admin_user_id):
        await interaction.response.send_message(f"Nice try {interaction.user.name}... Only peteeee has the power to harness petebot 😈")
        return
    response = firestore.add_role(interaction.guild_id, emote, role)
    await interaction.response.send_message(f"Hello {interaction.user.name}, {response}")

'''
/REMOVE_ROLE:
Ask user for emote/role. Remove the record for that association from Firestore.
If the association doesn't exist in Firestore let the user know.
'''

@bot.tree.command(name="remove_role", description="Remove role/emote combination for this channel")
@app_commands.describe(emote="Emote used to gain that role")
async def remove_role(interaction: discord.Interaction, emote: str):
    # all slash commands require a response otherwise it will error
    admin_user_id = gcp_secrets.get_secret_contents('discord-bot-admin-user-id')
    if interaction.user.id != int(admin_user_id):
        await interaction.response.send_message(f"Nice try {interaction.user.name}... Only peteeee has the power to harness petebot 😈")
        return
    response = firestore.remove_role(interaction.guild_id, emote)
    await interaction.response.send_message(f"Hello {interaction.user.name}, {response}")

'''
!SHOW_ROLES:
Show a user every single emote/role combination in firestore.
If there are no associations in Firestore let the user know.
'''
@bot.command()
async def show_roles(ctx):
    role_list = firestore.show_roles(ctx.message.guild.id)
    # if roles exist
    if role_list:
        response = ''
        for dict in role_list:
            #for i in dict:
            response += f'\n {dict["roleEmote"]} | #{dict["roleName"]}'
        response = f'The following emote/roles are set for this server:{response}'
    else:
        response = 'There are currently no emote/roles set for this server. Add one using /add_role.'
    await ctx.send(f"Hello {ctx.message.author}, {response}")



# EVENTS
@bot.event
async def on_raw_reaction_add(payload):
    '''
    give a role based on a reaction emoji
    '''

    # get the server_config for a channel from firestore. uses the guild_id from the incoming payload
    messageId = firestore.get_messageID(payload.guild_id)

    # create a guild object used for other things.
    guild = bot.get_guild(payload.guild_id)

    # do nothing if the reaction is on any message that isnt the role message defined in firestore
    if payload.message_id != messageId:
        return

    # look up the associated role in firestore based on the emote from the payload
    # do nothing if the reaction does not match a document in firestore
    firestoreRoleName = firestore.get_role(payload.guild_id, payload.emoji.name)
    if firestoreRoleName == None:
        logger.write_log(
            env=env,
            payload=f"No Role configured for {payload.emoji.name}, taking no action.",
            severity='Info'
        )
        return

    # assign user the roleName
    discordRoleName = discord.utils.get(guild.roles, name=firestoreRoleName)
    await payload.member.add_roles(discordRoleName)

    logger.write_log(
        env=env,
        payload=f"User {payload.member} emoted {payload.emoji.name}. Adding role #{firestoreRoleName}.",
        severity='Info'
    )

@bot.event
async def on_raw_reaction_remove(payload):
    '''
    remove a role based on a reaction emoji removal
    '''

    # get the server_config for a channel from firestore. uses the guild_id from the incoming payload
    messageId = firestore.get_messageID(payload.guild_id)

    # create a guild object used for other things.
    guild = bot.get_guild(payload.guild_id)

    # do nothing if the reaction is on any message that isnt the role message defined in the config
    if payload.message_id != messageId:
        return

    # the remove_roles requires a memberid
    member = guild.get_member(payload.user_id)

    # look up the associated role in firestore based on the emote from the payload
    # do nothing if the reaction does not match a document in firestore
    firestoreRoleName = firestore.get_role(payload.guild_id, payload.emoji.name)
    if firestoreRoleName == None:
        logger.write_log(
            env=env,
            payload=f'No Role configured for {payload.emoji.name}, taking no action.',
            severity='Info'
        )
        return

    # assign user the roleName
    discordRoleName = discord.utils.get(guild.roles, name=firestoreRoleName)
    await member.remove_roles(discordRoleName)
    logger.write_log(
        env=env,
        payload=f'Removed role {firestoreRoleName} from user {payload.user_id}.',
        severity='Info'
    )

bot.run(token)