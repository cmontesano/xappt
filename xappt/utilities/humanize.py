from typing import Iterable

__all__ = [
    'humanize_list',
    'humanize_bytes',
    'humanize_ordinal',
]


def humanize_list(items: Iterable, conjunction: str = "or") -> str:
    conjunction = f" {conjunction.strip()} "
    items = list(map(lambda x: str(x).strip(), items))
    if len(items) == 0:
        raise ValueError("Expected a collection with at least one item")
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return conjunction.join(items)
    return f"{', '.join(items[:-1])},{conjunction}{items[-1]}"


MAGNITUDE = {
    1000: ('B', 'kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'),
    1024: ('B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB'),
}


def humanize_bytes(value, *, decimal_places: int = 0, binary: bool = True) -> str:
    f = f"{{0:.{decimal_places}f}} {{1}}"
    b = 1024 if binary else 1000
    m = MAGNITUDE[b]
    for i in range(len(m)):
        c = b ** i
        if c >= value:
            p = max(0, i - 1)
            return f.format(float(value) / float(b ** p), m[p])
    p = len(m) - 1
    return f.format(value / (b ** p), m[p])


ORDINAL_SPECIAL_SUFFIX = {1: "st", 2: "nd", 3: "rd"}
ORDINAL_DEFAULT_SUFFIX = "th"
ORDINAL_EXCEPTIONS = (11, 12, 13)


def humanize_ordinal(value: int) -> str:
    suffix = ORDINAL_DEFAULT_SUFFIX
    last_digit = value % 10
    if last_digit in ORDINAL_SPECIAL_SUFFIX.keys():
        if value % 100 not in ORDINAL_EXCEPTIONS:
            suffix = ORDINAL_SPECIAL_SUFFIX[last_digit]
    return f"{value}{suffix}"
