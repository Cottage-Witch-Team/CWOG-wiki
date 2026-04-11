def create_table_base(cols: dict[str, str]) -> str:
    """Create a str table base for use in Markdown.

    >>> print( create_table_base({'a':"l", 'b':"c", 'c':"r"}) )
    | a | b | c |
    | :-- | :-: | --: |
    """
    alignment = {"l": ":--", "c": ":-:", "r": "--:"}

    column_names = cols.keys()
    column_alignment = [alignment[v] for v in cols.values()]

    line_1 = f"| {' | '.join(column_names)} |"
    line_2 = f"| {' | '.join(column_alignment)} |"

    return f"{line_1}\n{line_2}"


def create_table_row(*args: str) -> str:
    """Create a str table row for use in Markdown.

    >>> print( create_table_row("abc", "def", "ghi") )
    | abc | def | ghi |
    """
    return f"| {' | '.join(args)} |"
