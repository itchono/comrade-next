from .relay_main import Relay


class RelayMixin:
    relay: Relay

    async def init_relay(self, guild_id: int):
        """
        Initialize the relay system

        Parameters
        ----------
        guild_id : int
            The ID of the guild to use

        """
        self.relay = await Relay.from_bot(self, guild_id)
