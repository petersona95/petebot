import discord
from discord.ext import commands
from discord import app_commands

# py files
import gcp_secrets # function to retrieve discord private key from gcp secret manager
import firestore # used to talk to firestore
import logger # used to write logs to google log explorer as well as to stdout


class UpdateRoleMessage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def check_admin_status(self, user_id):
        admin_user_id = gcp_secrets.get_secret_contents('discord-bot-admin-user-id')
        if user_id != int(admin_user_id):
            return False
        return True
    
    async def check_for_message(self, interaction): 
        # init occurs when the cog is loaded. We want something to run when the /command is called
        messageDict = firestore.get_role_message(interaction.guild_id)
        if not messageDict:
            await interaction.followup.send(f"A role message has not been defined for this server. Please create a role selection message by using /set_role_message")
            return
        try:
            channel = self.bot.get_channel(messageDict['channelID'])
            message = await channel.fetch_message(messageDict['messageID'])
        except discord.errors.NotFound: #if a NotFound error appears, the message is either not in this channel or deleted
            await interaction.followup.send(f"The channel or message originally set with /set_role_message no longer exists. Please create a new role selection message by using /set_role_message")
            return
        return messageDict, message
    
    async def update_role_message(self, interaction, messageDict, message):
        '''
        interaction: discord interaction object
        messageDict: dictionary of message data from firestore
        message: discord message object to edit
        '''
        # update the description of the role message by editing the existing message
        # first, get a list of roles for the description. We need to recreate the message entirely
        role_list = firestore.show_roles(interaction.guild_id)
        # if roles exist, add them first to description
        description = messageDict['messageDescription'] + '\n---'
        for dict in role_list:
            description += f'\n{dict["roleEmote"]} | <@&{dict["roleID"]}>'

        # update the message
        embed = discord.Embed(
            colour=discord.Color.dark_teal(),
            title=messageDict['messageTitle'],
            description=description
            # initial embed will tell the user to add new roles       
            )
        await message.edit(embed=embed)

        # add an emote to the role message for each role in role_list
        for dict in role_list:
            await message.add_reaction(dict['roleEmote'])

    '''
    /ADD_ROLE:
    Ask user for emote/role. Create a new record for that association in Firestore
    '''
    @app_commands.command(name="add_role", description="Create a new role/emote combination on the role selection message.")
    @app_commands.describe(emote="Emote used to gain that role")
    @app_commands.describe(role="Name of role in discord (role will be created if it does not exist)")
    async def add_role(self, interaction: discord.Interaction, emote: str, role: str):
        try:
            logger.write_log(
                action='/add_role',
                payload=f'User {interaction.user.name} invoked the /add_role command',
                severity='Debug'
            )
            # message can take longer than 3 second timeout. defer for 5 seconds
            await interaction.response.defer(ephemeral=True)

            # check for admin status
            if not self.check_admin_status(interaction.user.id):
                await interaction.response.send_message(f"{interaction.user.name}, you do not have permission to use this command.", ephemeral=True)
                logger.write_log(
                    action='Check Admin Status',
                    payload=f'User {interaction.user.name} was blocked from using the /remove_role command',
                    severity='Debug'
                )
                return

            # get existing message data from firestore
            # if either are none, exception already handled in check_for_message
            messageDict, message = await self.check_for_message(interaction)
            if not messageDict or not message:
                return

            # check if a discord role exists. if it does not, create one
            existingRole = discord.utils.get(interaction.guild.roles, name=str(role).lower())
            if not existingRole: # if a role doesnt exist, create one
                await interaction.guild.create_role(name=str(role).lower())

            # update firestore
            roleID = discord.utils.get(interaction.guild.roles, name=str(role).lower())
            response = firestore.add_role(interaction.guild_id, emote, role, roleID.id) # attempts to add role. If response returns it was successful            
            await self.update_role_message(interaction, messageDict, message)
            await interaction.followup.send(f"Hello {interaction.user.name}, {response}", ephemeral=True)

        except Exception as e:
            logger.write_log(
                action='/add_role',
                payload=e,
                severity='Error'
            )
            admin_user_id = gcp_secrets.get_secret_contents('discord-bot-admin-user-id')
            adminUser = interaction.guild.get_member(int(admin_user_id))
            await adminUser.send(f'An error occured in petebot; command /add_role; {e}')
            await interaction.followup.send(f"Hello <@{interaction.user.id}>. This command has failed. A notification has been sent to admin to investigate.", ephemeral=True)
            return

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
            await interaction.response.defer(ephemeral=True)

            # check for admin status
            if not self.check_admin_status(interaction.user.id):
                await interaction.response.send_message(f"{interaction.user.name}, you do not have permission to use this command.", ephemeral=True)
                logger.write_log(
                    action='Check Admin Status',
                    payload=f'User {interaction.user.name} was blocked from using the /remove_role command',
                    severity='Debug'
                )
                return

            # get existing message data from firestore
            # if either are none, exception already handled in check_for_message
            messageDict, message = await self.check_for_message(interaction)
            if not messageDict or not message:
                return

            # remove the role from firestore
            response = firestore.remove_role(interaction.guild_id, emote)
            # update the role message
            await self.update_role_message(interaction, messageDict, message)
            # respond to the user
            await interaction.followup.send(f"Hello {interaction.user.name}, {response}", ephemeral=True)

        except Exception as e:
            logger.write_log(
                action='/remove_role',
                payload=e,
                severity='Error'
            )
            admin_user_id = gcp_secrets.get_secret_contents('discord-bot-admin-user-id')
            adminUser = interaction.guild.get_member(int(admin_user_id))
            await adminUser.send(f'An error occured in petebot; command /remove_role; {e}')
            await interaction.followup.send(f"Hello <@{interaction.user.id}>. This command has failed. A notification has been sent to admin to investigate.", ephemeral=True)
            return


async def setup(bot: commands.Bot):
    await bot.add_cog(UpdateRoleMessage(bot))