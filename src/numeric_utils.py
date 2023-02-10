def to_int(number: int | None | str | float) -> int:
    """Converts a number to an int .

    Args:
        number (int): integer or None or string or float number

    Returns:
        int:  integer number
    """
    if number is None:
        return 0

    return int(number)


def to_float(number: int | None | str | float) -> float:
    """Converts a number to a float .

    Args:
        number (int): integer or None or string or float number

    Returns:
        float: float number
    """
    if number is None:
        return 0

    return float(number)
