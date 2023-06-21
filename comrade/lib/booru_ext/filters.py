from html import unescape
from urllib.parse import unquote_plus

from comrade.lib.text_utils import escape_md


def clean_up_autocomplete_tag(tag: str) -> str:
    """
    Removes garbage text from autocompletion tags

    input may be of the format:
    kurosawa_rin_(aikatsu%21)

    we want to clean it up to:
    kurosawa_rin_(aikatsu!)

    Parameters
    ----------
    tag : str
        The tag to clean up

    Returns
    -------
    str
        The cleaned up tag
    """

    tag_without_html = unquote_plus(tag).strip()

    # Clean up additional garbage
    # Danbooru: tags may be of the form:
    # kurosawa_dia ai:kurosawa_dia,0% after cleanup
    # drop the ai: onwards
    if " " in tag_without_html:
        return tag_without_html.split(" ")[0]

    return tag_without_html


def clean_up_post_tag(tag: str) -> str:
    """
    Removes garbage text from post tags

    Parameters
    ----------
    tag : str
        The tag to clean up

    Returns
    -------
    str
        The cleaned up tag
    """
    return escape_md(unescape(tag).strip())
