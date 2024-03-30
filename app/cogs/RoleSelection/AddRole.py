import discord
from discord.ext import commands
from discord import app_commands

# py files
import gcp_secrets # function to retrieve discord private key from gcp secret manager
import firestore # used to talk to firestore
import logger # used to write logs to google log explorer as well as to stdout


class AddRole(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    '''
    /ADD_ROLE:
    Ask user for emote/role. Create a new record for that association in Firestore
    '''
    @app_commands.command(name="add_role", description="Create a new role/emote combination on the role selection message.")
    @app_commands.describe(emote="Emote used to gain that role")
    @app_commands.describe(role="Name of role in discord (role will be created if it does not exist)")
    async def add_role(self, interaction: discord.Interaction, emote: str, role: str):
        logger.write_log(
            action='/add_role',
            payload=f'User {interaction.user.name} invoked the /add_role command',
            severity='Debug'
        )
        # message can take longer than 3 second timeout. defer for 5 seconds
        await interaction.response.defer(ephemeral=True)

        # check if a messageID has been defined for this server
        # if a messageID has not been defined in the database
        try:
            messageDict = firestore.get_role_message(interaction.guild_id)
        except Exception as e:
            logger.write_log(
                action='/translate',
                payload=str(e),
                severity='Error'
            )
            admin_user_id = gcp_secrets.get_secret_contents('discord-bot-admin-user-id')
            adminUser = interaction.guild.get_member(int(admin_user_id))
            await adminUser.send(f'An error occured in petebot; command /add_role; {e}')
            await interaction.followup.send(f"Hello <@{interaction.user.id}>. This command has failed. A notification has been sent to admin to investigate.", ephemeral=True)
            return

        if messageDict:
            try:
                channel = self.bot.get_channel(messageDict['channelID'])
                message = await channel.fetch_message(messageDict['messageID'])
            except discord.errors.NotFound: #if a NotFound error appears, the message is either not in this channel or deleted
                await interaction.followup.send(f"The channel or message originally set with /set_role_message no longer exists. Please create a new role selection message by using /set_role_message")
                return
        else:
            await interaction.followup.send(f"A role message has not been defined for this server. Please create a role selection message by using /set_role_message")
            return

        # check if a discord role exists. if it does not, create one
        try:
            existingRole = discord.utils.get(interaction.guild.roles, name=str(role).lower())
            if existingRole == None: # if a role doesnt exist, create one
                await interaction.guild.create_role(name=str(role).lower())
        except Exception as e:
            logger.write_log(
                action='/translate',
                payload=str(e),
                severity='Error'
            )
            admin_user_id = gcp_secrets.get_secret_contents('discord-bot-admin-user-id')
            adminUser = interaction.guild.get_member(int(admin_user_id))
            await adminUser.send(f'An error occured in petebot; command /add_role; {e}')
            await interaction.followup.send(f"Hello <@{interaction.user.id}>. This command has failed. A notification has been sent to admin to investigate.", ephemeral=True)
            return    

        # update firestore
        try:
            admin_user_id = gcp_secrets.get_secret_contents('discord-bot-admin-user-id')
            if interaction.user.id != int(admin_user_id):
                await interaction.followup.send(f"{interaction.user.name}, you do not have permission to use this command.", ephemeral=True)
                logger.write_log(
                    action='/add_role',
                    payload=f'User {interaction.user.name} was blocked from using the /add_role command',
                    severity='Debug'
                )
                return
            roleID = discord.utils.get(interaction.guild.roles, name=str(role).lower())
            firestore.add_role(interaction.guild_id, emote, role, roleID.id) # attempts to add role. If response returns it was successful
            logger.write_log(
                    action='/add_role',
                    payload=f'Successfully added a firestore entry for {emote}, {role} to guild {interaction.guild_id}',
                    severity='Debug'
                )

        except Exception as e:
            logger.write_log(
                action='/add_role',
                payload=str(e),
                severity='Error'
            )
            admin_user_id = gcp_secrets.get_secret_contents('discord-bot-admin-user-id')
            adminUser = interaction.guild.get_member(int(admin_user_id))
            await adminUser.send(f'An error occured in petebot; command /add_role; {e}')
            await interaction.followup.send(f"Hello <@{interaction.user.id}>. This command has failed. A notification has been sent to admin to investigate.", ephemeral=True)
            return
        
        try:
            # update the description of the role message by editing the existing message
            # first, get a list of roles for the description. We need to recreate the message entirely
            role_list = firestore.show_roles(interaction.guild_id)
            # if roles exist, add them first to description
            description = ''
            newRoleId = '' # keep track of the role we're trying to add to the list. Use this for the followup message
            for dict in role_list:
                description += f'\n{dict["roleEmote"]} | <@&{dict["roleID"]}>'
                if dict['roleEmote'] == emote:
                    newRoleId = dict['roleID']

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

            # notify the user of success
            await interaction.followup.send(f'Successfully added a new role selection for {emote} | <@&{newRoleId}>',ephemeral=True)

        except Exception as e:
            logger.write_log(
                action='/add_role',
                payload=str(e),
                severity='Error'
            )
            admin_user_id = gcp_secrets.get_secret_contents('discord-bot-admin-user-id')
            adminUser = interaction.guild.get_member(int(admin_user_id))
            await adminUser.send(f'An error occured in petebot; command /add_role; {e}')
            await interaction.followup.send(f"Hello <@{interaction.user.id}>. This command has failed. A notification has been sent to admin to investigate.", ephemeral=True)
            return


async def setup(bot: commands.Bot):
    await bot.add_cog(AddRole(bot))