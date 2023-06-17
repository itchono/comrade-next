def filter_title_text(text: str) -> str:
    """
    Converts the title text from the fully formatted title
    to just the title text.

    The full title text contains text grouped in square brackets and parentheses.
    The title text is the first group of text not enclosed in
    square brackets or parentheses.

    Ignore all subsequent groups of text that are not enclosed
    in square brackets or parentheses.

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
    """
    title_text = ""

    opening_braces = ["[", "("]
    closing_braces = ["]", ")"]

    brace_stack = []
    corr_opening_brace = {b: c for b, c in zip(closing_braces, opening_braces)}

    try:
        for c in text:
            if c in opening_braces:
                # if c is an opening brace, push it onto the stack
                brace_stack.append(c)

                # If we already have nontrivial title text, ignore the rest of the text
                if title_text.strip() != "":
                    return title_text.strip()

                continue

            elif c in closing_braces:
                # If c is a closing brace

                if len(brace_stack) == 0:
                    # closing brace without opening brace,
                    # silently ignore, but clear title text
                    title_text = ""

                elif brace_stack[-1] == corr_opening_brace[c]:
                    brace_stack.pop()

                continue

            elif len(brace_stack) == 0:
                title_text += c

        return title_text.strip()

    except Exception:
        # this should not usually
        # happen, but if it does, return the original text
        return text
