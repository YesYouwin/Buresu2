import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
from database.db import init_db
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

            except Exception:
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
# BOT SETUP
# -----------------------------

intents = discord.Intents.default()
intents.message_content = True
intents.members = True


class MyBot(commands.Bot):

    async def setup_hook(self):

        logging.info("Loading command modules...")

        extensions = [
            "commands.players.player_logs"
        ]

        for ext in extensions:

            try:
                await self.load_extension(ext)
                logging.info(f"Loaded extension: {ext}")

            except Exception:
                logging.exception(f"Failed to load extension: {ext}")

        logging.info("Syncing slash commands...")

        guild = discord.Object(id=GUILD_ID)

        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

        logging.info("Slash commands synced")


bot = MyBot(command_prefix="!", intents=intents)


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


# -----------------------------
# COMMAND LOGGING
# -----------------------------

@bot.event
async def on_command(ctx):

    logging.info(
        f"Prefix command used | {ctx.author} | !{ctx.command} | {ctx.guild}"
    )


@bot.event
async def on_app_command_completion(interaction, command):

    logging.info(
        f"Slash command used | {interaction.user} | /{command.name} | {interaction.guild}"
    )


# -----------------------------
# ERROR HANDLING
# -----------------------------

@bot.event
async def on_command_error(ctx, error):

    logging.error(f"Prefix command error: {error}")

    traceback_str = "".join(traceback.format_exception(type(error), error, error.__traceback__))

    logging.error(traceback_str)


@bot.tree.error
async def on_app_command_error(interaction, error):

    logging.error(f"Slash command error: {error}")

    traceback_str = "".join(traceback.format_exception(type(error), error, error.__traceback__))

    logging.error(traceback_str)

    try:
        await interaction.response.send_message(
            "❌ Command error occurred.", ephemeral=True
        )
    except:
        pass


# -----------------------------
# PREFIX COMMAND
# -----------------------------

@bot.command()
async def ping(ctx):

    await ctx.send("Pong!")


# -----------------------------
# SLASH COMMAND
# -----------------------------

@bot.tree.command(name="ping", description="Check if the bot is alive")
async def slash_ping(interaction: discord.Interaction):

    await interaction.response.send_message("Pong!")


# -----------------------------
# START BOT
# -----------------------------

keep_alive()
bot.run(TOKEN)
