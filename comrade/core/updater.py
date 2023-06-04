# A simple script to relaunch the bot on command.

import os
import subprocess
import sys


def restart_process() -> None:
    """
    Restart the bot with all the same arguments it was launched with.
    """
    os.execv(sys.argv[0], sys.argv)


def update_packages() -> str:
    """
    Re-installs the bot package

    (i.e. pip install -e . --upgrade)

    (and returns the output of the command)
    """
    return subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", ".", "--upgrade"],
        capture_output=True,
        check=True,
    ).stdout.decode()


def pull_repo(branch: str = "main") -> None:
    """
    Pulls the latest changes from the git repo

    Parameters
    ----------
    branch : str
        The branch to pull from, defaults to "main"

    """
    current_branch = (
        subprocess.run(
            ["git", "branch", "--show-current"], capture_output=True, check=True
        )
        .stdout.decode()
        .strip()
    )
    if current_branch != branch:
        subprocess.run(["git", "checkout", branch], check=True)

    subprocess.run(["git", "pull"], check=True)