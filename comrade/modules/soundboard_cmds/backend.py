from dataclasses import asdict
from mimetypes import guess_type
from typing import Awaitable, Callable
from urllib.parse import urlparse

from bson import ObjectId
from interactions import ActionRow, BaseContext, spread_to_rows

from comrade.core.comrade_client import Comrade
from comrade.lib.sound_system import SoundboardAudio, download_video_to_mp3


class SoundboardBackend:
    bot: Comrade

    def get_soundboard_audio(self, object_id: str) -> SoundboardAudio | None:
        """
        Get a soundboard audio by its _id.

        Parameters
        ----------
        object_id : str
            The _id of the soundboard audio

        Returns
        -------
        SoundboardAudio
            The soundboard audio, or None if it doesn't exist.
        """
        collection = self.bot.db.soundboardSounds

        doc = collection.find_one({"_id": ObjectId(object_id)})

        if doc is None:
            return None
        return SoundboardAudio.from_dict(doc)

    def get_all_soundboard_audio_in_guild(
        self, guild_id: int
    ) -> list[SoundboardAudio] | None:
        """
        Get all soundboard audio in a guild.

        Parameters
        ----------
        guild_id : int
            The guild to query

        Returns
        -------
        list[SoundboardAudio]
            A list of all soundboard audio in the guild, or None if there are none.
        """
        collection = self.bot.db.soundboardSounds

        cursor = collection.find({"guild_id": guild_id})

        if cursor is None:
            return None
        return list(map(SoundboardAudio.from_dict, cursor))

    def delete_soundboard_audio(self, ctx: BaseContext, name: str) -> None:
        """
        Delete a named soundboard audio from a given server, assuming the author is the
        creator of the sound.

        Parameters
        ----------
        ctx : BaseContext
            Invocation context of the command, containing the guild_id and author_id
        name : str
            The name of the sound
        """
        collection = self.bot.db.soundboardSounds

        result = collection.delete_one(
            {"guild_id": ctx.guild_id, "name": name, "author_id": ctx.author_id}
        )

        if result.deleted_count == 0:
            # figure out why it wasn't deleted

            # check if it exists
            if (
                doc := collection.find_one(
                    {"guild_id": ctx.guild_id, "name": name}
                )
            ) is None:
                raise ValueError("Sound does not exist")
            # check if the author is the same
            elif doc["author_id"] != ctx.author_id:
                raise ValueError("You are not the author of this sound")

            # if we get here, something went wrong
            raise RuntimeError("Could not delete sound due to unknown error")

    async def create_soundboard_audio(
        self, ctx: BaseContext, url: str, name: str, emoji: str
    ) -> SoundboardAudio:
        """
        Creates a new Soundboard Audio instance from a youtube video url.

        Parameters
        ----------
        ctx : BaseContext
            Invocation context of the command
        url : str
            The url of the youtube video
        name : str
            The name of the sound
        emoji : str
            The emoji to use for the sound

        Returns
        -------
        SoundboardAudio
            The created SoundboardAudio instance
        """
        # sanity check: make sure the name is not already taken
        if self.bot.db.soundboardSounds.find_one({"name": name}) is not None:
            raise ValueError("Name is already taken")

        # triage URL based on domain
        parsed_url = urlparse(url)
        netloc = parsed_url.netloc
        # strip www. from the netloc
        if netloc.startswith("www."):
            netloc = netloc[4:]

        # youtube
        if netloc in ["youtube.com", "youtu.be"]:
            # download the video as an mp3 file
            mp3_file = download_video_to_mp3(url, limit_time=15)

            # clone the blob to relay
            doc = await self.bot.relay.create_blob_from_bytes(
                mp3_file, filename=f"{name}.mp3"
            )
        # any other domain
        else:
            # get the mime type
            mime_type, _ = guess_type(url)

            if mime_type is None:
                raise ValueError("Could not determine mime type of url")
            elif not mime_type.startswith("audio"):
                raise ValueError("Mime type is not audio")

            # clone the blob to relay
            doc = await self.bot.relay.create_blob_from_url(url)

        # we want the blob url
        blob_url = doc["blob_url"]

        # create the soundboard audio instance
        audio = SoundboardAudio(
            name, ctx.guild_id, ctx.author_id, blob_url, emoji
        )

        collection = self.bot.db.soundboardSounds
        collection.insert_one(asdict(audio))

        return audio

    async def paginator_callback(
        self, ctx: BaseContext
    ) -> Callable[[int], Awaitable[tuple[list[ActionRow], str]]]:
        """
        Callback for dynamicpaginator to paginate through soundboard audio.
        Assumes that there is at least one soundboard audio in the guild.
        """
        # get all soundboard audio in the guild
        all_audio = self.get_all_soundboard_audio_in_guild(ctx.guild_id)

        # chunk audio into groups of 20
        audio_chunks = [
            all_audio[i : i + 20] for i in range(0, len(all_audio), 20)
        ]

        async def callback(page_number: int) -> tuple[list[ActionRow], str]:
            # get the current chunk
            chunk = audio_chunks[page_number - 1]

            action_rows = spread_to_rows(*[audio.button for audio in chunk])

            # create the embed
            status_str = f"Page {page_number}/{len(audio_chunks)}"

            return action_rows, status_str

        return callback
