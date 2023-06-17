"""
Context menu and command to set reminders.
"""
from interactions import (
    CommandType,
    ContextMenuContext,
    DateTrigger,
    Extension,
    InteractionContext,
    Modal,
    ModalContext,
    ShortText,
    Task,
    context_menu,
)

from comrade.lib.discord_utils import messageable_from_context_id
from comrade.lib.reminders import Reminder


class Reminders(Extension):
    async def task_from_reminder(self, reminder: Reminder) -> Task:
        """
        Generates a task from a reminder,
        which can then be set for execution.

        Parameters
        ----------
        reminder : Reminder
            The reminder to generate a task from.

        Returns
        -------
        Task
            The task generated from the reminder.
            Use Task.start() to start the task.
        """
        # Infer the channel in which to send the reminder
        # from the context ID of the reminder

        @Task.create(trigger=DateTrigger(reminder.time_utc))
        async def send_reminder():
            sendable = await messageable_from_context_id(
                reminder.context_id, self.bot
            )

            message_to_send = (
                f"Reminder for <@{reminder.author_id}>: {reminder.note}"
            )

            if reminder.jump_url:
                message_to_send += f"\n\nJump to message: {reminder.jump_url}"

            await sendable.send(message_to_send)

        return send_reminder

    async def create_reminder(
        self,
        ctx: InteractionContext,
        relative_time: str,
        reminder_note: str,
    ) -> Reminder:
        """
        Schedule a reminder to fire off in a channel at a given time,
        and returns the reminder.

        Parameters
        ----------
        ctx : InteractionContext
            The context of the command invocation.
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
            reminder = await Reminder.from_relative_time_and_ctx(
                relative_time, ctx, reminder_note
            )
        except ValueError as e:
            await ctx.send(f"Invalid input: {e}", ephemeral=True)
            return

        send_reminder = await self.task_from_reminder(reminder)
        send_reminder.start()

        return reminder

    @context_menu(name="Create Reminder", context_type=CommandType.MESSAGE)
    async def reminder_ctx_menu(self, menu_ctx: ContextMenuContext):
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

        reminder = await self.create_reminder(
            menu_ctx,
            modal_ctx.responses["relative_time"],
            modal_ctx.responses["reminder_note"],
        )

        future_timestamp = reminder.timestamp

        await modal_ctx.send(
            f"Reminder registered to send {future_timestamp.format('R')}"
            f" ({future_timestamp.format('F')}).",
        )

    # TODO: figure out slash commands


def setup(bot):
    Reminders(bot)
