print("Loading Logs Module")

import discord
from discord.ext import commands
import json
import math
import time
import os
from discord import app_commands
from commands.staff.utils import is_staff

LOG_FILE = "/home/wisp/logs.json"
LOGS_PER_PAGE = 25


def load_logs(errors_only=False):

    for _ in range(3):
        try:
            with open(LOG_FILE, "r") as f:
                data = json.load(f)

            clean_logs = []

            for line in data:

                if "|" not in line:
                    continue

                if errors_only:
                    if "ERROR" in line or "WARNING" in line:
                        clean_logs.append(line)
                else:
                    if "INFO" in line or "ERROR" in line or "WARNING" in line:
                        clean_logs.append(line)

            return clean_logs

        except:
            time.sleep(0.1)

    return []


class PageJumpModal(discord.ui.Modal, title="Jump to Page"):

    page = discord.ui.TextInput(
        label="Page Number",
        placeholder="Enter page number",
        required=True
    )

    def __init__(self, view):
        super().__init__()
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):

        try:
            page = int(self.page.value) - 1
        except:
            await interaction.response.send_message(
                "Invalid page number.",
                ephemeral=True
            )
            return

        total_pages = max(1, math.ceil(len(self.view.logs) / LOGS_PER_PAGE))

        if page < 0 or page >= total_pages:
            await interaction.response.send_message(
                f"Page must be between 1 and {total_pages}.",
                ephemeral=True
            )
            return

        self.view.page = page

        await interaction.response.edit_message(
            content=self.view.format_page(),
            view=self.view
        )


class LogsView(discord.ui.View):

    def __init__(self, logs, user, errors_only=False):
        super().__init__(timeout=120)

        self.logs = logs
        self.user = user
        self.page = 0
        self.errors_only = errors_only

    def format_page(self):
        MAX_DISCORD_MSG = 2000
        total_pages = max(1, math.ceil(len(self.logs) / LOGS_PER_PAGE))

        start = self.page * LOGS_PER_PAGE
        end = start + LOGS_PER_PAGE

        page_logs = self.logs[start:end]

        title = "⚠️ Errors & Warnings" if self.errors_only else "📜 Bot Logs"

        text = f"{title} (Page {self.page+1}/{total_pages})\n\n"

        for log in page_logs:
            if len(text) + len(log) + 10 > MAX_DISCORD_MSG:
                text += "...(truncated)\n"
                break
            text += f"{log}\n"

        return f"```ansi\n{text}\n```"

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.user.id

    # FIRST PAGE
    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.secondary)
    async def first(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.page = 0

        await interaction.response.edit_message(
            content=self.format_page(),
            view=self
        )

    # PREVIOUS
    @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):

        if self.page > 0:
            self.page -= 1

        await interaction.response.edit_message(
            content=self.format_page(),
            view=self
        )

    # PAGE JUMP
    @discord.ui.button(emoji="🔢", style=discord.ButtonStyle.primary)
    async def jump(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_modal(PageJumpModal(self))

    # NEXT
    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):

        if (self.page + 1) * LOGS_PER_PAGE < len(self.logs):
            self.page += 1

        await interaction.response.edit_message(
            content=self.format_page(),
            view=self
        )

    # LAST PAGE
    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary)
    async def last(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.page = max(0, math.ceil(len(self.logs) / LOGS_PER_PAGE) - 1)

        await interaction.response.edit_message(
            content=self.format_page(),
            view=self
        )

    # REFRESH
    @discord.ui.button(label="Refresh", emoji="🔄", style=discord.ButtonStyle.success)
    async def refresh(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.logs = load_logs(self.errors_only)[::-1][:200]
        self.page = 0

        await interaction.response.edit_message(
            content=self.format_page(),
            view=self
        )

    # TOGGLE ERRORS
    @discord.ui.button(label="Errors Only", emoji="⚠️", style=discord.ButtonStyle.danger)
    async def toggle_errors(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.errors_only = not self.errors_only

        self.logs = load_logs(self.errors_only)[::-1][:200]
        self.page = 0

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

        logs = load_logs()[-200:][::-1]

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

