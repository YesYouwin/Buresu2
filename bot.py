import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
from database.db import init_db

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


class MyBot(commands.Bot):

    async def setup_hook(self):

        print("Syncing slash commands...")

        guild = discord.Object(id=GUILD_ID)

        # sync commands to your test server instantly
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

        print("Slash commands synced")


bot = MyBot(command_prefix="!", intents=intents)

# -----------------------------
# EVENTS
# -----------------------------

@bot.event
async def on_ready():
    init_db()
    print(f"Logged in as {bot.user}")


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
