"""
Context menu and command to set reminders.
"""

from interactions import Extension, slash_command


class Reminders(Extension):
    pass


def setup(bot):
    Reminders(bot)
