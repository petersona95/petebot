import discord
from discord.ext import commands

# py files
import firestore # used to talk to firestore
import logger # used to write logs to google log explorer as well as to stdout


class OnReactionEvents(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.Cog.listener() # required for discord to recognize this event occured
    async def on_raw_reaction_add(self, payload):
        '''
        give a role based on a reaction emoji
        '''

        # get the server_config for a channel from firestore. uses the guild_id from the incoming payload
        messageId = firestore.get_role_message(payload.guild_id)['messageID']

        # create a guild object used for other things.
        guild = self.bot.get_guild(payload.guild_id)

        # do nothing if the reaction is on any message that isnt the role message defined in firestore
        if payload.message_id != messageId:
            return

        # look up the associated role in firestore based on the emote from the payload
        # do nothing if the reaction does not match a document in firestore
        firestoreRoleName = firestore.get_role(payload.guild_id, str(payload.emoji))
        if firestoreRoleName == None:
            logger.write_log(
                action='on_raw_reaction_add',
                payload=f"No Role configured for {str(payload.emoji)}, taking no action.",
                severity='Debug'
            )
            return

        # assign user the roleName
        discordRoleName = discord.utils.get(guild.roles, name=firestoreRoleName)
        await payload.member.add_roles(discordRoleName)

        logger.write_log(
            action='on_raw_reaction_add',
            payload=f"User {payload.member} emoted {str(payload.emoji)}. Adding role #{firestoreRoleName}.",
            severity='Info'
        )


    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        '''
        remove a role based on a reaction emoji removal
        '''

        # get the server_config for a channel from firestore. uses the guild_id from the incoming payload
        messageId = firestore.get_role_message(payload.guild_id)['messageID']

        # create a guild object used for other things.
        guild = self.bot.get_guild(payload.guild_id)

        # do nothing if the reaction is on any message that isnt the role message defined in the config
        if payload.message_id != messageId:
            return

        # the remove_roles requires a memberid
        member_id = guild.get_member(payload.user_id)

        # get the member's name as well
        member = await guild.fetch_member(payload.user_id)

        # look up the associated role in firestore based on the emote from the payload
        # do nothing if the reaction does not match a document in firestore
        firestoreRoleName = firestore.get_role(payload.guild_id, str(payload.emoji))
        if firestoreRoleName == None:
            logger.write_log(
                action='on_raw_reaction_remove',
                payload=f'No Role configured for {str(payload.emoji)}, taking no action.',
                severity='Debug'
            )
            return

        # assign user the roleName
        discordRoleName = discord.utils.get(guild.roles, name=firestoreRoleName)
        await member_id.remove_roles(discordRoleName)
        logger.write_log(
            action='on_raw_reaction_remove',
            payload=f'User {member} removed emote {str(payload.emoji)}. Removing role #{firestoreRoleName}.',
            severity='Info'
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(OnReactionEvents(bot))