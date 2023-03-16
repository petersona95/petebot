import discord

intents = discord.Intents.default()
intents.members = True


client = discord.Client(intents=intents)

@client.event # decorator
async def on_ready():
    print("bot is logged in")

@client.event
async def on_raw_reaction_add(payload):
    print("Hello.")

client.run('MTA4NjAxMDQyNzgwNjMyNjgwNA.GzGibV.h4sa0EfoS-mKrUr4Js5YSTx3pf1DzoH0eSIGIA')