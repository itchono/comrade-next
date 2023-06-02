from os import getenv
from pathlib import Path

import dotenv
from interactions.client.const import CLIENT_FEATURE_FLAGS

from comrade.core.bot_subclass import Comrade
from comrade.core.init_logging import init_logging

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
dotenv.load_dotenv(dotenv_path=env_path)


def main():
    init_logging("comrade")

    bot = Comrade(timezone=getenv("TIMEZONE"))

    # Temp workaround for discord API image upload bug
    CLIENT_FEATURE_FLAGS["FOLLOWUP_INTERACTIONS_FOR_IMAGES"] = True

    # Load all extensions in the comrade/modules directory
    for module in (Path(__file__).parent / "modules").glob("*.py"):
        if module.stem == "__init__":
            continue
        bot.load_extension(f"comrade.modules.{module.stem}")

    bot.load_extension("interactions.ext.jurigged")

    bot.start(getenv("TOKEN"))


if __name__ == "__main__":
    main()
