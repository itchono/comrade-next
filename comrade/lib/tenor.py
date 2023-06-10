import aiohttp
import bs4


async def tenor_link_to_gif(
    link: str, http_session: aiohttp.ClientSession
) -> str:
    """
    Converts a Tenor link to a GIF link.

    Parameters
    ----------
    link: str
        The Tenor link to convert.
    http_session : aiohttp.ClientSession
        The aiohttp ClientSession to use for the request.

    Returns
    -------
    str
        The GIF link.
    """
    # Validate link format
    if not link.startswith("https://tenor.com/view/"):
        raise ValueError("Link is not a Tenor link")

    async with http_session.get(link) as response:
        html = await response.text()

    soup = bs4.BeautifulSoup(html, "lxml")

    # Find the <img> tag with the GIF
    img = soup.find("img", src=lambda x: x.endswith(".gif"))

    # Get the GIF link
    return img["src"]
