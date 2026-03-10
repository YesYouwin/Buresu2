
print("Loading UserInfo command")

import discord
from discord import app_commands
from discord.ext import commands

class UserInfo(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="userinfo", description="Show user info")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member):
        embed = discord.Embed(title=str(user), color=discord.Color.blue())
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="User ID", value=user.id)
        embed.add_field(name="Joined", value=user.joined_at)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    print("Setting up UserInfo cog")
    await bot.add_cog(UserInfo(bot))
