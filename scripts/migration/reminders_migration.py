"""
Script used to migrade Comrade V5 reminders to V7.

This only needs to be run once. I anticipate that I will be
the only one who needs to run this script.
"""
from argparse import ArgumentParser
from dataclasses import asdict, dataclass
from datetime import datetime, timezone

from bson import ObjectId
from decouple import config
from pymongo import MongoClient

from comrade.lib.reminders import Reminder

# MongoDB URIs
PROD_MONOGDB_URI: str = config("MIGRATION_PROD_MONGODB_URI")
TEST_MONGODB_URI: str = config("MIGRATION_TEST_MONGODB_URI")


@dataclass
class ReminderV5:
    _id: ObjectId
    server: bool  # whether the reminder was made in a guild
    message: str
    time: datetime  # naive; but the timezone is always UTC when retrieved from the database
    user: int  # user ID
    channel: int  # channel ID
    jumpurl: str  # jump URL to the message

    @classmethod
    def from_dict(cls, **data):
        reminder = cls(**data)

        # if the datetimes are naive, make them aware (UTC)
        if reminder.time.tzinfo is None:
            reminder.time = reminder.time.replace(tzinfo=timezone.utc)
        return reminder

    @property
    def as_reminder_v7(self) -> Reminder:
        """
        Converts the reminder to a Reminder object.
        """
        # the key missing field is the guild ID, which we must manually patch in
        # We can infer this from the jump url

        # format is https://discord.com/channels/{guild_id}/{channel_id}/{message_id}

        if not self.server:
            guild_id = None
        else:
            guild_id = int(self.jumpurl.split("/")[4])

        return Reminder(
            scheduled_time=self.time,
            context_id=self.channel if self.server else self.user,
            author_id=self.user,
            guild_id=guild_id,
            note=self.message,
            jump_url=self.jumpurl,
            _id=self._id,
        )


def main(run_real: bool = False, wipe_dest: bool = False):
    db_prod = MongoClient(PROD_MONOGDB_URI)["Comrade"]
    db_test = MongoClient(TEST_MONGODB_URI)["comradeDB"]

    reminders_v5 = db_prod.Reminders

    if run_real:
        print("***** RUNNING ON REAL DATABASE *****")
        input("Press enter to continue...")
        print("Proceeding with migration")
        reminders_v7 = db_prod.remindersV7
    else:
        reminders_v7 = db_test.remindersV7

    if wipe_dest:
        print("***** WIPING DESTINATION COLLECTION *****")
        input("Press enter to continue...")
        print("Wiping destination collection")
        reminders_v7.delete_many({})

    for reminder_v5_doc in reminders_v5.find():
        reminder_v5 = ReminderV5.from_dict(**reminder_v5_doc)
        print(f"Processing reminder {reminder_v5._id}")

        reminder_v7 = reminder_v5.as_reminder_v7
        insert_result = reminders_v7.insert_one(asdict(reminder_v7))
        print(f"Inserted reminder {insert_result.inserted_id}")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--real",
        action="store_true",
        help="Whether to run the migration on the real database.",
    )
    parser.add_argument(
        "--wipe_dest",
        action="store_true",
        help="Whether to wipe the destination reminder collection before running the migration.",
    )
    args = parser.parse_args()

    main(run_real=args.real, wipe_dest=args.wipe_dest)
