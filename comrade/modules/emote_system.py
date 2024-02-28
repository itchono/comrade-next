from interactions import Embed, Extension, listen
from interactions.api.events import MessageCreate

from comrade.core.comrade_client import Comrade
from comrade.lib.discord_utils import echo
from comrade.lib.emotes.finder import find_emote_v5, find_similar_emotes


class EmoteSystem(Extension):
    bot: Comrade

    @listen("message_create")
    async def emote_listener(self, message_event: MessageCreate):
        """
        Listen for CustomEmote calls in messages of the format

        :emote_name:

        Possibly with spaces around the emote name
        e.g. :    emote_name  :

        First attempt to match exact case, but fall back to case-insensitive query

        e.g. :EmoteName: >> :emotename:

        If no match is found, show similarly named emotes based on Levenshtein distance

        e.g. :EmoteName: >> :EmoteName2: :EmoteName3: :EmoteName4:

        If a big emote is found, send it
        If an inline emote is found, do not send it
        (currently still being handled by another bot)

        Parameters
        ----------
        message_event: MessageCreate
            The message event to listen for
        """
        msg = message_event.message

        # If the message contains non-ascii chars, ignore it
        if not msg.content.isascii():
            return

        if msg.content.startswith(":") and msg.content.endswith(":"):
            # remove : :, as well as any spaces around the emote name
            parse_str = msg.content.strip(": ").lower()
            try:
                emote = find_emote_v5(
                    parse_str,
                    self.bot.db.Emotes,
                    message_event.message.guild.id,
                )
            except ValueError:
                similar_emotes = find_similar_emotes(
                    parse_str,
                    self.bot.db.Emotes,
                    message_event.message.guild.id,
                )
                embed = Embed(title="Emote not found.")
                embed.set_footer(
                    text="Emotes with a 60%+ similarity are included in suggestions"
                )

                if similar_emotes:
                    embed.description = "__[I] = Inline, [B] =  Big__\n\n"
                    for emote in similar_emotes:
                        if emote.type == "big":
                            embed.description += f"[B] {emote.name}\n"
                        elif emote.type == "inline":
                            embed.description += f"[I] {emote.name}\n"
                else:
                    embed.description = "No similar emotes found."

                await message_event.message.channel.send(embed=embed)
                return

            if emote.type == "big":
                await echo(msg.channel, msg.author, content=emote.URL)
            elif emote.type == "inline":
                await echo(msg.channel, msg.author, content=emote.URL)  # HOTPATCH FOR EMOTE SYSTEM PROBLEMS


def setup(bot):
    EmoteSystem(bot)
