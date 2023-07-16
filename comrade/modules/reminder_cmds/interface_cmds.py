"""
Context menu and command to set reminders.
"""
import re

from bson import ObjectId
from interactions import (
    Button,
    ButtonStyle,
    CommandType,
    ComponentContext,
    ContextMenuContext,
    InteractionContext,
    Message,
    Modal,
    ModalContext,
    OptionType,
    ShortText,
    TimestampStyles,
    component_callback,
    context_menu,
    slash_option,
)
from interactions.ext.hybrid_commands import HybridContext, hybrid_slash_command

from comrade.core.configuration import ACCENT_COLOUR
from comrade.lib.discord_utils import SafeLengthEmbed
from comrade.lib.reminders import Reminder

from .backend import RemindersBackend


class InterfaceCmds(RemindersBackend):
    async def send_confirmation(
        self, reminder: Reminder, ctx: InteractionContext
    ) -> Message:
        """
        Sends a message confirming that a reminder has been set.
        Also attaches a button to delete the reminder.
        """
        embed = SafeLengthEmbed(
            color=ACCENT_COLOUR,
            description=reminder.note,
            timestamp=reminder.created_at,
            title="Preview of Reminder",
        )
        embed.set_author(
            name=f"Reminder for {ctx.author}",
            url=reminder.jump_url,
            icon_url=ctx.author.avatar.url,
        )

        return await ctx.send(
            "Reminder registered to send "
            f"{reminder.timestamp.format(TimestampStyles.RelativeTime)} at "
            f"{reminder.timestamp.format(TimestampStyles.LongDateTime)}",
            components=[self.del_reminder_button(reminder._id)],
            embed=embed,
        )

    @context_menu(name="Create Reminder", context_type=CommandType.MESSAGE)
    async def reminder_ctx_menu(self, menu_ctx: ContextMenuContext):
        modal = Modal(
            ShortText(
                label="Time from Now",
                placeholder="e.g. '5s' or '2 hours, 7 minutes, 6 seconds'",
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

        reminder = await self.create_and_store_reminder(
            menu_ctx,
            modal_ctx.responses["relative_time"],
            modal_ctx.responses["reminder_note"],
        )

        if reminder is None:
            await modal_ctx.send("Reminder creation failed.")
            return

        await self.start_reminder(reminder)
        await self.send_confirmation(reminder, modal_ctx)

    @hybrid_slash_command(
        name="remind",
        description="Set a reminder at a given time in the future.",
    )
    @slash_option(
        name="time_from_now",
        description=(
            "e.g. '5s' or '2 hours, 7 minutes' or '2d 5h 8m' "
            "(the parser is pretty lenient)"
        ),
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
        self, ctx: HybridContext, time_from_now: str, reminder_note: str
    ):
        reminder = await self.create_and_store_reminder(
            ctx, time_from_now, reminder_note
        )

        if reminder is None:
            return

        msg = await self.send_confirmation(reminder, ctx)

        # patch in the jump url and update in the db (evil hack, needs a better API)
        reminder.jump_url = msg.jump_url
        self.bot.db.remindersV7.update_one(
            {"_id": reminder._id}, {"$set": {"jump_url": msg.jump_url}}
        )
        await self.start_reminder(reminder)

    def del_reminder_button(self, _id: ObjectId) -> Button:
        return Button(
            style=ButtonStyle.DANGER,
            label="Delete Reminder",
            custom_id=f"del_reminder:{_id}",
        )

    @component_callback(re.compile(r"del_reminder:(\w+)"))
    async def del_reminder_callback(self, ctx: ComponentContext):
        # parse the object id from the custom id
        _id = ObjectId(ctx.custom_id.split(":")[1])

        # find the reminder
        reminder_doc = self.bot.db.remindersV7.find_one({"_id": _id})

        # if the reminder doesn't exist, send an error
        if reminder_doc is None:
            await ctx.send(
                "This reminder was probably executed or deleted "
                "already. It is no longer in the database.",
                ephemeral=True,
            )
            return

        reminder = Reminder.from_dict(reminder_doc)

        if reminder.author_id != ctx.author_id:
            await ctx.send(
                "You are not the author of this reminder.",
                ephemeral=True,
            )
            return

        # delete the reminder
        self.clean_up_reminder(reminder)

        # send a confirmation
        await ctx.send("Reminder deleted.", ephemeral=True)
