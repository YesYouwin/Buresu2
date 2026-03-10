````python
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
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL"))

# ------------------------------------------------
# DISCORD LOGGING HANDLER (MULTI-MESSAGE SUPPORT)
# ------------------------------------------------

class DiscordLogHandler(logging.Handler):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.max_length = 1900

    def emit(self, record):

        log_entry = self.format(record)

        async def send():
            try:
                channel = self.bot.get_channel(LOG_CHANNEL)

                if not channel:
                    return

                # Split logs into chunks so nothing is cut
                chunks = [
                    log_entry[i:i+self.max_length]
                    for i in range(0, len(log_entry), self.max_length)
                ]

                for chunk in chunks:
                    await channel.send(f"```{chunk}```")
                    await asyncio.sleep(0.3)

            except Exception:
                pass

        try:
            asyncio.create_task(send())
        except RuntimeError:
            pass


# ------------------------------------------------
# KEEP ALIVE SERVER (for uptime services)
# ------------------------------------------------

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
# LOGGING SETUP
# ------------------------------------------------

logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

# capture discord.py logs too
logging.getLogger("discord").setLevel(logging.INFO)
logging.getLogger("discord.http").setLevel(logging.INFO)


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

    discord_handler = DiscordLogHandler(bot)
    discord_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    )

    logging.getLogger().addHandler(discord_handler)

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

@bot.event
async def on_command(ctx):

    logging.info(
        f"Prefix command | user={ctx.author} | command=!{ctx.command} | guild={ctx.guild} | channel={ctx.channel}"
    )


@bot.event
async def on_app_command_completion(interaction, command):

    logging.info(
        f"Slash command | user={interaction.user} | command=/{command.name} | guild={interaction.guild} | channel={interaction.channel}"
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


loop = asyncio.get_event_loop()
loop.set_exception_handler(handle_exception)


# ------------------------------------------------
# START BOT
# ------------------------------------------------

keep_alive()
bot.run(TOKEN)
````
