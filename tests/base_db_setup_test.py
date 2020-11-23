#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test base database setup class."""
from os import unlink
from os.path import isfile
from pacifica.example.__main__ import cmd


class BaseDBSetup:
    """Setup the database and tear it down when done."""

    # pylint: disable=invalid-name
    # pylint: disable=no-self-use
    def setUp(self) -> None:
        """Create the database."""
        cmd(['dbsync'])

    # pylint: disable=invalid-name
    # pylint: disable=no-self-use
    def tearDown(self) -> None:
        """Delete the sqlite db."""
        if isfile('db.sqlite3'):
            unlink('db.sqlite3')
