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
        print("Starting bot setup...")

        guild = discord.Object(id=GUILD_ID)

        print("Syncing commands...")
        await self.tree.sync(guild=guild)

        print("Commands synced to development server.")
        print("New version running")

bot = MyBot(command_prefix="!", intents=intents)

# -----------------------------
# EVENTS
# -----------------------------

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# -----------------------------
# TEST SLASH COMMAND
# -----------------------------

@bot.tree.command(name="ping", description="Check if the bot is alive")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")



keep_alive()
bot.run(TOKEN)
