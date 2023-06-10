def text_safe_length(text: str, limiting_length: int) -> str:
    """
    Truncates a string with an ellipsis if it exceeds a certain length,
    otherwise returns the string as-is.
    """
    if len(text) > limiting_length:
        return text[: limiting_length - 3] + "..."
    else:
        return text
