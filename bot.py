import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

# -----------------------------
# LOAD ENV VARIABLES
# -----------------------------

load_dotenv()

TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

# -----------------------------
# KEEP ALIVE SERVER (OPTIONAL)
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
intents.members = True
intents.message_content = True


class MyBot(commands.Bot):

    async def setup_hook(self):

        print("Loading command modules...")

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
                print(f"Loaded {ext}")
            except Exception as e:
                print(f"Failed to load {ext}: {e}")

        guild = discord.Object(id=GUILD_ID)

        print("Clearing old commands...")
        self.tree.clear_commands(guild=guild)

        print("Syncing commands...")
        await self.tree.sync(guild=guild)

        print("Commands synced to development server.")


bot = MyBot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


# Optional keep alive (safe to keep)
keep_alive()

bot.run(TOKEN)
