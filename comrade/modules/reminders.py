'''
Context menu and command to set reminders.
'''

from nextcord.ext import commands


class Reminders(commands.Cog):


def setup(bot):
    bot.add_cog(Reminders(bot))
