
print("Loading Ping command")

import discord
from discord import app_commands
from discord.ext import commands

class Ping(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        print("Ping cog initialized")

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latency: **{latency}ms**",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    print("Setting up Ping cog")
    await bot.add_cog(Ping(bot))
