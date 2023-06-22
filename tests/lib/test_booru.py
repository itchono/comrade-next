import booru
import pytest
from aiohttp import ClientSession

from comrade.lib.booru_ext import (
    BOORUS,
    BooruSession,
    autocomplete_query,
)


def test_booru_dict():
    assert BOORUS["danbooru"] == booru.Danbooru
    assert BOORUS["gelbooru"] == booru.Gelbooru


async def test_booru_session_gelbooru(http_session: ClientSession):
    """
    Integrated test; requests a post from gelbooru,
    verifies integrity of the embed, and then makes
    sure that the depleted list of posts exits gracefully.
    """

    gelbooru = booru.Gelbooru(http_session)

    # An image of Dia Kurosawa from Love Live! Sunshine!!
    session = BooruSession(gelbooru, "id:8435932", sort_random=False)

    assert await session.init_posts(0, limit_count=1)

    embed = session.formatted_embed

    assert (
        embed.image.url
        == "https://img3.gelbooru.com/images/ee/3a/ee3a33cc0cf29e9956f2c2f5a35d6ca8.png"
    )

    field_names = [f.name for f in embed.fields]

    assert "Result Count" in field_names

    # The post list should be depleted now
    assert not await session.advance_post()


@pytest.mark.online
async def test_autocomplete_gelbooru(http_session: ClientSession):
    """
    Tests tags completion for gelbooru.
    """
    partial_query = "tsushima_"

    suggestions = await autocomplete_query(
        partial_query, booru.Gelbooru(http_session)
    )

    assert "tsushima_yoshiko" in suggestions
    assert "tsushima_(kancolle)" in suggestions


@pytest.mark.online
async def test_booru_session_danbooru(http_session: ClientSession):
    """
    Integrated test; requests a post from danbooru,
    verifies integrity of the embed, and then makes
    sure that the depleted list of posts exits gracefully.
    """

    danbooru = booru.Danbooru(http_session)

    # An image of Dia Kurosawa from Love Live! Sunshine!!
    session = BooruSession(danbooru, "id:6223033", sort_random=False)

    assert await session.init_posts(0, limit_count=1)

    embed = session.formatted_embed

    assert (
        embed.image.url
        == "https://cdn.donmai.us/original/ee/3a/ee3a33cc0cf29e9956f2c2f5a35d6ca8.png"
    )

    # The post list should be depleted now
    assert not await session.advance_post()


@pytest.mark.online
async def test_autocomplete_danbooru(http_session: ClientSession):
    """
    Tests tags completion for danbooru.
    """
    partial_query = "tsushima_"

    suggestions = await autocomplete_query(
        partial_query, booru.Danbooru(http_session)
    )

    assert "tsushima_yoshiko" in suggestions
    assert "tsushima_(kancolle)" in suggestions
