"""
Common CLI utility functions for firestone and firestone apps.
"""
import configparser
import io
import json
import logging
import logging.config
import os
import re
import time

import click
import jinja2
import pkg_resources
import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

_LOGGER = logging.getLogger(__name__)


def init_logging(pkg: str, name: str) -> None:
    """Initialize a logging config file for logging.

    :param str pkg: the package name where the logging config is located.
    :param str name: the name of the file to load for logging.
    """
    log_conf = pkg_resources.resource_stream(pkg, name)

    try:
        logging.config.fileConfig(log_conf.name)
        logging.Formatter.converter = time.gmtime
    except configparser.Error:
        click.echo(f"Error parsing logging config file {log_conf.name}")


class CommaDelimitedList(click.ParamType):
    """A custom click parameter type tha takes comma delimited list of items."""

    name = "Comma delimited list"

    def __init__(self, item_type=click.STRING):
        """Constructor for a new comma delimited list."""
        self.item_type = item_type

    # pylint: disable=inconsistent-return-statements
    def convert(self, value: str, param: str, ctx):
        """Convert this param value to a list, given the str."""
        if value == "-":
            return "-"
        if value is None:
            return []
        if isinstance(value, list):
            return value

        try:
            return [self.item_type.convert(item, param, ctx) for item in value.split(",")]
        except AttributeError:
            self.fail(f"{value} is not comma-delimited", param, ctx)


class FromJsonOrYaml(click.ParamType):
    """Converts a string from the CLI as a parameter to JSON or YAML object."""

    name = "String to JSON or YAML object, optionally via a file, using @file.json"

    def convert(self, value, param, ctx):
        """Convert a string from the CLI as a parameter to JSON object."""
        if value == "-":
            return "-"
        if not isinstance(value, str):
            return value

        raw_str = value
        if value.startswith("@"):
            filename = value[1:]
            _LOGGER.debug(f"Reading data from file {filename}...")
            with io.open(filename, "r", encoding="utf-8") as fh:
                raw_str = fh.read()

        template = jinja2.Environment(loader=jinja2.BaseLoader()).from_string(raw_str)
        data = template.render(**os.environ)

        try:
            _LOGGER.debug("Trying json.load")
            return json.loads(data)
        # pylint: disable=broad-exception-caught
        except Exception:
            pass

        try:
            _LOGGER.debug("Trying yaml.load")
            return yaml.load(data, Loader=Loader)
        # pylint: disable=broad-exception-caught
        except Exception:
            self.fail(f"{value} is not in JSON or YAML format", param, ctx)

        return data


class KeyValue(click.ParamType):
    """A custom click parameter type tha takes key/value items."""

    name = "Key and value click type" ""

    def __init__(self, item_type=click.STRING, inner_sep=r"=", outer_sep=r","):
        """Constructor for a new delimited dict."""
        self.item_type = item_type
        self.inner_sep = inner_sep
        self.outer_sep = outer_sep

    # pylint: disable=inconsistent-return-statements
    def convert(self, value: str, param: str, ctx):
        """Convert this param value to a dict, given the str."""
        if value and isinstance(value, str) and value.startswith("{"):
            try:
                json_param_type = FromJsonOrYaml()
                return json_param_type.convert(value, param, ctx)
            # pylint: disable=broad-except
            except Exception:
                pass

        if value == "-":
            return "-"
        if value is None:
            return {}
        if isinstance(value, dict):
            return value

        try:
            data = {}
            for item in re.split(self.outer_sep, value):
                key, val = re.split(self.inner_sep, item)
                data[key] = self.item_type.convert(val, param, ctx)

            return data
        except AttributeError:
            self.fail(f"{value} is not comma-delimited", param, ctx)


IntList = CommaDelimitedList(item_type=click.INT)

PathList = CommaDelimitedList(item_type=click.Path(exists=True))

StrList = CommaDelimitedList()

StrDict = KeyValue()

AnyDict = FromJsonOrYaml()


__all__ = [
    "init_logging",
    "KeyValue",
    "FromJsonOrYaml",
    "IntList",
    "PathList",
    "StrList",
    "StrDict",
    "AnyDict",
]
