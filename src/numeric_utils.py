def to_int(number: int | None | str | float) -> int:
    if number is None:
        return 0

    return int(number)


def to_float(number: int | None | str | float) -> float:
    if number is None:
        return 0

    return float(number)
