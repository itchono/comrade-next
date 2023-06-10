import subprocess
import sys


def get_current_branch() -> str:
    """
    Returns the name of the current git branch.
    """
    return subprocess.check_output(
        ["git", "branch", "--show-current"], encoding="utf-8"
    ).strip()


def get_installed_pip_packages() -> str:
    """
    Returns the result of running pip list.
    """
    return subprocess.run(
        [sys.executable, "-m", "pip", "list"],
        capture_output=True,
        check=True,
    ).stdout.decode()
