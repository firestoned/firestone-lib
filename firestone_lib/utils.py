"""
Utility module for firestone project.
"""
import functools

import asyncio


def click_coro(func):
    """Click coroutine."""
    func = asyncio.coroutine(func)

    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))

    return functools.update_wrapper(wrapper, func)
