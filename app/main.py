import discord
from discord.ext import commands
import os
from pathlib import Path

# py files
import gcp_secrets # function to retrieve discord private key from gcp secret manager
import logger # used to write logs to google log explorer as well as to stdout


intents = discord.Intents.default()
intents.members = True # required for removing roles
intents.message_content = True # required for slash commands

# determine token based on environment variable
env = os.getenv('env')
# ID of the secret to create.
if env=='dev':
    secretName = "discord-role-bot-token-dev"
elif env=='prod':
    secretName = "discord-role-bot-token"
token = gcp_secrets.get_secret_contents(secretName)


# create connection
class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)

        self.cog_dir = Path('cogs')  # directory containing the cogs

    # loop through all files in the cogs folder. load each one into the bot
    async def setup_hook(self):
        for subdir, dirs, files in os.walk(self.cog_dir):
            for file in files:
                if file.endswith('.py') and file != 'CogTemplate.py': # ignore the template, its not a real cog
                    path = Path(subdir, file).relative_to('.')
                    cog = str(path.with_suffix('')).replace('/', '.')
                    await self.load_extension(cog) # load them into the bot

    async def on_ready(self):
        logger.write_log(
            action=None,
            payload='Bot has logged in.',
            severity='Debug'
        )    
        try:
            # syncing is used for /commands
            # Its used to show /command options available for users in discord itself. They're called trees in discord
            # by not defining a guild_id its considered a global tree. it can take up to 24 hours to refresh on servers
            # TODO: I shouldn't have this here because every time the shard invalidates it re-syncs the functions.
            '''
            2023-04-20 22:36:42 INFO     discord.gateway Shard ID None session has been invalidated.
            2023-04-20 22:36:47 INFO     discord.gateway Shard ID None has connected to Gateway (Session ID: 08fa2f592630f7558353482ffbd1f724).
            bot is logged in
            synced 2 command(s)
            '''
            synced = await self.tree.sync()
            logger.write_log(
                action=None,
                payload=f"synced {len(synced)} command(s)",
                severity='Debug'
            )

        except Exception as e:
            logger.write_log(
                action=None,
                payload=e,
                severity='Error'
            )


bot = Client()
bot.run(token)


# TODO: Need to create an additional cog, UpdateRole? Or duplicate the code througout. The remove_role command doesnt reset the embedded message.
# TODO: Build functionality to create/delete BOT-<rolename> roles that the bot manages. Add functionality to remove reactions - https://stackoverflow.com/questions/68813945/discord-py-how-to-remove-all-reactions-from-a-message-added-by-a-specific-user
    # i think the only way to remove reactions is  to loop over each reaction individually for each user.