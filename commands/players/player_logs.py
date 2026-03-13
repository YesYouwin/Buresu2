print("Loading Playerlogs module...")
print("Loading Playerhistory module...")

import discord
from discord import app_commands
from discord.ext import commands
from commands.staff.utils import is_staff
from datetime import datetime
import asyncio
import traceback

from database.db import save_log, search_logs


class PlayerLogs(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="playerlogs", description="Create a formatted player log")
    @app_commands.check(is_staff())
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

        emoji = (
            "<:Plus:1438977678890766517>"
            if action.value in ["Recruitment", "Promotion"]
            else "<:Negative:1438979843252289656>"
        )

        color = (
            discord.Color.green()
            if action.value in ["Recruitment", "Promotion"]
            else discord.Color.red()
        )

        divider = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

        embed = discord.Embed(
            description=f"""
{divider}
**{emoji} {action.value}**

{discordname.mention}

**IGN -** [{ign}]({trackerid})

**{team1} ➜ {team2}**

**Date -** {formatted_date}

**Reason —** *{reason}*
{divider}
""",
            color=color,
        )

        embed.set_thumbnail(url=discordname.display_avatar.url)
        embed.set_footer(text=f"© Buresu • {datetime.now().year}")

        log_channel = self.bot.get_channel(1443545539445653604)


        if log_channel:
            await log_channel.send(embed=embed)


        try:
            await asyncio.wait_for(
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
                ),
                timeout=10
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

        search = search.strip()

        if search.startswith("<@") and search.endswith(">"):
            search = search.replace("<@", "").replace(">", "").replace("!", "")

        try:
            rows = await asyncio.wait_for(
                asyncio.to_thread(search_logs, search),
                timeout=10
            )        
        except Exception:
            error_msg = traceback.format_exc()

            print(error_msg)

            await interaction.followup.send(
                f"❌ Database Error:\n```{error_msg[:1900]}```",
                 ephemeral=True
            )
            return

        if not rows:
            await interaction.followup.send("❌ No logs found.", ephemeral=True)
            return

        divider = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

        await interaction.followup.send(
            f"📜 Found **{len(rows)}** log(s) for `{search}`", ephemeral=True
        )

        for action, discord_id, ign, team1, team2, date, trackerid, reason in rows:

            try:
                user = await self.bot.fetch_user(int(discord_id))
                mention = user.mention
                avatar = user.display_avatar.url
            except:
                mention = f"<@{discord_id}>"
                avatar = None

            emoji = (
                "<:Plus:1438977678890766517>"
                if action in ["Recruitment", "Promotion"]
                else "<:Negative:1438979843252289656>"
            )

            color = (
                discord.Color.green()
                if action in ["Recruitment", "Promotion"]
                else discord.Color.red()
            )

            try:
                parsed = datetime.strptime(date, "%d/%m/%Y")
                formatted_date = f"{date} [{parsed.strftime('%A')}]"
            except:
                formatted_date = date

            embed = discord.Embed(
                description=f"""
{divider}
**{emoji} {action}**

{mention}

**IGN -** [{ign}]({trackerid})

**{team1} ➜ {team2}**

**Date -** {formatted_date}

**Reason —** *{reason}*
{divider}
""",
                color=color,
            )

            if avatar:
                embed.set_thumbnail(url=avatar)

            embed.set_footer(text=f"© Buresu • {datetime.now().year}")

            await interaction.followup.send(embed=embed, ephemeral=True)
            await asyncio.sleep(0.2)




async def setup(bot):
    await bot.add_cog(PlayerLogs(bot))
