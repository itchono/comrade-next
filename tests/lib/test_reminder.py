from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

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


def test_reminder_naive_timestamp():
    now = datetime.now(timezone.utc)
    positive_delta = timedelta(seconds=1)

    reminder_time = now + positive_delta

    reminder = Reminder(reminder_time, now, 1, 1, 1, "test", "test")

    local_tz = datetime.now().astimezone().tzinfo

    assert reminder.naive_scheduled_time == reminder_time.astimezone(
        local_tz
    ).replace(tzinfo=None)


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


def test_reminder_alternate_timezone():
    fake_ctx = generate_dummy_context()
    example_tz = ZoneInfo("US/Central")

    reminder = Reminder.from_relative_time_and_ctx("1s", fake_ctx, example_tz)

    now_plus_1s = datetime.now(example_tz) + timedelta(seconds=1)
    local_tz = datetime.now().astimezone().tzinfo
    naive_now_plus_1s = now_plus_1s.astimezone(local_tz).replace(tzinfo=None)

    assert (reminder.scheduled_time - now_plus_1s).total_seconds() < 1
    assert (
        reminder.naive_scheduled_time - naive_now_plus_1s
    ).total_seconds() < 1
