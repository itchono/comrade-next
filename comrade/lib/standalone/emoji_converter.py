# Emoji conversion library
# Converts letters to corresponding regional indicator emojis

import string

_letters = list(string.ascii_lowercase)
_regional_indicators_unicode = [chr(0x1f1e6 + i) for i in range(26)]


def letter_to_regional_indicator(letter: str) -> str:
    '''
    Converts a letter to a regional indicator emoji

    Parameters
    ----------
    letter : str
        The letter to convert to a regional indicator emoji

    Returns
    -------
    str
        The regional indicator emoji corresponding to the letter
    '''
    # normalize letter to lowercase
    letter = letter.lower()

    assert letter in _letters, f"Letter {letter} not in alphabet"
    return _regional_indicators_unicode[_letters.index(letter)]


def string_to_regional_indicator(string: str) -> str:
    '''
    Converts a string to a string of regional indicator emojis

    Parameters
    ----------
    string : str
        The string to convert to a string of regional indicator emojis

    Returns
    -------
    str
        The string of regional indicator emojis corresponding to the string
    '''
    return "".join([letter_to_regional_indicator(letter) for letter in string])


# now do the opposite
def regional_indicator_to_letter(regional_indicator: str) -> str:
    '''
    Converts a regional indicator emoji to a letter

    Parameters
    ----------
    regional_indicator : str
        The regional indicator emoji to convert to a letter

    Returns
    -------
    str
        The letter corresponding to the regional indicator emoji
    '''
    assert regional_indicator in _regional_indicators_unicode, f"Regional indicator {regional_indicator} not in regional indicator unicode list"
    return _letters[_regional_indicators_unicode.index(regional_indicator)]


def regional_indicator_string_to_string(regional_indicator_string: str) -> str:
    '''
    Converts a string of regional indicator emojis to a string

    Parameters
    ----------
    regional_indicator_string : str
        The string of regional indicator emojis to convert to a string

    Returns
    -------
    str
        The string corresponding to the string of regional indicator emojis
    '''
    return "".join([regional_indicator_to_letter(regional_indicator) for regional_indicator in regional_indicator_string])
