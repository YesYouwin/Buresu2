
print("Loading ScrimSchedule module")

import discord
from discord import app_commands
from discord.ext import commands
from commands.staff.utils import is_staff

class ScrimSchedule(commands.Cog):

    scrim = app_commands.Group(name="scrim", description="Scrim commands")

    def __init__(self, bot):
        self.bot = bot

    @scrim.command(name="schedule", description="Create scrim")
    @is_staff()
    async def schedule(self, interaction: discord.Interaction):
        await interaction.response.send_message("Scrim scheduled.")

async def setup(bot):
    print("Setting up ScrimSchedule cog")
    await bot.add_cog(ScrimSchedule(bot))
