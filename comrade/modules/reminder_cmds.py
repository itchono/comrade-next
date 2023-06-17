"""
Context menu and command to set reminders.
"""
from interactions import (
    CommandType,
    ContextMenuContext,
    DateTrigger,
    Embed,
    Extension,
    InteractionContext,
    Modal,
    ModalContext,
    OptionType,
    ShortText,
    SlashContext,
    Task,
    context_menu,
    listen,
    slash_command,
    slash_option,
)
from interactions.ext.prefixed_commands import PrefixedContext, prefixed_command

from comrade.core.bot_subclass import Comrade
from comrade.core.configuration import ACCENT_COLOUR
from comrade.lib.discord_utils import messageable_from_context_id
from comrade.lib.reminders import Reminder


class Reminders(Extension):
    bot: Comrade

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

        @Task.create(trigger=DateTrigger(reminder.scheduled_time))
        async def send_reminder():
            sendable = await messageable_from_context_id(
                reminder.context_id, self.bot
            )

            if not sendable:
                self.bot.logger.error(
                    f"Failed to send reminder {reminder._id}: "
                    f"could not find channel with ID {reminder.context_id}."
                )
                return

            if reminder.guild_id:
                author = await self.bot.fetch_member(
                    reminder.author_id, reminder.guild_id
                )
            else:
                author = await self.bot.fetch_user(reminder.author_id)

            embed = Embed(
                color=ACCENT_COLOUR,
                description=reminder.note,
                timestamp=reminder.created_at,
            )
            embed.set_author(
                name=f"Reminder for {author.nick}",
                url=reminder.jump_url,
                icon_url=author.avatar.url,
            )
            embed.set_footer(text="Reminder originally set")

            content = author.mention

            if reminder.jump_url:
                content += f"\nJump to message: {reminder.jump_url}"

            await sendable.send(
                content=content, embed=embed, reply_to=reminder.reply_id
            )

            self.bot.logger.info(f"Sent reminder {reminder._id}.")

            deletion_result = self.bot.db.remindersV7.delete_one(
                {"_id": reminder._id}
            )

            if not deletion_result.acknowledged:
                self.bot.logger.error(
                    f"Failed to delete reminder {reminder._id} from MongoDB."
                )
            elif deletion_result.deleted_count == 0:
                self.bot.logger.error(
                    f"Failed to delete reminder {reminder._id} from MongoDB: reminder not found."
                )
            else:
                self.bot.logger.info(
                    f"Successfully deleted reminder {reminder._id} from MongoDB."
                )

        return send_reminder

    async def create_reminder(
        self,
        ctx: InteractionContext,
        relative_time: str,
        reminder_note: str,
    ) -> Reminder | None:
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
            await ctx.send(
                f"Invalid input `{relative_time}`: {e}", ephemeral=True
            )
            return None

        insertion_result = self.bot.db.remindersV7.insert_one(
            reminder.to_dict()
        )
        if not insertion_result.acknowledged:
            self.bot.logger.error("Failed to insert reminder into MongoDB.")
        else:
            self.bot.logger.info(
                f"Inserted reminder into MongoDB with ID {insertion_result.inserted_id}."
            )

        reminder._id = insertion_result.inserted_id

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
                placeholder="e.g. Submit paper",
                required=True,
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

        if reminder is None:
            await modal_ctx.send("Reminder creation failed.")
            return

        await modal_ctx.send(
            f"Reminder registered to send {reminder.timestamp.format('R')}"
            f" ({reminder.timestamp.format('F')}).",
        )

    @slash_command(
        name="remind",
        description="Set a reminder at a given time in the future.",
    )
    @slash_option(
        name="relative_time",
        description="The relative time to send the reminder at, e.g. 'in 5 seconds' or 'in 2 hours'.",
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="reminder_note",
        description="The note to send with the reminder.",
        required=True,
        opt_type=OptionType.STRING,
    )
    async def reminder_slash_cmd(
        self, ctx: SlashContext, relative_time: str, reminder_note: str
    ):
        reminder = await self.create_reminder(ctx, relative_time, reminder_note)

        if reminder is None:
            return

        await ctx.send(
            f"Reminder registered to send {reminder.timestamp.format('R')}"
            f" ({reminder.timestamp.format('F')}).",
        )

    @prefixed_command(
        name="remind", help="Set a reminder at a given time in the future."
    )
    async def reminder_prefixed_cmd(
        self, ctx: PrefixedContext, relative_time: str, reminder_note: str
    ):
        """
        Set a reminder at a given time in the future.

        Parameters
        ----------
        relative_time : str
            The relative time to send the reminder at,
            e.g. "in 5 seconds" or "in 2 hours".
        reminder_note : str
            The note to send with the reminder.
        """

        reminder = await self.create_reminder(ctx, relative_time, reminder_note)

        if reminder is None:
            return

        await ctx.send(
            f"Reminder registered to send {reminder.timestamp.format('R')} ({reminder.timestamp.format('F')})."
        )

    @listen("on_ready")
    async def init_existing_reminders(self):
        """
        Pull all existing reminders from the database
        and schedule them as tasks.
        """
        reminder_dicts = list(self.bot.db.remindersV7.find())

        self.bot.logger.info(
            f"Loaded {len(reminder_dicts)} reminders from MongoDB."
        )

        for reminder_dict in reminder_dicts:
            reminder = Reminder.from_dict(reminder_dict)
            send_reminder = await self.task_from_reminder(reminder)
            send_reminder.start()

        self.bot.logger.info("Started all reminders.")


def setup(bot):
    Reminders(bot)
