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

bot = commands.Bot(command_prefix="!", intents=intents)

# -----------------------------
# EVENTS
# -----------------------------

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("New version running")

# -----------------------------
# PREFIX COMMAND
# -----------------------------

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# -----------------------------
# START BOT
# -----------------------------

keep_alive()
bot.run(TOKEN)
