print("Loading Logs Module")

import discord
from discord import app_commands
from discord.ext import commands
import json
import math

from utils import is_staff

LOG_FILE = "logs.json"
LOGS_PER_PAGE = 10


def load_logs():
    try:
        with open(LOG_FILE) as f:
            return json.load(f)
    except:
        return []


class LogsView(discord.ui.View):

    def __init__(self, logs, user):
        super().__init__(timeout=120)
        self.logs = logs
        self.page = 0
        self.user = user

    def format_page(self):

        start = self.page * LOGS_PER_PAGE
        end = start + LOGS_PER_PAGE

        page_logs = self.logs[start:end]
        total_pages = math.ceil(len(self.logs) / LOGS_PER_PAGE)

        text = f"📜 **Bot Logs (Page {self.page+1}/{total_pages})**\n\n"

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
    @app_commands.check(is_staff())
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
