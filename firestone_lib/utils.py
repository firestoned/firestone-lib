"""
Utility module for firestone project and anyone else wanting to use it!
"""

import asyncio
from functools import wraps

DEFAULT_SEPARATOR = "_"


def click_coro(func):
    """Click coroutine."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


def split_capitalize(input_str: str, sep: str = None) -> str:
    """Split a string on `sep` and capitalize the words."""
    if sep is None:
        sep = DEFAULT_SEPARATOR

    words = input_str.split(sep)

    pretty_name = []
    for word in words:
        pretty_name.append(word.capitalize())

    return " ".join(pretty_name)
