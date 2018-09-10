#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Global configuration options expressed in environment variables."""
from os import getenv
from os.path import expanduser, join

CONFIG_FILE = getenv('EXAMPLE_CONFIG', join(
    expanduser('~'), '.pacifica-example', 'config.ini'))
CHERRYPY_CONFIG = getenv('EXAMPLE_CPCONFIG', join(
    expanduser('~'), '.pacifica-example', 'cpconfig.ini'))
