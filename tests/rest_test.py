#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the rest interface."""
from time import sleep
import requests
from cherrypy.test import helper
from .celery_setup_test import TestExampleBase


class ExampleCPTest(TestExampleBase, helper.CPWebCase):
    """Base class for all testing classes."""

    def test_default_mul(self):
        """Test a default summation in example."""
        resp = requests.get('http://127.0.0.1:8069/dispatch/mul/2/2')
        self.assertEqual(resp.status_code, 200)
        uuid = resp.text
        sleep(2)
        resp = requests.get('http://127.0.0.1:8069/status/{}'.format(uuid))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(int(resp.text), 4)

    def test_default_sum(self):
        """Test a default summation in example."""
        resp = requests.get('http://127.0.0.1:8069/dispatch/add/2/2')
        self.assertEqual(resp.status_code, 200)
        uuid = resp.text
        sleep(2)
        resp = requests.get('http://127.0.0.1:8069/status/{}'.format(uuid))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(int(resp.text), 4)

    def test_string_mul(self):
        """Test a default summation in example."""
        resp = requests.get('http://127.0.0.1:8069/dispatch/mul/a/2')
        self.assertEqual(resp.status_code, 200)
        uuid = resp.text
        resp = requests.get('http://127.0.0.1:8069/status/{}'.format(uuid))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.text, 'aa')

    def test_error_sum(self):
        """Test a default summation in example."""
        resp = requests.get('http://127.0.0.1:8069/dispatch/add/2/2/2')
        self.assertEqual(resp.status_code, 200)
        uuid = resp.text
        resp = requests.get('http://127.0.0.1:8069/status/{}'.format(uuid))
        self.assertEqual(resp.status_code, 404)

    def test_error_json(self):
        """Test a default summation in example."""
        resp = requests.get('http://127.0.0.1:8069/status')
        self.assertEqual(resp.status_code, 500)
