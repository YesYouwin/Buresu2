
print("Loading PlayerLogs module")

import discord
from discord import app_commands
from discord.ext import commands
from commands.staff.utils import is_staff

class PlayerLogs(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="playerlogs", description="Create player log")
    @is_staff()
    async def playerlogs(self, interaction: discord.Interaction):
        await interaction.response.send_message("Player log command works.")

async def setup(bot):
    print("Setting up PlayerLogs cog")
    await bot.add_cog(PlayerLogs(bot))
