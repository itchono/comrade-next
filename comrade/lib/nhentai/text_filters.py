import re


def filter_title_text(text: str) -> str:
    """
    Converts the title text from the fully formatted title
    to just the title text.

    Extracts the first group of text outside of brackets or parentheses.

    examples:
    '(C91) [Artist] Title (Group) [English]' -> 'Title'
    '[Artist] Title (Group) [English]' -> 'Title'
    '[Artist] Title [English] not the title' -> 'Title'  # ignore the last group

    Parameters
    ----------
    text : str
        The full title text

    Returns
    -------
    str
        The title text

    Note
    ----
    This function is not robust to all cases.
    In the case of an error, the original text is returned.

    This function might also clip certain titles
    where parentheses or brackets are used in the title.
    """

    match_pattern = re.compile(
        r"(?:]|\))([^\[\]\(\)]*[^\[\]\(\)\s]+[^\[\]\(\)]*)(?:\(|\[)"
    )
    # this pattern matches text between a closing brace and an opening brace,
    # but only if the text contains at least one non-whitespace character
    # and exludes braces

    # find all matches
    matches = match_pattern.findall(text)

    # return the first match (after stripping whitespace)
    # or the original text if no matches were found
    return next(map(str.strip, matches), text)
