from __future__ import annotations

from io import BufferedIOBase, BytesIO
from logging import getLogger
from typing import Any

from interactions import (
    File,
    Guild,
    GuildText,
    Listener,
    Message,
    logger_name,
)
from interactions.api.events import MessageCreate
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

from comrade.core.augmentations import AugmentedClient
from comrade.lib.file_utils import give_filename_extension

from .cache_mixin import RelayCacheMixin
from .update_hook import is_valid_update_wh, perform_update


class Relay(RelayCacheMixin):
    """
    Server relay system, used for communication between discord bots, and storing blobs

    Communication is performed using the relay channel, which all bots have access to.

    Blobs are stored in the blob-storage channel, which is
    only accessible to the relay bot. This allows us to upload images
    and other files to Discord, and then store the URL in MongoDB.

    Relay document schema:
    {
        "_id": blob source URL, or the attachment url of the message
        "blob_url": the URL of the blob in the blob storage channel
        "channel_id": the ID of the channel the blob was sent in
        "message_id": the ID of the message the blob was sent in
        "filename": the filename of the blob
    }

    An in-memory cache is used to avoid unnecessary database queries.
    The in-memory cache starts off empty on startup, and is populated
    as requests are made to find_blob_by_url() and create_blob_from_bytes().
    """

    bot: AugmentedClient
    guild: Guild
    blob_storage_collection: Collection

    # channels
    blob_storage_channel: GuildText = None
    relay_channel: GuildText = None

    def __init__(
        self,
        bot: AugmentedClient,
        guild: Guild,
        blob_storage_collection: Collection,
    ):
        self.bot = bot
        self.guild = guild
        self.blob_storage_collection = blob_storage_collection

        @Listener.create(event_name="message_create")
        async def relay_msg_callback(event: MessageCreate):
            msg = event.message
            if msg._channel_id == self.relay_channel.id:
                if is_valid_update_wh(msg):
                    bot.logger.info("[RELAY] received update webhook")
                    await perform_update(msg, self.bot)
                    return

                bot.logger.info(
                    f"[RELAY] received message from {msg.author.username}"
                    f" in {msg.guild.name}: {msg.content}"
                )

        self.bot.add_listener(relay_msg_callback)

    async def ensure_channels(self):
        """
        Ensure that all channels exist
        """
        logger = getLogger(logger_name)

        guild_channels = await self.guild.fetch_channels()

        channel_mapping = {channel.name: channel for channel in guild_channels}

        try:
            self.relay_channel = channel_mapping["relay"]
        except KeyError:
            self.relay_channel = await self.guild.create_text_channel("relay")
            logger.warning(
                f"Created relay channel in {self.guild.name}, because it did not exist."
            )

        try:
            self.blob_storage_channel = channel_mapping["blob-storage"]
        except KeyError:
            self.blob_storage_channel = await self.guild.create_text_channel(
                "blob-storage"
            )
            logger.warning(
                f"Created blob-storage channel in {self.guild.name},"
                " because it did not exist."
            )

        logger.info(f"[RELAY] all channels initialized in {self.guild.name}")

    @classmethod
    async def from_bot(cls, bot: AugmentedClient, guild_id: int) -> Relay:
        """
        Create a Relay instance from a bot instance

        Parameters
        ----------
        bot : Client
            The bot instance to use
        guild_id : int
            The ID of the guild to use

        Returns
        -------
        Relay
            The created Relay instance

        """
        guild = await bot.fetch_guild(guild_id)
        if not guild:
            raise ValueError(
                f"Could not find guild with ID {guild_id}."
                f"For reference, your guilds are {bot.guilds}"
            )

        relay = cls(bot, guild, bot.db.blobStorage)

        await relay.ensure_channels()

        return relay

    async def create_blob_from_bytes(
        self,
        data: BufferedIOBase,
        mongodb_collection: Collection = None,
        document_data: dict = {},
        filename: str = "blob",
    ) -> dict[str, Any]:
        """
        Upload a blob to the blob-storage channel and sync it to MongoDB

        Parameters
        ----------
        data : BufferedIOBase
            The data to store in the blob
        mongodb_collection : Collection, optional
            The MongoDB collection to sync to, by default the one
            passed to the constructor
        document_data : dict, optional
            Additional fields to store in the MongoDB document, by default {}
        filename : str, optional
            The filename to use for the blob, by default "blob"

        Notes
        -----
        By default, the MongoDB document will contain the following fields:
        - blob_url: the URL of the blob
        - channel_id: the ID of the Discord channel containing the blob
        - message_id: the ID of the Discord message containing the blob

        Returns
        -------
        dict[str, Any]
            The MongoDB document that was created,
            or the existing document if the blob already exists

        """
        if mongodb_collection is None:
            mongodb_collection = self.blob_storage_collection

        # Shortcut: if the document is already in the database, return it
        if "_id" in document_data and (
            doc := mongodb_collection.find_one({"_id": document_data["_id"]})
        ):
            # Cache the document
            self.cache_blob(doc)
            return doc

        filename = give_filename_extension(filename, data.read())
        data.seek(0)

        msg = await self.blob_storage_channel.send(
            file=File(data, file_name=filename)
        )

        base_document = {
            "_id": msg.attachments[0].url,
            "blob_url": msg.attachments[0].url,
            "channel_id": self.blob_storage_channel.id,
            "message_id": msg.id,
            "filename": filename,
        }

        # merge the base document with the additional data, with the
        # additional data taking precedence
        document = base_document | document_data

        # For safety, check if the document is already in the database
        try:
            mongodb_collection.insert_one(document)
            # Cache the document
            self.cache_blob(document)
            return document
        except DuplicateKeyError:
            return mongodb_collection.find_one({"_id": document["_id"]})

    async def create_blob_from_url(
        self,
        source_url: str,
        mongodb_collection: Collection = None,
        document_data: dict = {},
        filename: str = "blob",
    ) -> dict[str, Any]:
        """
        Mirrors an existing blob from the internet to the
        blob-storage channel and sync it to MongoDB

        Parameters
        ----------
        source_url : str
            The URL of the blob to mirror
        mongodb_collection : Collection, optional
            The MongoDB collection to sync to, by default
            the one passed to the constructor
        mongodb_document_data : dict, optional
            Additional fields to store in the MongoDB document, by default {}
        filename : str, optional
            The filename to use for the blob by default "blob"

        Returns
        -------
        dict[str, Any]
            The MongoDB document that was created,

        This allows the function to transparently mirror
        blobs from the internet to Discord,
        """

        async with self.bot.http_session.get(source_url) as resp:
            resp.raise_for_status()
            data = BytesIO(await resp.read())

        # Tack on the blob URL to the MongoDB document, so we can find it later
        modified_document_data = {"_id": source_url} | document_data

        # Upload the blob
        return await self.create_blob_from_bytes(
            data, mongodb_collection, modified_document_data, filename
        )

    async def find_blob_by_url(
        self,
        source_url: str,
        mongodb_collection: Collection = None,
    ) -> str | None:
        """
        Gets a blob from the blob-storage channel if it exists.

        Parameters
        ----------
        source_url : str
            The source URL of the blob to find (i.e. the external URL)
        mongodb_collection : Collection, optional
            The MongoDB collection to sync to, by default
            the one passed to the constructor

        Returns
        -------
        str | None
            The URL of the mirrored blob

        """
        # check cache
        if doc := self.get_cached_blob(source_url):
            return doc["blob_url"]

        if mongodb_collection is None:
            mongodb_collection = self.blob_storage_collection

        # Check if the blob is already mirrored
        doc = mongodb_collection.find_one({"_id": source_url})
        if doc:
            # Cache the document to speed up future lookups
            self.cache_blob(doc)
            return doc["blob_url"]
        else:
            return None

    async def delete_blob(
        self,
        source_url: str,
        mongodb_collection: Collection = None,
        keep_message: bool = True,
    ):
        """
        Deletes a tracked blob from MongoDB, and optionally deletes
        the underlying message as well.

        Deletes all blobs with the given source URL.

        Parameters
        ----------
        source_url : str
            The source URL of the blob to delete (i.e. the external URL)
        mongodb_collection : Collection, optional
            The MongoDB collection to sync to, by default
            the one passed to the constructor
        keep_message : bool, optional
            Whether to keep the underlying message, by default True
            (because Discord storage is free)
        """
        if not mongodb_collection:
            mongodb_collection = self.blob_storage_collection

        doc = mongodb_collection.find_one({"_id": source_url})

        if not doc:
            raise ValueError("Blob not found")

        result = mongodb_collection.delete_one({"_id": source_url})

        # Remove the document from the local cache
        self.uncache_blob(source_url)

        if result.deleted_count == 0:
            raise ValueError("Blob not found")

        if keep_message:
            return

        # Delete the message
        channel = await self.bot.fetch_channel(doc["channel_id"])
        message = await channel.fetch_message(doc["message_id"])
        await message.delete()

    async def send_message(self, message: str) -> Message:
        """
        Send a message to the relay channel

        Parameters
        ----------
        message : str
            The message to send

        Returns
        -------
        Message
            The sent message

        """
        return await self.relay_channel.send(message)
