from os import getenv
from pathlib import Path

import dotenv

from comrade.core.bot_subclass import Comrade
from comrade.core.init_logging import init_logging

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
dotenv.load_dotenv(dotenv_path=env_path)


bot = Comrade()


def main():
    init_logging()
    bot.start(getenv("TOKEN"))


if __name__ == "__main__":
    main()
