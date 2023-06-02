"""
Context menu and command to set reminders.
"""

import asyncio

from interactions import ContextMenuContext, Extension, context_menu


class Reminders(Extension):
    async def create_reminder(self, ctx: ContextMenuContext):
        await ctx.send("Reminder created!", ephemeral=True)
        await asyncio.sleep(5)
        await ctx.send("Reminder triggered!", ephemeral=True)


def setup(bot):
    Reminders(bot)
