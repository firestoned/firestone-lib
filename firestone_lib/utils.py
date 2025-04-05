"""
Utility module for firestone project and anyone else wanting to use it!
"""

import functools

import asyncio

DEFAULT_SEPARATOR = "_"


def click_coro(func):
    """Click coroutine."""

    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))

    return functools.update_wrapper(wrapper, func)


def split_capitalize(input_str: str, sep: str = None) -> str:
    """Split a string on `sep` and capitalize the words."""
    if sep is None:
        sep = DEFAULT_SEPARATOR

    words = input_str.split(sep)

    pretty_name = []
    for word in words:
        pretty_name.append(word.capitalize())

    return " ".join(pretty_name)
