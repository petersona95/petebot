import discord
import get_secret # function to store private key

intents = discord.Intents.default()
intents.members = True


client = discord.Client(intents=intents)

messageId = 1086016325094211604

# get token from file
# with open('token.txt') as f:
#     token = f.read()

# get token from secret
token = get_secret.get_secret_contents()

@client.event # decorator
async def on_ready():
    print("bot is logged in")

@client.event
async def on_raw_reaction_add(payload):
    '''
    give a role based on a reaction emoji
    '''

    # do nothing if the reaction is on any message that isnt the role message
    if payload.message_id != messageId:
        return
    
    # figure out which channel emoji came from
    guild = client.get_guild(payload.guild_id)

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


@client.event
async def on_raw_reaction_remove(payload):
    '''
    remove a role based on a reaction emoji removal
    '''

    # do nothing if the reaction is on any message that isnt the role message
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


client.run(token)