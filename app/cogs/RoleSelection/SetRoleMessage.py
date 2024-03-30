import discord
from discord.ext import commands
from discord import app_commands

# py files
import gcp_secrets # function to retrieve discord private key from gcp secret manager
import firestore # used to talk to firestore
import logger # used to write logs to google log explorer as well as to stdout


class SetRoleMessage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    '''
    /SET_ROLE_MESSAGE:
    Create a new SELECT ROLE message.
    '''
    @app_commands.command(name="set_role_message", description="Create a message in the current channel for role selection.")
    @app_commands.describe(title="What is the title of your welcome message? ex: Welcome to my channel! Please select a role from the options below.")
    async def set_role_message(self, interaction: discord.Interaction, title: str):
        try:
            logger.write_log(
            action='/set_role_message',
            payload=f'User {interaction.user} invoked the /set_title_message command.',
            severity='Debug'
            )
            
            # create an initial embed as a base point
            embed = discord.Embed(
                colour=discord.Color.dark_teal(),
                title=title,
                description='Use /add_role to add new role|emote combinations in your channel. You can only have one role selection message active at a time, so using /set_role_message again will replace this message.'
                # initial embed will tell the user to add new roles       
                )
            await interaction.response.send_message(embed=embed)
            # get the messageID for this role_message
            message = await interaction.original_response()
            # add messageID to firestore
            firestore.set_role_message(interaction.guild_id, message.id, interaction.channel_id, title)

        except Exception as e:
            logger.write_log(
                action='/translate',
                payload=e,
                severity='Error'
            )
            admin_user_id = gcp_secrets.get_secret_contents('discord-bot-admin-user-id')
            adminUser = interaction.guild.get_member(int(admin_user_id))
            await adminUser.send(f'An error occured in petebot; command /set_role_message; channel {interaction.channel_id}; {e}')
            await interaction.followup.send(f"Hello <@{interaction.user.id}>. This command has failed. A notification has been sent to admin to investigate.", ephemeral=True)
            return


async def setup(bot: commands.Bot):
    await bot.add_cog(SetRoleMessage(bot))