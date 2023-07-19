from dataclasses import dataclass, field
from typing import Optional

from bson import ObjectId
from interactions import Button, ButtonStyle


@dataclass
class SoundboardAudio:
    """
    Mimics a Soundboard sound on Discord
    """

    name: str
    guild_id: int
    author_id: int
    blob_url: str
    emoji: Optional[str] = None
    _id: ObjectId = field(default_factory=ObjectId)

    @classmethod
    def from_dict(cls, data: dict):
        """
        Create a SoundboardAudio from a MongoDB document.
        """
        return cls(**data)

    @property
    def button(self) -> Button:
        """
        interactable button for this audio instance,
        with the name and emoji on the label, and a custom ID
        corresponding to the _id attribute.
        """
        # default schema for custom id is "soundboard:{_id}}"

        return Button(
            label=self.name,
            emoji=self.emoji,
            custom_id=f"soundboard:{self._id}",
            style=ButtonStyle.PRIMARY,
        )
