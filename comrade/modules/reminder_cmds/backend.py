from dataclasses import asdict
from logging import getLogger

from bson import ObjectId
from interactions import (
    DateTrigger,
    InteractionContext,
    Task,
    listen,
)

from comrade.core.comrade_client import Comrade
from comrade.core.configuration import ACCENT_COLOUR
from comrade.lib.discord_utils import (
    SafeLengthEmbed,
    messageable_from_context_id,
)
from comrade.lib.reminders import Reminder

logger = getLogger(__name__)


class RemindersBackend:
    """
    Nuts and bolts used to implement reminders.
    """

    bot: Comrade
    reminder_tasks: dict[ObjectId, Task] = {}  # reminder ID -> task

    def clean_up_reminder(self, reminder: Reminder):
        """
        Clean up a reminder after it has been sent, or
        requested to be deleted.
        Deletes the reminder from the database.
        """
        # Try to cancel the task if it exists
        if reminder._id in self.reminder_tasks:
            self.reminder_tasks[reminder._id].stop()
            del self.reminder_tasks[reminder._id]

        # Clean up the reminder from the database
        deletion_result = self.bot.db.remindersV7.delete_one(
            {"_id": reminder._id}
        )

        if not deletion_result.acknowledged:
            logger.error(
                f"Failed to delete reminder {reminder._id} from MongoDB."
            )
        elif deletion_result.deleted_count == 0:
            logger.error(
                f"Failed to delete reminder {reminder._id} from MongoDB: reminder not found."
            )
        else:
            logger.info(
                f"Successfully deleted reminder {reminder._id} from MongoDB."
            )

    async def get_reminder_task(self, reminder: Reminder) -> Task:
        """
        Generates an interactions.py task from a reminder,
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
        @Task.create(trigger=DateTrigger(reminder.naive_scheduled_time))
        async def send_reminder_task():
            sendable = await messageable_from_context_id(
                reminder.context_id, self.bot
            )

            if not sendable:
                logger.error(
                    f"Failed to send reminder {reminder._id}: "
                    f"could not find channel with ID {reminder.context_id}."
                )
                return

            if reminder.guild_id:
                author = await self.bot.fetch_member(
                    reminder.author_id, reminder.guild_id
                )
                author_name = author.display_name
            else:
                author = await self.bot.fetch_user(reminder.author_id)
                author_name = author.username

            if author is None:
                # e.g. author is no longer in the guild
                logger.error(
                    f"Failed to send reminder {reminder._id}: "
                    f"could not find author with ID {reminder.author_id}."
                )
                self.clean_up_reminder(reminder)
                return

            embed = SafeLengthEmbed(
                color=ACCENT_COLOUR,
                description=reminder.note,
                timestamp=reminder.created_at,
            )
            embed.set_author(
                name=f"Reminder for {author_name}",
                url=reminder.jump_url,
                icon_url=author.avatar.url,
            )
            content = author.mention

            if reminder.jump_url:
                content += f"\nJump to source message: {reminder.jump_url}"

            await sendable.send(
                content=content, embed=embed, reply_to=reminder.reply_id
            )
            logger.info(f"Sent reminder {reminder._id}.")
            self.clean_up_reminder(reminder)

        return send_reminder_task

    async def start_reminder(self, reminder: Reminder) -> Task:
        """
        Starts a reminder as a task.

        Fires off reminder immediately if it is already expired.

        Parameters
        ----------
        reminder : Reminder
            The reminder to start.

        Returns
        -------
        Task
            The task that was started.

        """
        send_reminder = await self.get_reminder_task(reminder)

        if reminder.expired:
            # Fire off the reminder immediately
            logger.warning(
                f"Reminder {reminder._id} expired at "
                f"{reminder.scheduled_time}, executing now."
            )
            await send_reminder.callback()
            return send_reminder

        # otherwise, start the task
        send_reminder.start()
        self.reminder_tasks[reminder._id] = send_reminder
        logger.info(f"Started reminder {reminder._id}.")
        return send_reminder

    async def create_and_store_reminder(
        self,
        ctx: InteractionContext,
        relative_time: str,
        reminder_note: str,
    ) -> Reminder | None:
        """
        Create a reminder from a context and a relative time,
        and insert it into the database.

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
            reminder = Reminder.from_relative_time_and_ctx(
                relative_time, ctx, self.bot.tz, reminder_note
            )
        except ValueError as e:
            await ctx.send(str(e), ephemeral=True)
            return None

        insertion_result = self.bot.db.remindersV7.insert_one(asdict(reminder))
        if not insertion_result.acknowledged:
            logger.error("Failed to insert reminder into MongoDB.")
        else:
            logger.info(
                f"Inserted reminder into MongoDB with ID {insertion_result.inserted_id}."
            )
        return reminder

    @listen("on_ready")
    async def init_existing_reminders(self):
        """
        Pull all existing reminders from the database
        and schedule them as tasks.
        """
        reminder_dicts = list(self.bot.db.remindersV7.find())

        logger.info(
            f"Need to start {len(reminder_dicts)} reminders from MongoDB."
        )

        for reminder_dict in reminder_dicts:
            reminder = Reminder.from_dict(reminder_dict)
            await self.start_reminder(reminder)

        logger.info("Started all reminders.")
