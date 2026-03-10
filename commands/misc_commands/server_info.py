
print("Loading ServerInfo command")

import discord
from discord import app_commands
from discord.ext import commands

class ServerInfo(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="serverinfo", description="Show server info")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(title=guild.name, color=discord.Color.blurple())
        embed.add_field(name="Members", value=guild.member_count)
        embed.add_field(name="Server ID", value=guild.id)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    print("Setting up ServerInfo cog")
    await bot.add_cog(ServerInfo(bot))
