from discord.ext import commands

# py files
import firestore # used to talk to firestore
import logger # used to write logs to google log explorer as well as to stdout


class ShowRoles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    '''
    !SHOW_ROLES:
    Show a user every single emote/role combination in firestore.
    If there are no associations in Firestore let the user know.
    Mainly used for debugging purposes.
    '''
    @commands.command()
    async def show_roles(self, ctx):
        try:
            role_list = firestore.show_roles(ctx.message.guild.id)
            # if roles exist
            if role_list:
                response = ''
                for dict in role_list:
                    #for i in dict:
                    response += f'\n {dict["roleEmote"]} | #{dict["roleName"]}'
                response = f'The following emote/roles are set for this server:{response}'
            else:
                response = 'There are currently no emote/roles set for this server. Add one using /add_role.'
            await ctx.send(f"Hello {ctx.message.author}, {response}")
        
        except Exception as e:
            logger.write_log(
                action='!show_roles',
                payload=str(e),
                severity='Error'
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(ShowRoles(bot))