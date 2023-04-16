import discord
from discord import app_commands
from discord.ext import commands
import get_secret # function to store private key
import json

intents = discord.Intents.all()
intents.members = True

# create connection
bot = commands.Bot(command_prefix="!", intents=intents)

# get config file
with open('config.json') as f:
    file_contents = f.read()

config_json = json.loads(file_contents)

# determine token based on config
if config_json["botParams"]["env"] == 'local':
    with open('token-dev.txt') as f:
        token = f.read()
elif config_json["botParams"]["env"] in ['dev', 'prod']:
    env = config_json["botParams"]["env"]
    token = get_secret.get_secret_contents(env)
else:
    print('Invalid Environment. Please check the config file and ensure env is set to local, dev or prod...')
    quit()

def get_server_config(guild):
    '''
    use the guild_id to look up the messageId
    loop over the list of server configs to get matching server
    '''
    # lookup the messageId from the config.json file
    for server in config_json['servers']:
        if server['guildID'] == guild:
            return server


@bot.event # decorator
async def on_ready():
    print("bot is logged in")
    try:
        # syncing is used for /commands
        # I believe its used to show /command options available for users
        synced = await bot.tree.sync()
        print(f"synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.tree.command(name="hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"hey {interaction.user.mention}! This is a slash command!")

@bot.tree.command(name="def_request")
@app_commands.describe(xCoordinates="Input X Coordinates for Defense Call. ex: 56")
@app_commands.describe(yCoordinates="Input Y Coordinates for Defense Call. ex: 41")
@app_commands.describe(troopCount="Input # Troops required for Defense Call. ex: 10000")
async def def_request(interaction: discord.Interaction, xCoordinates: int, yCoordinates: int, troopCount: int):
    await interaction.response.send_message(f"NEW DEFENSE CALL: {interaction.user.name} requires {troopCount} troops at ({xCoordinates} | {yCoordinates})")

@bot.event
async def on_raw_reaction_add(payload):
    '''
    give a role based on a reaction emoji
    '''

    # get the server_config for a channel from the config. uses the guild_id from the incoming payload
    server_config_json = get_server_config(payload.guild_id)
    messageId = server_config_json['messageID']

    # create a guild object used for other things.
    guild = bot.get_guild(payload.guild_id)

    # do nothing if the reaction is on any message that isnt the role message defined in the config
    if payload.message_id != messageId:
        return

    # determine which emote was used. Do nothing if no emote match
    # loop through different roles in config
    for role_config in server_config_json['roles']:
        # if role emote matches with user submission
        if role_config['roleEmote'] == payload.emoji.name:
            # assign user the roleName
            role = discord.utils.get(guild.roles, name= role_config['roleName'])
            await payload.member.add_roles(role)

@bot.event
async def on_raw_reaction_remove(payload):
    '''
    remove a role based on a reaction emoji removal
    '''

    # get the server_config for a channel from the config. uses the guild_id from the incoming payload
    server_config_json = get_server_config(payload.guild_id)
    messageId = server_config_json['messageID']

    # create a guild object used for other things.
    guild = bot.get_guild(payload.guild_id)

    # do nothing if the reaction is on any message that isnt the role message defined in the config
    if payload.message_id != messageId:
        return

    # the remove_roles requires a memberid
    member = guild.get_member(payload.user_id)

    # determine which emote was removed. Do nothing if no emote match
    # loop through different roles in config
    for role_config in server_config_json['roles']:
        # if role emote matches with user submission
        if role_config['roleEmote'] == payload.emoji.name:
            # assign user the roleName
            role = discord.utils.get(guild.roles, name= role_config['roleName'])
            await member.remove_roles(role)

bot.run(token)