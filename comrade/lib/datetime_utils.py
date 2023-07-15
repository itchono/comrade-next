from datetime import timedelta


def fmt_timedelta(td: timedelta) -> str:
    """
    Formats a timedelta into a human-readable string.

    e.g. 1d, 2h, 3m, 4s

    Parameters
    ----------
    td : timedelta
        The timedelta to format

    Returns
    -------
    str
        The formatted  string
    """
    days = td.days
    hours, rem = divmod(td.seconds, 3600)
    minutes, seconds = divmod(rem, 60)

    if days:
        return f"{days}d, {hours}h, {minutes}m, {seconds}s"
    elif hours:
        return f"{hours}h, {minutes}m, {seconds}s"
    elif minutes:
        return f"{minutes}m, {seconds}s"
    else:
        return f"{seconds}s"
