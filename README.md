# Comrade NEXT

[![Test Python package](https://github.com/itchono/comrade-next/actions/workflows/ci-pytest.yml/badge.svg)](https://github.com/itchono/comrade-next/actions/workflows/ci-pytest.yml)
[![codecov](https://codecov.io/gh/itchono/comrade-next/branch/main/graph/badge.svg?token=3DW5YRS91J)](https://codecov.io/gh/itchono/comrade-next)

![comrade-next-logo](https://user-images.githubusercontent.com/54449457/239707605-5ffae413-a8e7-4f3d-84b9-6100f053b61b.png)

The next rewrite of my personal Discord bot, using [`interactions.py`](https://github.com/interactions-py/interactions.py)

The goal of this bot is to become a long-term maintainable bot that I can use for the next several years. It will represent the culmination of nearly 4 years of work on my original version of Comrade which started in 2019.

Comrade NEXT represents the 7th major version of the bot, and will become integrated as Comrade 7.x after it is stable.

The current goal is to get feature parity with Comrade 5.x, Ground Dragon, and Comrade Requiem (6.x)

You can read more in the [docs wiki](https://github.com/itchono/comrade-next/wiki).

Suggest improvements by creating [an issue](https://github.com/itchono/comrade-next/issues), and follow the development process!

## New Practices Being Employed

* Built-in patcher - easily update the bot from the latest version of the repository
* Tests - unit tests for library functions, and integration tests for bot commands; testing is done in CI
* Installing the bot as a Python package - for managing dependencies, and for easy deployment

# Deployment Instructions

## Requirements

* Python 3.11+
* Discord Bot Token
* MongoDB cluster that you can connect to (either local or Atlas)
* Spare Discord server for asset storage

## Procedure

1. Clone the repo
2. `cd` to repo root
3. (Optional) [Create a virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment)
4. Run `pip install -e .` to install the bot as a package
5. Create a configuration file:
     * The easiest way is to make a file called `.env` in the repository root, with the following format:

    ```
    COMRADE_BOT_TOKEN = ...
    COMRADE_MONGODB_URI = ...
    COMRADE_TIMEZONE = ...
    COMRADE_RELAY_GUILD_ID = ...
    ```

    * You can also pass in values as environment variables with the same name.
    * Comrade uses [python-decouple](https://pypi.org/project/python-decouple/) for config loading. Check their docs to see other ways to specify configuration variables.

See `comrade/core/configuration.py` for details on the required values.

6. Run `comrade`
