import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
from database.db import init_db
import psutil
import logging
import asyncio
import traceback
import sys

load_dotenv()

TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

# ---------------------------------------------
# KEEP ALIVE SERVER
# ---------------------------------------------

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

# ------------------------------------------------
# LOGGING SETUP (console only → journalctl captures it)
# ------------------------------------------------

logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

# capture discord.py logs
logging.getLogger("discord").setLevel(logging.INFO)
logging.getLogger("discord.http").setLevel(logging.INFO)

# Redirect print() to logging
class PrintLogger:
    def write(self, message):
        message = message.strip()
        if message:
            logging.info(message)

    def flush(self):
        pass

sys.stdout = PrintLogger()
sys.stderr = PrintLogger()

# ------------------------------------------------
# BOT SETUP
# ------------------------------------------------

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
            "commands.misc_commands.logs",
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

# ------------------------------------------------
# BOT STATUS LOOP
# ------------------------------------------------

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

# ------------------------------------------------
# EVENTS
# ------------------------------------------------

@bot.event
async def on_ready():

    init_db()
    update_status.start()

    logging.info(f"Logged in as {bot.user}")
    logging.info("Bot successfully started")


@bot.event
async def on_disconnect():
    logging.warning("Bot disconnected from Discord gateway")


@bot.event
async def on_resumed():
    logging.info("Bot resumed session successfully")


@bot.event
async def on_connect():
    logging.info("Bot connected to Discord")


# ------------------------------------------------
# COMMAND LOGGING
# ------------------------------------------------

command_start_times = {}


def format_slash_command(interaction):

    args = []

    if interaction.namespace:
        for key, value in vars(interaction.namespace).items():
            args.append(str(value))

    arg_string = " ".join(args)

    if arg_string:
        return f"/{interaction.command.name} {arg_string}"
    else:
        return f"/{interaction.command.name}"


@bot.event
async def on_app_command(interaction):

    command_start_times[interaction.id] = asyncio.get_event_loop().time()


@bot.event
async def on_app_command_completion(interaction, command):

    start = command_start_times.pop(interaction.id, None)

    duration = 0
    if start:
        duration = round(asyncio.get_event_loop().time() - start, 3)

    command_string = format_slash_command(interaction)

    logging.info(
        f"Slash command | user={interaction.user} "
        f"| command={command_string} "
        f"| channel={interaction.channel} "
        f"| took={duration}s"
    )


@bot.event
async def on_command(ctx):

    logging.info(
        f"Prefix command | user={ctx.author} "
        f"| command=!{ctx.command} "
        f"| channel={ctx.channel}"
    )

# ------------------------------------------------
# ERROR HANDLING
# ------------------------------------------------

@bot.event
async def on_command_error(ctx, error):

    traceback_str = "".join(
        traceback.format_exception(type(error), error, error.__traceback__)
    )

    logging.error(
        f"Prefix command error | user={ctx.author} | command=!{ctx.command}\n{traceback_str}"
    )


@bot.tree.error
async def on_app_command_error(interaction, error):

    if isinstance(error, app_commands.CheckFailure):
        try:
            await interaction.response.send_message(
                "❌ You do not have permission to use this command.",
                ephemeral=True
            )
        except:
            pass
        return

    traceback_str = "".join(
        traceback.format_exception(type(error), error, error.__traceback__)
    )

    logging.error(
        f"Slash command error | user={interaction.user} | command={interaction.command}\n{traceback_str}"
    )

    try:
        await interaction.response.send_message(
            "❌ Command error occurred.", ephemeral=True
        )
    except:
        pass

    traceback_str = "".join(
        traceback.format_exception(type(error), error, error.__traceback__)
    )

    logging.error(
        f"Slash command error | user={interaction.user} | command={interaction.command}\n{traceback_str}"
    )

    try:
        await interaction.response.send_message(
            "❌ Command error occurred.", ephemeral=True
        )
    except Exception:
        pass

# ------------------------------------------------
# GLOBAL ERROR HANDLING
# ------------------------------------------------

def handle_exception(loop, context):

    msg = context.get("exception", context["message"])
    logging.error(f"Global async exception: {msg}")


asyncio.get_event_loop().set_exception_handler(handle_exception)


def excepthook(exc_type, exc_value, exc_traceback):
    logging.error(
        "Uncaught exception",
        exc_info=(exc_type, exc_value, exc_traceback)
    )


sys.excepthook = excepthook

# ------------------------------------------------
# START BOT
# ------------------------------------------------

keep_alive()
bot.run(TOKEN)
