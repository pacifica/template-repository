#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the rest interface."""
import uuid
from collections import namedtuple
from unittest import TestCase
from mock import patch
from pacifica.example.orm import ExampleModel
from pacifica.example.rest import Root
from pacifica.example.tasks import get_db_session
from pacifica.example.tasks.settings import configparser
from .base_db_setup_test import BaseDBSetup

MockCPUser = namedtuple('MockCPUser', ['uuid'])


class ExampleRestTest(BaseDBSetup, TestCase):
    """Base class for all testing classes."""

    @patch('cherrypy.request')
    def test_default_mul(self, cp_request):
        """Test a default summation in example."""
        setattr(cp_request, 'user', MockCPUser(uuid=str(uuid.uuid4())))
        # pylint: disable=invalid-name
        with get_db_session(configparser) as db:
            setattr(cp_request, 'db', db)
            setattr(cp_request, 'json', {
                'method': 'add',
                'numbers': [2, 2]
            })
            obj = Root(configparser).POST()
            self.assertEqual(type(obj), ExampleModel, 'Type of return object should be dict')
            self.assertEqual(obj.method, 'add', 'Method of return dictionary should be add')
