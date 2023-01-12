"""
Test the firestone_lib.cli module.
"""

import unittest
from unittest import mock

from firestone_lib import cli


class CliTest(unittest.TestCase):
    """Test all functions in firestone_lib.cli."""

    def test_init_logger_bad_filename(self):
        """Test firestone_lib.cli.init_logger a bad filename/data into fileConfig."""

        with mock.patch("pkg_resources.resource_stream") as mocker:
            instance = mocker.return_value
            instance.name = "/tmp/XXX1234"
            with self.assertRaises(KeyError):
                cli.init_logging("foo.bar", "baz.conf")

    def test_key_value_as_py(self):
        """Test firestone_lib.cli.KeyValue convert a python string."""
        keyval = cli.KeyValue()

        data = keyval.convert('foo=bar', "foo", None)
        self.assertEqual(data, {"foo": "bar"})

        data = keyval.convert('foo=bar,baz=blah', "foo", None)
        self.assertEqual(data, {"foo": "bar", "baz": "blah"})

    def test_key_value_as_json(self):
        """Test firestone_lib.cli.KeyValue convert a JSON string."""
        keyval = cli.KeyValue()

        data = keyval.convert('{"foo": "bar"}', "foo", None)
        self.assertEqual(data, {"foo": "bar"})

    def test_key_value_as_json_list(self):
        """Test firestone_lib.cli.KeyValue convert a JSON string."""
        keyval = cli.KeyValue()

        data = keyval.convert('{"foo": ["bar", "baz"]}', "foo", None)
        self.assertEqual(data, {"foo": ["bar", "baz"]})

    def test_key_value_none(self):
        """Test firestone_lib.cli.KeyValue convert a None string."""
        keyval = cli.KeyValue()

        data = keyval.convert(None, "foo", None)
        self.assertEqual(data, {})

    def test_key_value_dash(self):
        """Test firestone_lib.cli.KeyValue convert a python dash string."""
        keyval = cli.KeyValue()

        data = keyval.convert("-", "foo", None)
        self.assertEqual(data, "-")

    def test_key_value_dict(self):
        """Test firestone_lib.cli.KeyValue convert a python dict."""
        keyval = cli.KeyValue()

        data = keyval.convert({"foo": "bar"}, "foo", None)
        self.assertEqual(data, {"foo": "bar"})


if __name__ == "__main__":
    unittest.main()
