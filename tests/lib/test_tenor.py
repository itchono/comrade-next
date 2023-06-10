import aiohttp
import pytest

from comrade.lib.tenor import tenor_link_to_gif


@pytest.mark.parametrize(
    ("picker_link, expected_link"),
    [
        (
            "https://tenor.com/view/kotori-kotori-itsuka-itsuka-kotori-gif-23001734",
            "https://media.tenor.com/Xlyaw4BYs0AAAAAC/kotori-kotori-itsuka.gif",
        ),
        (
            "https://tenor.com/view/fish-react-fish-react-him-thanos-gif-26859685",
            "https://media.tenor.com/y2GeN5HIt7UAAAAd/fish-react-fish-react-him.gif",
        ),
    ],
)
async def test_gif_conversion(
    picker_link: str, expected_link: str, http_session: aiohttp.ClientSession
):
    gif_link = await tenor_link_to_gif(picker_link, http_session)

    assert gif_link == expected_link
