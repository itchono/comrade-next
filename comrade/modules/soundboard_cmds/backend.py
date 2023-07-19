from dataclasses import asdict
from urllib.parse import urlparse

from bson import ObjectId
from interactions import BaseContext

from comrade.core.comrade_client import Comrade
from comrade.lib.sound_system.downloader import download_video_to_mp3
from comrade.lib.sound_system.structures import SoundboardAudio


class SoundboardBackend:
    bot: Comrade

    def get_soundboard_audio(self, object_id: str) -> SoundboardAudio | None:
        collection = self.bot.db.soundboardSounds

        doc = collection.find_one({"_id": ObjectId(object_id)})

        if doc is None:
            return None
        return SoundboardAudio.from_dict(doc)

    def get_all_soundboard_audio_in_guild(
        self, guild_id: int
    ) -> list[SoundboardAudio] | None:
        collection = self.bot.db.soundboardSounds

        cursor = collection.find({"guild_id": guild_id})

        if cursor is None:
            return None
        return list(map(SoundboardAudio.from_dict, cursor))

    async def create_soundboard_audio(
        self, ctx: BaseContext, url: str, name: str
    ) -> SoundboardAudio:
        """
        Creates a new Soundboard Audio instance from a youtube video url.
        """

        # ensure that the url is a youtube video url
        parsed_url = urlparse(url)
        netloc = parsed_url.netloc
        # strip www. from the netloc
        if netloc.startswith("www."):
            netloc = netloc[4:]

        if netloc not in ["youtube.com", "youtu.be"]:
            raise ValueError("URL is not a youtube video url.")

        # download the video as an mp3 file
        mp3_file = download_video_to_mp3(url)

        # clone the blob to relay
        doc = await self.bot.relay.create_blob_from_bytes(mp3_file)

        # we want the blob url
        blob_url = doc["blob_url"]

        # create the soundboard audio instance
        audio = SoundboardAudio(name, ctx.guild_id, ctx.author_id, blob_url)

        collection = self.bot.db.soundboardSounds
        collection.insert_one(asdict(audio))

        return audio
