from pathlib import Path
from os import getenv

import dotenv
import nextcord
from nextcord.ext import commands

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
dotenv.load_dotenv(dotenv_path=env_path)


bot = commands.Bot()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")

@bot.slash_command(description="Replies with pong!")
async def ping(interaction: nextcord.Interaction):
    await interaction.send("Pong!", ephemeral=True)

bot.run(getenv("TOKEN"))
