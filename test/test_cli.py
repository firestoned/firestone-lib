"""
Test the firestone_lib.cli module.
"""

import configparser
import logging
import os
import tempfile
import time
from pathlib import Path

import unittest
from unittest import mock

import click
import yaml

from firestone_lib import cli


class CliTest(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """Test suite covering CLI helpers."""

    def test_init_logger_bad_filename(self):
        """init_logging surfaces a helpful message when parsing the config fails."""
        resource = mock.Mock()
        resource.joinpath.return_value.open.return_value.name = "/tmp/XXX1234"

        with (
            mock.patch("importlib.resources.files", return_value=resource),
            mock.patch("logging.config.fileConfig", side_effect=configparser.Error("boom")),
            mock.patch("click.echo") as echo_mock,
        ):
            cli.init_logging("foo.bar", "baz.conf")

        resource.joinpath.assert_called_once_with("baz.conf")
        echo_mock.assert_called_once_with("Error parsing logging config file /tmp/XXX1234")

    def test_init_logging_success_sets_gmtime(self):
        """init_logging configures logging and switches formatter time converter."""
        original_converter = logging.Formatter.converter
        self.addCleanup(setattr, logging.Formatter, "converter", original_converter)

        with mock.patch("logging.config.fileConfig") as file_config:
            cli.init_logging("firestone_lib.resources.logging", "cli.conf")
            config_path = Path(file_config.call_args.args[0])
            self.assertTrue(config_path.name.endswith("cli.conf"))
            self.assertIs(logging.Formatter.converter, time.gmtime)

        file_config.assert_called_once()

    def test_key_value_as_py(self):
        """Test firestone_lib.cli.KeyValue convert a python string."""
        keyval = cli.KeyValue()

        data = keyval.convert("foo=bar", "foo", None)
        self.assertEqual(data, {"foo": "bar"})

        data = keyval.convert("foo=bar,baz=blah", "foo", None)
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

    def test_loading_json(self):
        """Test firestone_lib.cli.FromJsonOrYaml convert from JSON to dict."""
        from_json_or_yaml = cli.FromJsonOrYaml()

        data = from_json_or_yaml.convert('{"foo": "bar"}', "foo", None)
        self.assertEqual(data, {"foo": "bar"})

    def test_loading_yaml(self):
        """Test firestone_lib.cli.FromJsonOrYaml convert from YAML to dict."""
        from_json_or_yaml = cli.FromJsonOrYaml()

        data = from_json_or_yaml.convert("foo: bar", "foo", None)
        self.assertEqual(data, {"foo": "bar"})

    def test_loading_yaml_with_jinja(self):
        """Test firestone_lib.cli.FromJsonOrYaml convert from YAML to dict with os.environ."""
        from_json_or_yaml = cli.FromJsonOrYaml()

        os.environ["BAR"] = "bar"
        data = from_json_or_yaml.convert("foo: {{ BAR }}", "foo", None)
        self.assertEqual(data, {"foo": "bar"})

    def test_loading_raw_with_jinja(self):
        """Test firestone_lib.cli.SlurpStrOrFile convert from YAML to dict with os.environ."""
        slurp_str_or_file = cli.SlurpStrOrFile()

        os.environ["BAR"] = "bar"
        data = slurp_str_or_file.convert("foo: {{ BAR }}", "foo", None)
        self.assertEqual(data, "foo: bar")

    def test_comma_delimited_list_variants(self):
        """CommaDelimitedList normalizes string data and preserves existing collections."""
        delimited = cli.CommaDelimitedList()

        self.assertEqual(delimited.convert("foo,bar", "param", None), ["foo", "bar"])
        self.assertEqual(delimited.convert(["foo", "bar"], "param", None), ["foo", "bar"])
        self.assertEqual(delimited.convert("-", "param", None), "-")
        self.assertEqual(delimited.convert(None, "param", None), [])

    def _create_comma_list(self, item_type=click.STRING):
        """Helper to create a CommaDelimitedList with a specific item type."""
        return cli.CommaDelimitedList(item_type=item_type)

    def test_comma_delimited_list_with_custom_type(self):
        """CommaDelimitedList applies the provided item type conversion."""
        numbers = self._create_comma_list(item_type=click.INT)

        self.assertEqual(numbers.convert("1,2,3", "param", None), [1, 2, 3])

    def test_comma_delimited_list_invalid_type(self):
        """CommaDelimitedList reports a helpful error when split() is unavailable."""
        delimited = self._create_comma_list()

        with self.assertRaises(click.BadParameter):
            delimited.convert(123, "param", None)

    def test_path_list_requires_existing_files(self):
        """PathList uses click.Path to enforce existence of each entry."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            first = Path(tmp_dir, "first.txt")
            second = Path(tmp_dir, "second.txt")
            first.write_text("a", encoding="utf-8")
            second.write_text("b", encoding="utf-8")

            result = cli.PathList.convert(f"{first},{second}", "paths", None)

            self.assertEqual(result, [str(first), str(second)])

    def test_slurp_str_or_file_reads_from_file(self):
        """SlurpStrOrFile reads @file targets and renders environment values."""
        slurp_str_or_file = cli.SlurpStrOrFile()

        with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tmp:
            tmp.write("value: {{ TOKEN }}")
            filename = tmp.name

        try:
            with mock.patch.dict(os.environ, {"TOKEN": "abc"}, clear=False):
                rendered = slurp_str_or_file.convert(f"@{filename}", "param", None)

            self.assertEqual(rendered, "value: abc")
        finally:
            os.remove(filename)

    def test_from_json_or_yaml_invalid_payload(self):
        """FromJsonOrYaml surfaces click.BadParameter when parsing fails."""
        parser = cli.FromJsonOrYaml()

        with mock.patch("firestone_lib.cli.yaml.load", side_effect=yaml.YAMLError("boom")):
            with self.assertRaises(click.BadParameter):
                parser.convert("definitely-not-json", "param", None)

    def test_from_json_or_yaml_passthrough_when_fail_suppressed(self):
        """Derived FromJsonOrYaml can bypass failures and return raw data."""

        class SilentParser(cli.FromJsonOrYaml):
            """Custom parser that suppresses failure handling."""

            def fail(self, message, param, ctx):  # type: ignore[override]  # pylint: disable=signature-differs
                return None

        parser = SilentParser()
        marker = object()

        self.assertIs(parser.convert(marker, "param", None), marker)

    def test_slurp_str_or_file_passthrough_value(self):
        """SlurpStrOrFile returns non-str inputs untouched and preserves '-' sentinel."""
        slurp_str_or_file = cli.SlurpStrOrFile()

        marker = object()
        self.assertIs(slurp_str_or_file.convert(marker, "param", None), marker)
        self.assertEqual(slurp_str_or_file.convert("-", "param", None), "-")

    def test_key_value_invalid_format(self):
        """KeyValue rejects inputs missing key separators."""
        keyval = cli.KeyValue()

        with self.assertRaises(ValueError):
            keyval.convert("foo", "param", None)

    def test_key_value_invalid_json_falls_back(self):
        """KeyValue falls back when JSON parsing fails before raising."""
        keyval = cli.KeyValue()

        with mock.patch.object(cli, "FromJsonOrYaml") as mock_loader:
            instance = mock_loader.return_value
            instance.convert.side_effect = click.BadParameter("boom")

            with self.assertRaises(ValueError):
                keyval.convert('{"foo": "bar"}', "param", None)

        instance.convert.assert_called_once()

    def _build_key_value(self, *, item_type=click.STRING, inner_sep=r"=", outer_sep=r","):
        """Create a KeyValue param type with custom configuration."""
        return cli.KeyValue(item_type=item_type, inner_sep=inner_sep, outer_sep=outer_sep)

    def test_key_value_custom_separators_and_type(self):
        """KeyValue supports alternate separators and value coercion."""
        keyval = self._build_key_value(item_type=click.INT, inner_sep=r":", outer_sep=r";")

        self.assertEqual(keyval.convert("foo:1;bar:2", "param", None), {"foo": 1, "bar": 2})

    def test_key_value_item_type_attribute_error(self):
        """KeyValue surfaces click.BadParameter when the inner type fails."""

        class Broken(click.ParamType):
            """Deliberately broken ParamType for negative testing."""

            name = "broken"

            def convert(self, value, param, ctx):
                raise AttributeError("boom")

        keyval = self._build_key_value(item_type=Broken())

        with self.assertRaises(click.BadParameter):
            keyval.convert("foo=bar", "param", None)

    def test_regex_validator(self):
        """RegexValidator returns matching strings and raises on mismatches."""
        validator = cli.RegexValidator(r"^foo-\d+$")

        self.assertEqual(validator.convert("foo-123", "param", None), "foo-123")
        with self.assertRaises(AttributeError):
            validator.convert("bar", "param", None)

    def test_param_type_aliases(self):
        """Alias instances exercise the same conversion logic."""
        self.assertEqual(cli.IntList.convert("1,2", "param", None), [1, 2])
        self.assertEqual(cli.StrDict.convert("foo=bar", "param", None), {"foo": "bar"})
        self.assertEqual(cli.AnyDict.convert('{"foo": "bar"}', "param", None), {"foo": "bar"})


if __name__ == "__main__":
    unittest.main()
