#!/usr/bin/python
# -*- coding: utf-8 -*-
"""The ORM module defining the SQL model for example."""
import uuid
from datetime import datetime
from peewee import Model, CharField, DateTimeField, UUIDField
from playhouse.db_url import connect
from pacifica.example.config import get_config

DB = connect(get_config().get('database', 'peewee_url'))


def database_setup():
    """Setup the database."""
    ExampleModel.database_setup()


class ExampleModel(Model):
    """Example saving some name data."""

    uuid = UUIDField(primary_key=True, default=uuid.uuid4, index=True)
    value = CharField(index=True)
    created = DateTimeField(default=datetime.now, index=True)
    updated = DateTimeField(default=datetime.now, index=True)
    deleted = DateTimeField(null=True, index=True)

    # pylint: disable=too-few-public-methods
    class Meta:
        """The meta class that contains db connection."""

        database = DB
    # pylint: enable=too-few-public-methods

    @classmethod
    def database_setup(cls):
        """Setup the database by creating all tables."""
        if not cls.table_exists():
            cls.create_table()

    @classmethod
    def connect(cls):
        """Connect to the database."""
        cls._meta.database.connect(True)

    @classmethod
    def close(cls):
        """Close the connection to the database."""
        cls._meta.database.close()

    @classmethod
    def atomic(cls):
        """Do the database atomic action."""
        return cls._meta.database.atomic()
