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
            instance.name = '/tmp/XXX1234'
            with self.assertRaises(KeyError):
                cli.init_logging("foo.bar", "baz.conf")


if __name__ == '__main__':
    unittest.main()
