import random

from interactions import CustomEmoji


def owoify(t: str):
    """
    Replace r's and l's with w's (matching case)

    Parameters
    ----------
    t : str
        The string to owoify

    Returns
    -------
    str
        The owoified string
    """
    remove_characters = ["R", "L", "r", "l"]
    for character in remove_characters:
        if character.islower():
            t = t.replace(character, "w")
        else:
            t = t.replace(character, "W")
    return t


def emojify(emojis: list[CustomEmoji], t: str):
    """
    Substitute spaces with emojis from a guild

    Parameters
    ----------
    emojis : list[CustomEmoji]
        The list of emojis to use
    t : str
        The string to emojify

    Returns
    -------
    str
        The emojified string
    """
    return "".join([str(random.choice(emojis)) if s == " " else s for s in t])


def mock(t: str):
    """
    Randomly captializes and lowercases letters in string
    (similarly to the Spongebob meme)

    Parameters
    ----------
    t : str
        The string to mock

    Returns
    -------
    str
        The mocked string
    """
    return "".join([random.choice([c.upper(), c.lower()]) for c in t])
