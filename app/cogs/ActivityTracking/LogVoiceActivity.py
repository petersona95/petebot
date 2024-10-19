import discord
from discord.ext import commands
from datetime import datetime

# py files
import firestore_utils as firestore # used to talk to firestore
import logger # used to write logs to google log explorer as well as to stdout


class LogVoiceActivity(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        payload = {
            'memberID': member.id,
            'timestampUTC': datetime.utcnow(),
            'beforeChannel': before.channel.id if before.channel else None,
            'afterChannel': after.channel.id if after.channel else None,
            'afterAFK': after.afk,
            'afterDeaf': after.deaf,
            'afterMute': after.mute,
            'afterRequestedToSpeakAt': after.requested_to_speak_at,
            'afterSelfDeaf': after.self_deaf,
            'afterSelfMute': after.self_mute,
            'afterSelfStream': after.self_stream,
            'afterSelfVideo': after.self_video,
            'afterSuppress': after.suppress
        }
        logger.write_log(
            action='on_voice_state_update',
            payload=f'User {member.name} changed voice status.',
            severity='Info'
        )

        # coalesce(before, after)
        # guild = before.channel.guild if before.channel else after.channel.guild
        firestore.log_activity(member.guild.id, payload)


async def setup(bot: commands.Bot):
    await bot.add_cog(LogVoiceActivity(bot))