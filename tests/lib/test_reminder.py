from datetime import datetime, timedelta, timezone

from comrade.lib.reminders import Reminder
from comrade.lib.testing_utils import generate_dummy_context


def test_reminder_expiry_positive():
    now = datetime.now(timezone.utc)
    negative_delta = timedelta(seconds=-1)

    reminder_time = now + negative_delta

    reminder = Reminder(reminder_time, now, 1, 1, 1, "test", "test")

    assert reminder.expired is True


def test_reminder_expiry_negative():
    now = datetime.now(timezone.utc)
    positive_delta = timedelta(seconds=1)

    reminder_time = now + positive_delta

    reminder = Reminder(reminder_time, now, 1, 1, 1, "test", "test")

    assert reminder.expired is False


def test_reminder_generate_from_ctx_dm():
    fake_ctx = generate_dummy_context()

    reminder = Reminder.from_relative_time_and_ctx("1s", fake_ctx, timezone.utc)

    assert reminder.scheduled_time > datetime.now(timezone.utc)

    assert reminder.author_id == fake_ctx.author_id
    assert reminder.context_id == fake_ctx.author_id
    assert reminder.guild_id == fake_ctx.guild_id


def test_reminder_generate_from_ctx_guild():
    fake_ctx = generate_dummy_context(guild_id=1)

    reminder = Reminder.from_relative_time_and_ctx("1s", fake_ctx, timezone.utc)

    assert reminder.scheduled_time > datetime.now(timezone.utc)
    assert reminder.author_id == fake_ctx.author_id
    assert reminder.context_id == fake_ctx.channel_id
    assert reminder.guild_id == fake_ctx.guild_id
