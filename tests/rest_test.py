#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the rest interface."""
from time import sleep
import requests
import cherrypy
from cherrypy.test import helper
from pacifica.example.orm import database_setup, ExampleModel
from pacifica.example.rest import Root, error_page_default
from pacifica.example.globals import CHERRYPY_CONFIG


def examplemodel_droptables(func):
    """Setup the database and drop it once done."""
    def wrapper(*args, **kwargs):
        """Create the database table."""
        database_setup()
        func(*args, **kwargs)
        ExampleModel.drop_table()
    return wrapper


class ExampleCPTest(helper.CPWebCase):
    """Base class for all testing classes."""

    HOST = '127.0.0.1'
    PORT = 8069
    url = 'http://{0}:{1}'.format(HOST, PORT)
    headers = {'content-type': 'application/json'}

    @staticmethod
    def setup_server():
        """Bind tables to in memory db and start service."""
        cherrypy.config.update({'error_page.default': error_page_default})
        cherrypy.config.update(CHERRYPY_CONFIG)
        cherrypy.tree.mount(Root(), '/', CHERRYPY_CONFIG)

    @examplemodel_droptables
    def test_default_mul(self):
        """Test a default summation in example."""
        resp = requests.get('http://127.0.0.1:8069/dispatch/mul/2/2')
        self.assertEqual(resp.status_code, 200)
        uuid = resp.text
        sleep(2)
        resp = requests.get('http://127.0.0.1:8069/status/{}'.format(uuid))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(int(resp.text), 4)

    @examplemodel_droptables
    def test_default_sum(self):
        """Test a default summation in example."""
        resp = requests.get('http://127.0.0.1:8069/dispatch/add/2/2')
        self.assertEqual(resp.status_code, 200)
        uuid = resp.text
        sleep(2)
        resp = requests.get('http://127.0.0.1:8069/status/{}'.format(uuid))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(int(resp.text), 4)

    @examplemodel_droptables
    def test_string_mul(self):
        """Test a default summation in example."""
        resp = requests.get('http://127.0.0.1:8069/dispatch/mul/a/2')
        self.assertEqual(resp.status_code, 200)
        uuid = resp.text
        resp = requests.get('http://127.0.0.1:8069/status/{}'.format(uuid))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.text, 'aa')

    @examplemodel_droptables
    def test_error_sum(self):
        """Test a default summation in example."""
        resp = requests.get('http://127.0.0.1:8069/dispatch/add/2/2/2')
        self.assertEqual(resp.status_code, 200)
        uuid = resp.text
        resp = requests.get('http://127.0.0.1:8069/status/{}'.format(uuid))
        self.assertEqual(resp.status_code, 404)

    @examplemodel_droptables
    def test_error_json(self):
        """Test a default summation in example."""
        resp = requests.get('http://127.0.0.1:8069/status')
        self.assertEqual(resp.status_code, 500)
