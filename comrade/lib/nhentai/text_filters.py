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
    """
    title_text = ""

    opening_braces = ["[", "("]
    closing_braces = ["]", ")"]

    brace_stack = []
    corr_opening_brace = {b: c for b, c in zip(closing_braces, opening_braces)}

    for c in text:
        if c in opening_braces:
            brace_stack.append(c)

            # If we already have nontrivial title text, ignore the rest of the text
            if title_text.strip() != "":
                return title_text.strip()
            continue

        elif (brace := corr_opening_brace.get(c)) and brace_stack[-1] == brace:
            brace_stack.pop()
            continue

        if len(brace_stack) == 0:
            title_text += c

    return title_text.strip()
