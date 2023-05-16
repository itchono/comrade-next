# A simple script to relaunch the bot on command.

import os
import sys


def restart_process() -> None:
    """
    Restart the bot with all the same arguments it was launched with.
    """
    os.execv(sys.argv[0], sys.argv)
