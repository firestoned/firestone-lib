"""
Common CLI utility functions for firestone and firestone apps.
"""
import configparser
import logging
import logging.config
import time

import click
import pkg_resources


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
    """A custom click parameter type tha takes coma delimited list of items."""

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


IntList = CommaDelimitedList(item_type=click.INT)

PathList = CommaDelimitedList(item_type=click.Path(exists=True))

StrList = CommaDelimitedList()


__all__ = ["init_logging", "IntList", "PathList", "StrList"]
