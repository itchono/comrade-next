from Levenshtein import ratio
from pymongo.collection import Collection

from comrade.lib.emotes.structures import EmoteV5


def find_emote_v5(
    parse_str: str, collection: Collection, context_id: int
) -> EmoteV5:
    """
    Finds an emote, given a string to parse and a mongoDB collection
    corresponding to the emote database

    Parameters
    ----------
    parse_str : str
        The string to parse, stripped of : characters
    collection : Collection
        MongoDB collection containig all emote documents (of form EmoteV5)
    context_id : int
        The Discord ID of the context in which the emote was called,
        in this case a guild channel

    Returns
    -------
    EmoteV5
        An emote instance corresponding to the emote found
    """

    case_sensitive_query = {"name": parse_str, "server": context_id}
    case_insensitive_query = {
        "name": {"$regex": f"^{parse_str}$", "$options": "i"},
        "server": context_id,
    }

    if not (emote_document := collection.find_one(case_sensitive_query)):
        emote_document = collection.find_one(case_insensitive_query)

    try:
        emote = EmoteV5.from_dict(emote_document)
    except TypeError:
        raise ValueError("No emote found")

    return emote


def find_similar_emotes(
    parse_str: str, collection: Collection, context_id: int
) -> list[EmoteV5]:
    """
    Find emotes within 0.6 levenshtein distance of the parse_str

    Parameters
    ----------
    parse_str : str
        The string to parse, stripped of : characters
    collection : Collection
        MongoDB collection containig all emote documents (of form EmoteV5)
    context_id : int
        The Discord ID of the context in which the emote was called,
        in this case a guild channel

    Returns
    -------
    list[EmoteV5]
        A list of emotes with a levenshtein ratio of 0.6 or higher

    """
    all_documents = collection.find({"server": context_id})

    return [
        EmoteV5.from_dict(doc)
        for doc in all_documents
        if ratio(parse_str, doc["name"]) >= 0.6
    ]
