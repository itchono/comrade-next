# A simple script to relaunch the bot on command.

import os
import subprocess
import sys

from comrade.lib.updater_utils import get_current_branch


def restart_process(notify_channel: int = None) -> None:
    """
    Restart the bot with all the same arguments it was launched with,
    except for the notify_channel argument.

    Parameters
    ----------
    notify_channel : int
        The channel ID to send a message to after restarting;
        if None, no message will be sent.
    """
    if notify_channel is not None:
        os.execl(
            sys.executable,
            sys.executable,
            "-m",
            "comrade",
            "--notify_channel",
            str(notify_channel),
        )

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
    current_branch = get_current_branch()
    if current_branch != branch:
        subprocess.run(["git", "checkout", branch], check=True)

    subprocess.run(["git", "pull"], check=True)
