#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Configuration reading and validation module."""
from os import getenv
from configparser import ConfigParser
from .globals import CONFIG_FILE


def example_config(configparser: ConfigParser):
    """Return the ConfigParser object with defaults set."""

