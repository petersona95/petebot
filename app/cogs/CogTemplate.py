import discord
from discord.ext import commands
from discord import app_commands

class Cog1(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="cog1",description="Cog1 description")
    async def cog1(self, interaction: discord.Interaction):
        await interaction.response.send_message("Cog1 message")

async def setup(bot: commands.Bot):
    await bot.add_cog(Cog1(bot))