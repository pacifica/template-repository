#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the rest interface."""
import uuid
from datetime import datetime
from json import dumps, loads
from unittest import TestCase
from pacifica.example.tasks import get_db_session
from pacifica.example.tasks.settings import configparser
from pacifica.example.orm import ExampleModel, ExampleEncoder, as_example
from .base_db_setup_test import BaseDBSetup


class ExampleModelTest(BaseDBSetup, TestCase):
    """Test the example model."""

    def test_create_obj(self):
        """Test deserializing the example object."""
        # pylint: disable=invalid-name
        with get_db_session(configparser) as db:
            new_obj = ExampleModel()
            # pylint: disable=no-member
            db.add(new_obj)
            db.commit()
            new_obj = as_example(db, {
                'uuid': new_obj.uuid,
                'method': 'add',
                'numbers': [2, 2],
                'updated': datetime.now().isoformat()
            })
            self.assertEqual(type(new_obj), ExampleModel, 'return from as_example should be ExampleModel')

    def test_serialize_obj(self):
        """Test serializing the example object."""
        # pylint: disable=invalid-name
        with get_db_session(configparser) as db:
            new_obj = ExampleModel(
                method='add',
                numbers='[2,2]',
                created=datetime.now()
            )
            # pylint: disable=no-member
            db.add(new_obj)
            db.commit()
            json_obj = loads(dumps(new_obj, sort_keys=True, indent=4, cls=ExampleEncoder))
            self.assertEqual(json_obj.get('method'), 'add', 'Method must be add')

    def test_wrong_uuid(self):
        """Test deserializing an object not there."""
        # pylint: disable=invalid-name
        with get_db_session(configparser) as db:
            new_obj = as_example(db, {
                'uuid': str(uuid.uuid4())
            })
            self.assertEqual(new_obj, None, 'If uuid is not found as_example returns None')

    def test_not_example_obj(self):
        """Test deserializing an object not example."""
        # pylint: disable=invalid-name
        with get_db_session(configparser) as db:
            new_obj = as_example(db, [
                {
                    'foo': 'bar'
                }
            ])
            self.assertEqual(type(new_obj), list, 'Return should be pass through')
            self.assertEqual(type(new_obj[0]), dict, 'first object in list is dict')
            self.assertEqual(list(new_obj[0].keys()), ['foo'], 'keys of dict should be just foo')
            self.assertEqual(new_obj[0].get('foo'), 'bar', 'nothing was changed')
