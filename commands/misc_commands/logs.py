print("Loading Logs Module")

import discord
from discord.ext import commands
import json
import math
import time
import os
from discord import app_commands
from commands.staff.utils import is_staff

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_FILE = os.path.join(BASE_DIR, "logs.json")
LOGS_PER_PAGE = 10


def load_logs():

    for _ in range(3):
        try:
            with open(LOG_FILE, "r") as f:
                return json.load(f)
        except:
            time.sleep(0.1)

    return []


class LogsView(discord.ui.View):

    def __init__(self, logs, user):
        super().__init__(timeout=120)
        self.logs = logs
        self.page = 0
        self.user = user

    def format_page(self):

        total_pages = max(1, math.ceil(len(self.logs) / LOGS_PER_PAGE))

        start = self.page * LOGS_PER_PAGE
        end = start + LOGS_PER_PAGE

        page_logs = self.logs[start:end]

        text = f"📜 Bot Logs (Page {self.page+1}/{total_pages})\n\n"

        for log in page_logs:
            text += f"{log}\n"

        return f"```ansi\n{text}\n```"

    async def interaction_check(self, interaction: discord.Interaction):
        # Only the command user can use buttons
        return interaction.user.id == self.user.id

    @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):

        if self.page > 0:
            self.page -= 1

        await interaction.response.edit_message(
            content=self.format_page(),
            view=self
        )

    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):

        if (self.page + 1) * LOGS_PER_PAGE < len(self.logs):
            self.page += 1

        await interaction.response.edit_message(
            content=self.format_page(),
            view=self
        )


class Logs(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="logs", description="View bot logs")
    @is_staff()
    async def logs(self, interaction: discord.Interaction):

        logs = load_logs()

        if not logs:
            await interaction.response.send_message(
                "No logs found.",
                ephemeral=True
            )
            return

        view = LogsView(logs, interaction.user)

        await interaction.response.send_message(
            content=view.format_page(),
            view=view,
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Logs(bot))