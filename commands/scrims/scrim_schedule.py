print("Loading ScrimSchedule module...")

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import asyncio
from commands.staff.utils import is_staff


VALORANT_MAPS = [
    app_commands.Choice(name="Abyss", value="Abyss"),
    app_commands.Choice(name="Ascent", value="Ascent"),
    app_commands.Choice(name="Bind", value="Bind"),
    app_commands.Choice(name="Breeze", value="Breeze"),
    app_commands.Choice(name="Fracture", value="Fracture"),
    app_commands.Choice(name="Haven", value="Haven"),
    app_commands.Choice(name="Icebox", value="Icebox"),
    app_commands.Choice(name="Lotus", value="Lotus"),
    app_commands.Choice(name="Pearl", value="Pearl"),
    app_commands.Choice(name="Split", value="Split"),
    app_commands.Choice(name="Sunset", value="Sunset"),
]


class ScrimSchedule(commands.Cog):

    scrim = app_commands.Group(name="scrim", description="Scrim management commands")

    def __init__(self, bot):
        self.bot = bot


    @scrim.command(name="schedule", description="Create a scrim schedule")
    @is_staff()
    @app_commands.describe(
        scrim_type="Type of scrim",
        team_a="First team role",
        team_b="Second team role",
        date="Match date (DD/MM/YYYY)",
        time="Match time (HH:MM 24h)",
        format="Match format",
        map1="Map 1",
        map2="Map 2 (BO3/BO5)",
        map3="Map 3 (BO3/BO5)",
        map4="Map 4 (BO5)",
        map5="Map 5 (BO5)"
    )
    @app_commands.choices(
        scrim_type=[
            app_commands.Choice(name="Scrim", value="SCRIM"),
            app_commands.Choice(name="In-Houses", value="IN-HOUSES"),
            app_commands.Choice(name="Tournament", value="TOURNAMENT")
        ],
        format=[
            app_commands.Choice(name="BO1", value="BO1"),
            app_commands.Choice(name="BO3", value="BO3"),
            app_commands.Choice(name="BO5", value="BO5"),
        ],
        map1=VALORANT_MAPS,
        map2=VALORANT_MAPS,
        map3=VALORANT_MAPS,
        map4=VALORANT_MAPS,
        map5=VALORANT_MAPS
    )
    async def schedule(
        self,
        interaction: discord.Interaction,
        scrim_type: app_commands.Choice[str],
        team_a: discord.Role,
        team_b: discord.Role,
        date: str,
        time: str,
        format: app_commands.Choice[str],
        map1: app_commands.Choice[str],
        map2: app_commands.Choice[str] | None = None,
        map3: app_commands.Choice[str] | None = None,
        map4: app_commands.Choice[str] | None = None,
        map5: app_commands.Choice[str] | None = None,
    ):

        try:
            dt = datetime.strptime(f"{date} {time}", "%d/%m/%Y %H:%M")
            timestamp = int(dt.timestamp())
        except ValueError:
            await interaction.response.send_message(
                "❌ Use **DD/MM/YYYY** for date and **HH:MM (24h)** for time.",
                ephemeral=True
            )
            return

        time_display = f"<t:{timestamp}:F>"
        countdown = f"<t:{timestamp}:R>"

        maps = [map1.value]

        if format.value in ["BO3", "BO5"]:
            if map2:
                maps.append(map2.value)
            if map3:
                maps.append(map3.value)

        if format.value == "BO5":
            if map4:
                maps.append(map4.value)
            if map5:
                maps.append(map5.value)

        map_display = "\n".join(
            f"     **Map {i+1}:** {m}" for i, m in enumerate(maps)
        )

        await interaction.response.send_message(
            f"{team_a.mention} {team_b.mention}",
            allowed_mentions=discord.AllowedMentions(roles=True)
        )

        schedule_message = (
            f"# 🗓 **{scrim_type.value} SCHEDULE**\n\n"
            f"> **Teams:** {team_a.mention} vs {team_b.mention}\n"
            f"> **Time:** {time_display}\n"
            f"> **Starts:** {countdown}\n"
            f"> **Format:** {format.value}\n"
            f"> {map_display}\n\n"
            f"⚠️ **Note**\n"
            f"- Inform staff beforehand if you cannot attend.\n"
        )

        message = await interaction.followup.send(schedule_message)

        asyncio.create_task(
            self.scrim_reminder(message.channel, team_a, team_b, timestamp)
        )


    async def scrim_reminder(self, channel, team_a, team_b, timestamp):

        now = int(datetime.utcnow().timestamp())
        wait_30 = timestamp - now - 1800

        if wait_30 > 0:
            await asyncio.sleep(wait_30)

            await channel.send(
                f"⏰ **Scrim Reminder (30 minutes)**\n"
                f"{team_a.mention} vs {team_b.mention}"
            )

        now = int(datetime.utcnow().timestamp())
        wait_10 = timestamp - now - 600

        if wait_10 > 0:
            await asyncio.sleep(wait_10)

            await channel.send(
                f"⚠️ **Scrim starts in 10 minutes!**\n"
                f"{team_a.mention} vs {team_b.mention}"
            )


async def setup(bot):
    print("Setting up ScrimSchedule cog")
    await bot.add_cog(ScrimSchedule(bot))
