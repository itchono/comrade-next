from __future__ import annotations

from io import BufferedIOBase, BytesIO
from logging import getLogger
from mimetypes import guess_extension

from aiohttp import ClientSession
from interactions import (
    Client,
    File,
    Guild,
    GuildText,
    Listener,
    Message,
    logger_name,
)
from interactions.api.events import MessageCreate
from interactions.client.utils.serializer import get_file_mimetype
from pymongo.collection import Collection


class Relay:
    """
    Server relay system, used for communication between discord bots, and storing blobs

    Communication is performed using the relay channel, which all bots have access to.

    Blobs are stored in the blob-storage channel, which is only accessible to the relay bot.
    This allows us to upload images and other files to Discord, and then store the URL in MongoDB.

    """

    guild: Guild
    http_session: ClientSession
    blob_storage_collection: Collection

    # Cache for channels
    channel_cache: dict[str, GuildText] = {}

    def __init__(
        self,
        guild: Guild,
        http_session: ClientSession,
        blob_storage_collection: Collection,
    ):
        self.guild = guild
        self.http_session = http_session
        self.blob_storage_collection = blob_storage_collection

    async def ensure_channels(self):
        """
        Ensure that all channels exist
        """
        logger = getLogger(logger_name)

        guild_channels = await self.guild.fetch_channels()

        for channel in guild_channels:
            self.channel_cache[channel.name] = channel

        if "relay" not in self.channel_cache:
            self.channel_cache["relay"] = await self.guild.create_text_channel(
                "relay"
            )
            logger.warning(
                f"Created relay channel in {self.guild.name}, because it did not exist."
            )

        if "blob-storage" not in self.channel_cache:
            self.channel_cache[
                "blob-storage"
            ] = await self.guild.create_text_channel("blob-storage")
            logger.warning(
                f"Created blob-storage channel in {self.guild.name}, because it did not exist."
            )

        logger.info(f"Relay: all channels initialized in {self.guild.name}")

    @classmethod
    async def from_bot(cls, bot: Client, guild_id: int) -> Relay:
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

        relay = cls(guild, bot.http_session, bot.db.blobStorage)

        await relay.ensure_channels()

        return relay

    @property
    def blob_storage_channel(self) -> GuildText:
        try:
            return self.channel_cache["blob-storage"]
        except KeyError:
            guild_channels = self.guild.channels
            for channel in guild_channels:
                if channel.name == "blob-storage":
                    self.channel_cache["blob-storage"] = channel
                    return channel

        raise RuntimeError(
            "Could not find blob-storage channel. "
            "You may want to call .ensure_channels() first."
        )

    @property
    def relay_channel(self) -> GuildText:
        try:
            return self.channel_cache["relay"]
        except KeyError:
            guild_channels = self.guild.channels
            for channel in guild_channels:
                if channel.name == "relay":
                    self.channel_cache["relay"] = channel
                    return channel

        raise RuntimeError(
            "Could not find relay channel. "
            "You may want to call .ensure_channels() first."
        )

    async def upload_blob(
        self,
        data: BufferedIOBase,
        mongodb_collection: Collection = None,
        mongodb_document_data: dict = {},
        filename: str = "blob",
    ) -> Message:
        """
        Upload a blob to the blob-storage channel and sync it to MongoDB

        Parameters
        ----------
        data : BufferedIOBase
            The data to store in the blob
        mongodb_collection : Collection, optional
            The MongoDB collection to sync to, by default the one passed to the constructor
        mongodb_document_data : dict, optional
            Additional fields to store in the MongoDB document, by default {}
        filename : str, optional
            The filename to use for the blob (minus extension), by default "blob"

        Notes
        -----
        By default, the MongoDB document will contain the following fields:
        - blob_url: the URL of the blob
        - channel_id: the ID of the Discord channel containing the blob
        - msg_id: the ID of the Discord message containing the blob

        """
        if mongodb_collection is None:
            mongodb_collection = self.blob_storage_collection

        # Infer file extension
        mimetype = get_file_mimetype(data.read())
        data.seek(0)
        extension = guess_extension(mimetype, strict=False)
        if extension is None:
            extension

        msg = await self.blob_storage_channel.send(
            file=File(data, file_name=filename + extension)
        )

        base_document = {
            "blob_url": msg.attachments[0].url,
            "channel_id": self.blob_storage_channel.id,
            "msg_id": msg.id,
        }
        mongodb_collection.insert_one(base_document | mongodb_document_data)

        return msg

    async def mirror_blob(
        self,
        blob_url: str,
        mongodb_collection: Collection = None,
        mongodb_document_data: dict = {},
    ) -> str:
        """
        Mirrors an existing blob from the internet to the
        blob-storage channel and sync it to MongoDB

        Parameters
        ----------
        blob_url : str
            The URL of the blob to mirror
        mongodb_collection : Collection, optional
            The MongoDB collection to sync to, by default the one passed to the constructor
        mongodb_document_data : dict, optional
            Additional fields to store in the MongoDB document, by default {}

        Returns
        -------
        str
            The URL of the mirrored blob


        This allows the function to transparently mirror
        blobs from the internet to Discord,
        """

        async with self.http_session.get(blob_url) as resp:
            data = BytesIO(await resp.read())

        # Tack on the blob URL to the MongoDB document, so we can find it later
        modified_document_data = mongodb_document_data | {
            "source_url": blob_url
        }

        # Upload the blob
        msg = await self.upload_blob(
            data, mongodb_collection, modified_document_data
        )

        return msg.attachments[0].url

    async def get_mirrored_blob(
        self, blob_url: str, mongodb_collection: Collection = None
    ) -> str:
        """
        Gets a blob from the blob-storage channel if it exists,
        otherwise mirrors it from the internet

        Parameters
        ----------
        blob_url : str
            The URL of the blob to mirror
        mongodb_collection : Collection, optional
            The MongoDB collection to sync to, by default the one passed to the constructor

        Returns
        -------
        str
            The URL of the mirrored blob

        Notes
        -----
        it is recommended that the mongoDB collectino have an index
        on the "source_url" field to speed up lookups

        This is the "high-level" function that should be used over mirror_blob.

        """
        if mongodb_collection is None:
            mongodb_collection = self.blob_storage_collection

        # Check if the blob is already mirrored
        doc = mongodb_collection.find_one({"source_url": blob_url})
        if doc:
            return doc["blob_url"]
        else:
            return await self.mirror_blob(blob_url, mongodb_collection)

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

    async def register_listener(self, bot: Client):
        @Listener.create(event_name="message_create")
        async def relay_msg_callback(event: MessageCreate):
            msg = event.message
            if msg._channel_id == self.relay_channel.id:
                bot.logger.info(
                    f"Relay: received message from {msg.author.username} in {msg.guild.name}: {msg.content}"
                )

        bot.add_listener(relay_msg_callback)
