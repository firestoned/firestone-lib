"""
Test the firestone_lib.utils module.
"""

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
