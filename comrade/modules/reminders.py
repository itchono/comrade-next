"""
Context menu and command to set reminders.
"""

import asyncio

from arrow import Arrow
from interactions import (
    CommandType,
    ContextMenuContext,
    DateTrigger,
    Extension,
    Task,
    context_menu,
)


class Reminders(Extension):
    @context_menu(name="Create Reminder", command_type=CommandType.MESSAGE)
    async def create_reminder(self, ctx: ContextMenuContext):
        # make a time 10 seconds from now
        ten_sec_from_now = Arrow.now().shift(seconds=10)

        @Task.create(trigger=DateTrigger(ten_sec_from_now.datetime))
        async def send_reminder():
            await ctx.channel.send("Reminder triggered!")

        await send_reminder.start()

        await ctx.send("Reminder created!", ephemeral=True)


def setup(bot):
    Reminders(bot)
