# A simple script to relaunch the bot on command.

import os
import subprocess
import sys


def get_current_branch() -> str:
    """
    Returns the name of the current git branch.
    """
    return subprocess.check_output(
        ["git", "branch", "--show-current"], encoding="utf-8"
    ).strip()


def get_current_commit_hash() -> str:
    """
    Returns the hash of the current git commit.
    """
    return subprocess.check_output(
        ["git", "rev-parse", "--short", "HEAD"], encoding="utf-8"
    ).strip()


def check_updates_on_branch() -> str:
    """
    Returns the result of running git fetch and git status.
    """

    return subprocess.check_output(
        ["git", "fetch"], encoding="utf-8"
    ) + subprocess.check_output(["git", "status"], encoding="utf-8")


def restart_process(notify_channel: int | None = None) -> None:
    """
    Restart the bot with all the same arguments it was launched with,
    except for the notify_channel argument.

    Ensure that the bot's http connection is closed before calling this,
    otherwise you will run into HTTP 400 errors.

    Parameters
    ----------
    notify_channel : int | None
        The channel ID to send a message to after restarting;
        if None, no message will be sent.
    """
    if notify_channel is not None:
        os.execv(
            sys.argv[0], sys.argv + ["--notify_channel", str(notify_channel)]
        )

    os.execv(sys.argv[0], sys.argv)


def update_packages() -> str:
    """
    Re-installs the bot package

    (i.e. pip install -e . --upgrade)

    (and returns the output of the command)
    """
    return subprocess.check_output(
        [sys.executable, "-m", "pip", "install", "-e", ".", "--upgrade"],
        encoding="utf-8",
    )


def pull_repo(branch: str = "main") -> str:
    """
    Pulls the latest changes from the git repo

    Parameters
    ----------
    branch : str
        The branch to pull from, defaults to "main"

    """
    current_branch = get_current_branch()
    ret = ""
    if current_branch != branch:
        ret += subprocess.check_output(
            ["git", "checkout", branch], encoding="utf-8"
        )

    return ret + subprocess.check_output(["git", "pull"], encoding="utf-8")
