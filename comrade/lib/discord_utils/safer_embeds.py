from typing import Any, Optional

import attrs
from interactions import (
    EMBED_FIELD_VALUE_LENGTH,
    EMBED_MAX_DESC_LENGTH,
    EMBED_MAX_NAME_LENGTH,
    Embed,
    EmbedAuthor,
    EmbedField,
    EmbedFooter,
)

from comrade.lib.text_utils import text_safe_length


def preprocess(max_length: int):
    def tsl(text: Optional[str]) -> Optional[str]:
        """
        Preprocess a string to a safe length
        for sending in a discord embed
        """
        if text is None:
            return None

        return text_safe_length(text, max_length)

    return tsl


@attrs.define(eq=False, order=False, hash=False, kw_only=False)
class SafeLengthEmbed(Embed):
    """
    Embed that actively corrects
    for a title, description, field, author, etc.
    that is too long.
    """

    title: Optional[str] = attrs.field(
        default=None,
        repr=True,
        converter=preprocess(EMBED_MAX_NAME_LENGTH),
    )
    """The title of the embed"""

    description: Optional[str] = attrs.field(
        default=None,
        repr=True,
        converter=preprocess(EMBED_MAX_DESC_LENGTH),
    )
    """The description of the embed"""

    def set_author(
        self,
        name: str,
        url: Optional[str] = None,
        icon_url: Optional[str] = None,
    ) -> "Embed":
        """
        Set the author field of the embed,
        automatically correcting for length.

        Args:
            name: The text to go in the title section
            url: A url link to the author
            icon_url: A url of an image to use as the icon

        """
        self.author = EmbedAuthor(
            name=text_safe_length(name, EMBED_MAX_NAME_LENGTH),
            url=url,
            icon_url=icon_url,
        )
        return self

    def set_footer(self, text: str, icon_url: Optional[str] = None) -> "Embed":
        """
        Set the footer field of the embed,
        automatically correcting for length.

        Args:
            text: The text to go in the title section
            icon_url: A url of an image to use as the icon

        """
        self.footer = EmbedFooter(
            text=text_safe_length(text, 2048), icon_url=icon_url
        )
        return self

    def add_field(self, name: str, value: Any, inline: bool = False) -> "Embed":
        """
        Add a field to the embed,
        automatically correcting for length.

        Args:
            name: The title of this field
            value: The value in this field
            inline: Should this field be inline with other fields?

        """
        self.fields.append(
            EmbedField(
                name=text_safe_length(name, EMBED_MAX_NAME_LENGTH),
                value=text_safe_length(str(value), EMBED_FIELD_VALUE_LENGTH),
                inline=inline,
            )
        )
        self._fields_validation("fields", self.fields)

        return self
