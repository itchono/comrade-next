import asyncio

import booru

from comrade.lib.booru_lib import BOORUS, BooruSession


def test_booru_dict():
    assert BOORUS["danbooru"] == booru.Danbooru
    assert BOORUS["gelbooru"] == booru.Gelbooru


def test_booru_session():
    """
    Integrated test; requests a post from gelbooru,
    verifies integrity of the embed, and then makes
    sure that the depleted list of posts exits gracefully.
    """

    gelbooru = booru.Gelbooru()

    # An image of Dia Kurosawa from Love Live! Sunshine!!
    session = BooruSession(gelbooru, "id:8435932", sort_random=False)

    assert asyncio.run(session.init_posts(0, limit_count=1))

    embed = session.formatted_embed

    assert (
        embed.image.url
        == "https://img3.gelbooru.com/images/ee/3a/ee3a33cc0cf29e9956f2c2f5a35d6ca8.png"
    )

    # The post list should be depleted now
    assert not asyncio.run(session.advance_post())
