#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Configuration reading and validation module."""
from os import getenv
from configparser import ConfigParser
from .globals import CONFIG_FILE


def get_config():
    """Return the ConfigParser object with defaults set."""
    configparser = ConfigParser()
    configparser.add_section('database')
    configparser.set('database', 'peewee_url', getenv(
        'PEEWEE_URL', 'mysql://example:example@localhost:3306/pacifica_example'))
    configparser.add_section('celery')
    configparser.set('celery', 'broker_url', getenv(
        'BROKER_URL', 'pyamqp://'))
    configparser.set('celery', 'backend_url', getenv(
        'BACKEND_URL', 'rpc://'))
    configparser.read(CONFIG_FILE)
    return configparser
