# A simple script to relaunch the bot on command.

import os
import subprocess
import sys


def restart_process() -> None:
    """
    Restart the bot with all the same arguments it was launched with.
    """
    os.execv(sys.argv[0], sys.argv)


def update_packages() -> None:
    """
    Re-installs the bot package

    (i.e. pip install -e . --upgrade)
    """
    subprocess.run(["pip", "install", "-e", ".", "--upgrade"], check=True)


def pull_repo() -> None:
    """
    Pulls the latest changes from the git repo
    """
    subprocess.run(["git", "pull"], check=True)
