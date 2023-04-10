import discord
import get_secret # function to store private key
import json

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

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

def get_messageId(guild):
    '''
    use the guild_id to look up the messageId
    '''
    # lookup the messageId from the config.json file
    for server in config_json['servers']:
        if server['guildID'] == guild:
            return server['messageID']


@client.event # decorator
async def on_ready():
    print("bot is logged in")

@client.event
async def on_raw_reaction_add(payload):
    '''
    give a role based on a reaction emoji
    '''

    # get the messageId for that channel from the config. uses the guild_id from the incoming payload
    messageId = get_messageId(payload.guild_id)

    # create a guild object used for other things.
    guild = client.get_guild(payload.guild_id)

    # do nothing if the reaction is on any message that isnt the role message defined in the config
    if payload.message_id != messageId:
        return

    # if a user emojis the music note 
    if payload.emoji.name == '🎵':
        role = discord.utils.get(guild.roles, name='tunes')
        await payload.member.add_roles(role)

    elif payload.emoji.name == '🔫':
        role = discord.utils.get(guild.roles, name='game-of-the-week')
        await payload.member.add_roles(role)

    elif payload.emoji.name == '🇺🇸':
        role = discord.utils.get(guild.roles, name='politics')
        await payload.member.add_roles(role)

    elif payload.emoji.name == 'doge':
        role = discord.utils.get(guild.roles, name='memes')
        await payload.member.add_roles(role)

    elif payload.emoji.name == '⚔️':
        role = discord.utils.get(guild.roles, name='travian')
        await payload.member.add_roles(role)


@client.event
async def on_raw_reaction_remove(payload):
    '''
    remove a role based on a reaction emoji removal
    '''

    # get the messageId for that channel from the config. uses the guild_id from the incoming payload
    messageId = get_messageId(payload.guild_id)

    # do nothing if the reaction is on any message that isnt the role message defined in the config
    if payload.message_id != messageId:
        return
    
    # figure out which channel emoji came from
    guild = client.get_guild(payload.guild_id)
    # the remove_roles requires a memberid
    member = guild.get_member(payload.user_id)

    # if a user removes the music note emoji
    if payload.emoji.name == '🎵':
        role = discord.utils.get(guild.roles, name='tunes')
        await member.remove_roles(role)

    elif payload.emoji.name == '🔫':
        role = discord.utils.get(guild.roles, name='game-of-the-week')
        await member.remove_roles(role)

    elif payload.emoji.name == '🇺🇸':
        role = discord.utils.get(guild.roles, name='politics')
        await member.remove_roles(role)

    elif payload.emoji.name == 'doge':
        role = discord.utils.get(guild.roles, name='memes')
        await member.remove_roles(role)

    elif payload.emoji.name == '⚔️':
        role = discord.utils.get(guild.roles, name='travian')
        await member.remove_roles(role)


client.run(token)