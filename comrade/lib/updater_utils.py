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
    return (
        subprocess.run(
            ["git", "fetch"],
            capture_output=True,
            check=True,
        ).stdout.decode()
        + subprocess.run(
            ["git", "status"],
            capture_output=True,
            check=True,
        ).stdout.decode()
    )


def get_installed_pip_packages() -> str:
    """
    Returns the result of running pip list.
    """
    return subprocess.run(
        [sys.executable, "-m", "pip", "list"],
        capture_output=True,
        check=True,
    ).stdout.decode()
