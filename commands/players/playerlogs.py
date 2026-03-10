import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import asyncio
import traceback

from database.db import save_log, search_logs


class PlayerLogs(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="playerlogs", description="Create a formatted player log")
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Recruitment", value="Recruitment"),
            app_commands.Choice(name="Promotion", value="Promotion"),
            app_commands.Choice(name="Relegation", value="Relegation"),
            app_commands.Choice(name="Removed", value="Removed"),
        ]
    )
    async def playerlogs(
        self,
        interaction: discord.Interaction,
        action: app_commands.Choice[str],
        ign: str,
        discordname: discord.User,
        date: str,
        team1: str,
        team2: str,
        trackerid: str,
        reason: str,
    ):

        await interaction.response.defer(ephemeral=True)

        try:
            parsed = datetime.strptime(date, "%d/%m/%Y")
            formatted_date = f"{date} [{parsed.strftime('%A')}]"
        except ValueError:
            await interaction.followup.send(
                "❌ Invalid date format. Use **DD/MM/YYYY**", ephemeral=True
            )
            return


        embed = discord.Embed(
            title=f"{action.value}",
            description=f"""
{discordname.mention}

**IGN:** [{ign}]({trackerid})

**{team1} ➜ {team2}**

**Date:** {formatted_date}

**Reason:** {reason}
""",
            color=discord.Color.green(),
        )

        embed.set_thumbnail(url=discordname.display_avatar.url)

        log_channel = self.bot.get_channel(1443545539445653604)

        if log_channel:
            await log_channel.send(embed=embed)


        try:

            await asyncio.to_thread(
                save_log,
                action.value,
                str(discordname.id),
                ign,
                team1,
                team2,
                date,
                trackerid,
                reason
            )

        except Exception:

            error_msg = traceback.format_exc()

            print(error_msg)

            await interaction.followup.send(
                f"❌ Database Error:\n```{error_msg[:1900]}```",
                ephemeral=True
            )

            return


        await interaction.followup.send("✅ Player log created", ephemeral=True)



    @app_commands.command(name="playerhistory", description="Retrieve player history")
    async def playerhistory(self, interaction: discord.Interaction, search: str):

        await interaction.response.defer(ephemeral=True)

        rows = await asyncio.to_thread(search_logs, search)

        if not rows:
            await interaction.followup.send("❌ No logs found.", ephemeral=True)
            return


        for action, discord_id, ign, team1, team2, date, trackerid, reason in rows:

            embed = discord.Embed(
                title=action,
                description=f"""
<@{discord_id}>

**IGN:** [{ign}]({trackerid})

**{team1} ➜ {team2}**

**Date:** {date}

**Reason:** {reason}
""",
                color=discord.Color.blue(),
            )

            await interaction.followup.send(embed=embed, ephemeral=True)



async def setup(bot):
    await bot.add_cog(PlayerLogs(bot))
