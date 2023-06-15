"""
Context menu and command to set reminders.
"""
from arrow import Arrow
from interactions import (
    CommandType,
    ContextMenuContext,
    DateTrigger,
    Extension,
    InteractionContext,
    Message,
    Modal,
    ModalContext,
    ShortText,
    Task,
    Timestamp,
    context_menu,
)


class Reminders(Extension):
    async def create_reminder(
        self,
        ctx: InteractionContext,
        message: Message,
        relative_time: str,
        reminder_note: str,
    ):
        """
        Schedule a reminder to fire off in a channel at a given time.

        Parameters
        ----------
        ctx : InteractionContext
            The context of the command invocation.
        message : Message
            The message to remind the user about.
        relative_time : str
            The relative time to send the reminder at,
            e.g. "in 5 seconds" or "in 2 hours".
        reminder_note : str
            The note to send with the reminder.

        Notes
        -----
        Sends an error if the time cannot be parsed,
        or if the time is in the past.
        """
        try:
            time_from_now = Arrow.dehumanize(Arrow.now(), relative_time)
        except ValueError as e:
            await ctx.send(f"Invalid input: {e}", ephemeral=True)
            return

        if time_from_now < Arrow.now():
            past_timestamp = Timestamp.fromdatetime(time_from_now.naive)

            await ctx.send(
                "Reminder must be in the future. Your reminder "
                f"would have occurred at {past_timestamp.format('F')}.",
                ephemeral=True,
            )
            return

        @Task.create(trigger=DateTrigger(time_from_now.naive))
        async def send_reminder():
            await message.channel.send(
                f"Reminder: {message.jump_url}\n\n{reminder_note}"
            )

        send_reminder.start()

        future_timestamp = Timestamp.fromdatetime(time_from_now.naive)

        await ctx.send(
            f"Reminder registered to send {future_timestamp.format('R')}"
            f" ({future_timestamp.format('F')}).",
        )

    @context_menu(name="Create Reminder", context_type=CommandType.MESSAGE)
    async def reminder_ctx_menu(self, menu_ctx: ContextMenuContext):
        channel = await self.bot.fetch_channel(menu_ctx.channel_id)
        message = await channel.fetch_message(menu_ctx.target_id)

        modal = Modal(
            ShortText(
                label="Relative Time",
                placeholder="e.g. in 5 seconds",
                required=True,
                custom_id="relative_time",
            ),
            ShortText(
                label="Reminder Note",
                placeholder="(Optional) e.g. Submit paper",
                required=False,
                custom_id="reminder_note",
            ),
            title="Create Reminder",
        )

        await menu_ctx.send_modal(modal)

        modal_ctx: ModalContext = await menu_ctx.bot.wait_for_modal(modal)

        relative_time = modal_ctx.responses.get("relative_time")
        reminder_note = modal_ctx.responses.get("reminder_note")

        await self.create_reminder(
            modal_ctx, message, relative_time, reminder_note
        )

    # TODO: figure out slash commands


def setup(bot):
    Reminders(bot)
