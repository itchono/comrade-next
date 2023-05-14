from pathlib import Path
from os import getenv

import dotenv
import nextcord

from comrade.core.bot_subclass import Comrade
from comrade.core.self_restarter import restart_process

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
dotenv.load_dotenv(dotenv_path=env_path)


bot = Comrade()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")


@bot.slash_command(description="Replies with pong!")
async def ping(interaction: nextcord.Interaction):
    await interaction.send("Pong!", ephemeral=True)


@bot.slash_command(description="Restarts the bot.")
async def restart(interaction: nextcord.Interaction):
    await interaction.send("Restarting...", ephemeral=True)
    restart_process()


def main():
    bot.run(getenv("TOKEN"))


if __name__ == "__main__":
    main()
