print("Loading ServerInfo command")

import discord
from discord import app_commands
from discord.ext import commands

class ServerInfo(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="serverinfo", description="Show detailed server info")
    async def serverinfo(self, interaction: discord.Interaction):

        guild = interaction.guild

        # -------------------------
        # MEMBER STATS
        # -------------------------

        members = len([m for m in guild.members if not m.bot])
        bots = len([m for m in guild.members if m.bot])

        # -------------------------
        # CHANNEL STATS
        # -------------------------

        categories = len(guild.categories)
        text = len(guild.text_channels)
        voice = len(guild.voice_channels)
        stage = len(guild.stage_channels)
        announcement = len([c for c in guild.text_channels if c.is_news()])

        # -------------------------
        # EMOJIS / STICKERS
        # -------------------------

        normal_emojis = len([e for e in guild.emojis if not e.animated])
        animated_emojis = len([e for e in guild.emojis if e.animated])
        stickers = len(guild.stickers)

        # -------------------------
        # ROLES
        # -------------------------

        roles = [role.name for role in guild.roles if role.name != "@everyone"]
        role_count = len(roles)

        role_display = ", ".join(roles[:15])
        if role_display == "":
            role_display = "None"

        # -------------------------
        # BOOST INFO
        # -------------------------

        boosts = guild.premium_subscription_count
        boost_level = guild.premium_tier

        # Boost progress (next tier info)
        boost_goal = {0: 2, 1: 7, 2: 14}.get(boost_level, "Max")
        if boost_goal != "Max":
            boost_progress = f"{boosts}/{boost_goal}"
        else:
            boost_progress = "Max Level"

        # -------------------------
        # VERIFICATION LEVEL
        # -------------------------

        verification_levels = {
            discord.VerificationLevel.none: "None",
            discord.VerificationLevel.low: "Low",
            discord.VerificationLevel.medium: "Medium",
            discord.VerificationLevel.high: "High",
            discord.VerificationLevel.highest: "Very High"
        }

        verification = verification_levels.get(guild.verification_level, "Unknown")

        # -------------------------
        # TIMESTAMPS
        # -------------------------

        created_timestamp = int(guild.created_at.timestamp())

        created_string = f"<t:{created_timestamp}:f> (<t:{created_timestamp}:R>)"

        # -------------------------
        # EMBED
        # -------------------------

        embed = discord.Embed(
            title="🖥️ SERVER INFORMATION 🖥️",
            color=discord.Color.blurple()
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        if guild.banner:
            embed.set_image(url=guild.banner.url)

        # -------------------------
        # BASIC INFO
        # -------------------------

        embed.add_field(
            name="Server name",
            value=f"```{guild.name}```",
            inline=True
        )

        embed.add_field(
            name="Server owner ID",
            value=f"```{guild.owner_id}```",
            inline=True
        )

        embed.add_field(
            name=f"Server members [{guild.member_count}]",
            value=f"```Members: {members} | Bots: {bots}```",
            inline=False
        )

        # -------------------------
        # IDs / BOOSTS
        # -------------------------

        embed.add_field(
            name="Server ID",
            value=f"```{guild.id}```",
            inline=True
        )

        embed.add_field(
            name="Server boosts",
            value=f"```{boosts} (level {boost_level}) | Progress {boost_progress}```",
            inline=True
        )

        # -------------------------
        # CHANNELS
        # -------------------------

        embed.add_field(
            name=f"Server categories and channels [{categories + text + voice + stage}]",
            value=f"```Categories: {categories} | Text: {text} | Voice: {voice} | Announcement: {announcement} | Stage: {stage}```",
            inline=False
        )

        # -------------------------
        # EMOJIS
        # -------------------------

        embed.add_field(
            name=f"Server emojis and stickers [{normal_emojis + animated_emojis + stickers}]",
            value=f"```Normal: {normal_emojis} | Animated: {animated_emojis} | Stickers: {stickers}```",
            inline=False
        )

        # -------------------------
        # ROLES
        # -------------------------

        embed.add_field(
            name=f"Server roles [{role_count}] ",
            value=f"```{role_display}```",
            inline=False
        )

        # -------------------------
        # EXTRA SERVER INFO
        # -------------------------

        embed.add_field(
            name="Verification level",
            value=f"```{verification}```",
            inline=True
        )

        embed.add_field(
            name="NSFW level",
            value=f"```{guild.nsfw_level.name}```",
            inline=True
        )

        # -------------------------
        # CREATED DATE
        # -------------------------

        embed.add_field(
            name="Server created on ",
            value=f"```{guild.created_at.strftime('%m/%d/%Y %H:%M')}```\n{created_string}",
            inline=False
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    print("Setting up ServerInfo cog")
    await bot.add_cog(ServerInfo(bot))
