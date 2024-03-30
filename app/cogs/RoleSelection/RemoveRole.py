import discord
from discord.ext import commands
from discord import app_commands

# py files
import gcp_secrets # function to retrieve discord private key from gcp secret manager
import firestore # used to talk to firestore
import logger # used to write logs to google log explorer as well as to stdout


class RemoveRole(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    '''
    /REMOVE_ROLE:
    Ask user for emote/role. Remove the record for that association from Firestore.
    If the association doesn't exist in Firestore let the user know.
    '''

    @app_commands.command(name="remove_role", description="Remove role/emote combination for this channel")
    @app_commands.describe(emote="Emote used to gain that role")
    async def remove_role(self, interaction: discord.Interaction, emote: str):
        try:
            logger.write_log(
                action='/remove_role',
                payload=f'User {interaction.user.name} invoked the /remove_role command',
                severity='Debug'
            )

            admin_user_id = gcp_secrets.get_secret_contents('discord-bot-admin-user-id')
            if interaction.user.id != int(admin_user_id):
                await interaction.response.send_message(f"{interaction.user.name}, you do not have permission to use this command.", ephemeral=True)
                logger.write_log(
                    action='/remove_role',
                    payload=f'User {interaction.user.name} was blocked from using the /remove_role command',
                    severity='Debug'
                )
                return
            response = firestore.remove_role(interaction.guild_id, emote)
            await interaction.response.send_message(f"Hello {interaction.user.name}, {response}")
        
        except Exception as e:
            logger.write_log(
                action='/translate',
                payload=e,
                severity='Error'
            )
            admin_user_id = gcp_secrets.get_secret_contents('discord-bot-admin-user-id')
            adminUser = interaction.guild.get_member(int(admin_user_id))
            await adminUser.send(f'An error occured in petebot; command /remove_role; {e}')
            await interaction.followup.send(f"Hello <@{interaction.user.id}>. This command has failed. A notification has been sent to admin to investigate.", ephemeral=True)
            return


async def setup(bot: commands.Bot):
    await bot.add_cog(RemoveRole(bot))