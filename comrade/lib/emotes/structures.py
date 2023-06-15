from dataclasses import dataclass

from bson import ObjectId


@dataclass
class EmoteV5:
    """
    Comrade 5.0 emote structure, to be re-done in 7.0
    """

    _id: ObjectId
    name: str
    server: int
    type: str
    ext: str
    URL: str
    size: int

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

    def to_dict(self):
        return {
            "_id": self._id,
            "name": self.name,
            "server": self.server,
            "type": self.type,
            "ext": self.ext,
            "URL": self.URL,
            "size": self.size,
        }
