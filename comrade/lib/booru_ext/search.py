from orjson import loads

from comrade.lib.booru_ext.filters import clean_up_autocomplete_tag
from comrade.lib.booru_ext.structures import BooruType


async def autocomplete_query(
    query: str, booru_obj: BooruType, max_suggestions: int = 10
) -> list[str]:
    """
    Autocomplete tags for a given booru,
    returning a list of possible autocompleted queries.

    Parameters
    ----------
    query : str
        The query to autocomplete.
        e.g. tsushima_yos
    booru_obj : BooruType
        The booru to autocomplete for.
        e.g. BooruType.DANBOORU
    max_suggestions : int, optional
        The maximum number of suggestions to return, by default 10

    Returns
    -------
    list[str]
        The list of autocompleted queries.
        e.g. ["tsushima_yoshiko", "tsushima_yoshiko_(love_live!)", ...]

    Notes
    -----
    This assumes that:
    1. the booru supports tag searching
    2. the query is non-empty
    """

    # Autocomplete only on the most recent tag
    # Break the query into a list of tags

    query_tags = query.split()
    most_recent_tag = query_tags[-1]

    tag_suggestions = loads(await booru_obj.find_tags(most_recent_tag))

    # Clean up the tag suggestions, and remove duplicates if any
    cleaned_tag_suggestions = list(
        dict.fromkeys(map(clean_up_autocomplete_tag, tag_suggestions))
    )
    truncated_tag_suggestions = cleaned_tag_suggestions[:max_suggestions]

    if len(truncated_tag_suggestions) == 0:
        # Send back whatever the query was
        return [query]

    # Otherwise, construct a bunch of possible queries
    base = query_tags[:-1]

    return [f"{' '.join(base + [tag])}" for tag in truncated_tag_suggestions]
