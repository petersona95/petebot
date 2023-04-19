import discord
from discord import app_commands
from discord.ext import commands
import json
import os # used to define dev/prod token

# py files
import get_secret # function to retrieve discord private key from gcp secret manager
import firestore # used to talk to firestore

intents = discord.Intents.default()
intents.members = True # required for removing roles
intents.message_content = True # required for slash commands

# create connection
bot = commands.Bot(command_prefix="!", intents=intents)

# determine token based on environment variable
env = os.getenv('env')
token = get_secret.get_secret_contents(env)


@bot.event # decorator
async def on_ready():
    print("bot is logged in")
    try:
        # syncing is used for /commands
        # Its used to show /command options available for users in discord itself. They're called trees in discord
        # by not defining a guild_id its considered a global tree. it can take up to 24 hours to refresh on servers
        synced = await bot.tree.sync()
        print(f"synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.tree.command(name="hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"hey {interaction.user.mention}! This is a slash command!")

@bot.tree.command(name="add_role_channel", description="Create a new role in the config for this channel")
@app_commands.describe(role="channel role in discord")
@app_commands.describe(emote="emote used to gain access to channel")
async def add_role_channel(interaction: discord.Interaction, role: str, emote: str):
    # all slash commands require a response otherwise it will error
    await interaction.response.send_message(f"I HEAR YOU {interaction.user.name}, I'm adding {role} role and {emote} troops")

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
        print('No Role configured for ' + payload.emoji.name + ', taking no action.')
        return

    # assign user the roleName
    discordRoleName = discord.utils.get(guild.roles, name=firestoreRoleName)
    await payload.member.add_roles(discordRoleName)

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
        print('No Role configured for ' + payload.emoji.name + ', taking no action.')
        return

    # assign user the roleName
    discordRoleName = discord.utils.get(guild.roles, name=firestoreRoleName)
    await member.remove_roles(discordRoleName)

bot.run(token)