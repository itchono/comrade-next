def escape_md(t: str):
    """
    Escape markdown characters in a string

    Parameters
    ----------
    t : str
        The string to escape

    Returns
    -------
    str
        The escaped string
    """
    return t.replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")
