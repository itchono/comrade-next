from interactions import Extension

from .interface_cmds import InterfaceCmds


class Reminders(InterfaceCmds, Extension):
    ...


def setup(bot):
    Reminders(bot)
