print("Loading UserInfo command")

import discord
from discord import app_commands
from discord.ext import commands

class UserInfo(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="userinfo", description="Show detailed user info")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member):

        if user is None:
            user = interaction.user

        # Roles
        roles = [role.mention for role in user.roles if role.name != "@everyone"]
        role_count = len(roles)

        if len(roles) > 10:
            role_display = ", ".join(roles[:10])
        else:
            role_display = ", ".join(roles)

        if role_display == "":
            role_display = "None"

        # Boosting
        boosting = "Yes" if user.premium_since else "No"

        # Administrator permission
        if user.guild_permissions.administrator:
            permissions = "👑 Administrator (all permissions)"
        else:
            permissions = "Standard Member"

        # Time formatting
        joined_timestamp = int(user.joined_at.timestamp())
        created_timestamp = int(user.created_at.timestamp())

        joined_string = f"<t:{joined_timestamp}:f> (<t:{joined_timestamp}:R>)"
        created_string = f"<t:{created_timestamp}:f> (<t:{created_timestamp}:R>)"

        embed = discord.Embed(
            title="👥 USER INFORMATION 👥",
            color=discord.Color.blurple()
        )

        embed.set_thumbnail(url=user.display_avatar.url)

        embed.add_field(
            name="Username",
            value=f"`{user.name}`",
            inline=True
        )

        embed.add_field(
            name="User ID",
            value=f"`{user.id}`",
            inline=True
        )

        embed.add_field(
            name=f"Roles [{role_count}] (shows up to 10 roles)",
            value=role_display,
            inline=False
        )

        embed.add_field(
            name="Nickname",
            value=f"`{user.nick if user.nick else 'None'}`",
            inline=True
        )

        embed.add_field(
            name="Is boosting",
            value=f"`{boosting}`",
            inline=True
        )

        embed.add_field(
            name="Global permissions",
            value=permissions,
            inline=False
        )

        embed.add_field(
            name="Joined this server on",
            value=f"`{user.joined_at.strftime('%m/%d/%Y %H:%M')}`\n({joined_string})",
            inline=False
        )

        embed.add_field(
            name="Account created on",
            value=f"`{user.created_at.strftime('%m/%d/%Y %H:%M')}`\n({created_string})",
            inline=False
        )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    print("Setting up UserInfo cog")
    await bot.add_cog(UserInfo(bot))

