import discord
from discord.ext import commands
import os
from discord import app_commands
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
from database.db import init_db
import psutil
from discord.ext import tasks
import logging
import asyncio
import traceback

load_dotenv()

TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL"))

# -----------------------------
# DISCORD LOGGING HANDLER
# -----------------------------

class DiscordLogHandler(logging.Handler):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    def emit(self, record):

        log_entry = self.format(record)

        async def send():
            try:
                channel = self.bot.get_channel(LOG_CHANNEL)

                if channel:
                    await channel.send(f"```{log_entry[:1900]}```")

            except:
                pass

        try:
            asyncio.create_task(send())
        except RuntimeError:
            pass


# -----------------------------
# KEEP ALIVE SERVER
# -----------------------------

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!"

def run():
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()


# -----------------------------
# LOGGING SETUP
# -----------------------------

logger = logging.getLogger()
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
)

logger.addHandler(console_handler)


# -----------------------------
# BOT SETUP
# -----------------------------

intents = discord.Intents.default()
intents.members = True
intents.message_content = True


class MyBot(commands.Bot):

    async def setup_hook(self):

        logging.info("Loading command modules...")

        extensions = [

            "commands.misc_commands.ping",
            "commands.misc_commands.server_info",
            "commands.misc_commands.user_info",
            "commands.players.player_logs",
            "commands.scrims.scrim_schedule",

        ]

        for ext in extensions:

            try:
                await self.load_extension(ext)
                logging.info(f"Loaded extension: {ext}")

            except Exception:
                logging.exception(f"Failed to load extension: {ext}")

        guild = discord.Object(id=GUILD_ID)

        logging.info("Clearing old slash commands...")
        self.tree.clear_commands(guild=guild)

        logging.info("Syncing slash commands...")

        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

        logging.info("Commands synced to development server")


bot = MyBot(command_prefix="!", intents=intents)


# -----------------------------
# EVENTS
# -----------------------------

@bot.event
async def on_ready():

    init_db()

    discord_handler = DiscordLogHandler(bot)
    discord_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    )

    logging.getLogger().addHandler(discord_handler)

    logging.info(f"Logged in as {bot.user}")
    logging.info("Bot successfully started")

    @tasks.loop(seconds=30)
    async def update_status():

        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().used / 1024 / 1024
        ping = round(bot.latency * 1000)

        status = f"CPU {cpu}% | RAM {ram:.0f}MB | {ping}ms"

        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=status
            )
        )


# -----------------------------
# COMMAND LOGGING
# -----------------------------

@bot.event
async def on_command(ctx):

    logging.info(
        f"Prefix command | {ctx.author} | !{ctx.command} | {ctx.guild}"
    )


@bot.event
async def on_app_command_completion(interaction, command):

    logging.info(
        f"Slash command | {interaction.user} | /{command.name} | {interaction.guild}"
    )


# -----------------------------
# ERROR HANDLING
# -----------------------------

@bot.event
async def on_command_error(ctx, error):

    logging.error(f"Prefix command error: {error}")

    traceback_str = "".join(
        traceback.format_exception(type(error), error, error.__traceback__)
    )

    logging.error(traceback_str)


@bot.tree.error
async def on_app_command_error(interaction, error):

    logging.error(f"Slash command error: {error}")

    traceback_str = "".join(
        traceback.format_exception(type(error), error, error.__traceback__)
    )

    logging.error(traceback_str)

    try:
        await interaction.response.send_message(
            "❌ Command error occurred.", ephemeral=True
        )
    except:
        pass


# -----------------------------
# START BOT
# -----------------------------

keep_alive()
bot.run(TOKEN)
