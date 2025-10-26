"""
Test the firestone_lib.utils module.
"""

import asyncio
import unittest

from firestone_lib import utils


class CliTest(unittest.TestCase):
    """Test all functions in firestone_lib.cli."""

    def test_split_capitalize_without_sep(self):
        """Test firestone_lib.utils.split_capitalize() without a separator."""
        pretty_str = utils.split_capitalize("foo_bar")

        self.assertEqual(pretty_str, "Foo Bar")

    def test_split_capitalize_with_sep(self):
        """Test firestone_lib.utils.split_capitalize() with a separator."""
        pretty_str = utils.split_capitalize("foo-bar", sep="-")

        self.assertEqual(pretty_str, "Foo Bar")

    def test_split_capitalize_without(self):
        """Test firestone_lib.utils.split_capitalize() without any separator in string."""
        pretty_str = utils.split_capitalize("foobar")

        self.assertEqual(pretty_str, "Foobar")

    def test_click_coro_executes_coroutine(self):
        """Click coroutine runs the decorated async function and returns its result."""

        async def fake_command(value: int) -> int:
            await asyncio.sleep(0)
            return value + 1

        wrapped = utils.click_coro(fake_command)

        self.assertEqual(wrapped(10), 11)
        self.assertEqual(wrapped.__name__, "fake_command")

    def test_click_coro_raises_errors_from_coroutine(self):
        """Click coroutine surfaces errors raised by the async function."""

        class SampleError(RuntimeError):
            """Runtime error used for testing."""

        async def failing_command() -> None:
            raise SampleError("boom")

        wrapped = utils.click_coro(failing_command)

        with self.assertRaises(SampleError):
            wrapped()
