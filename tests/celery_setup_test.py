#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test cart database setup class."""
import os
from time import sleep
import threading
import cherrypy
from celery.bin.celery import main as celery_main
from pacifica.example.rest import Root, error_page_default
from pacifica.example.orm import ExampleModel


class TestExampleBase:
    """Contain all the tests for the Cart Interface."""

    PORT = 8069
    HOST = '127.0.0.1'
    url = 'http://{0}:{1}'.format(HOST, PORT)
    headers = {'content-type': 'application/json'}

    @classmethod
    def setup_server(cls):
        """Start all the services."""
        os.environ['EXAMPLE_CPCONFIG'] = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), '..', 'server.conf')
        cherrypy.config.update({'error_page.default': error_page_default})
        cherrypy.config.update(os.environ['EXAMPLE_CPCONFIG'])
        cherrypy.tree.mount(Root(), '/', os.environ['EXAMPLE_CPCONFIG'])

    # pylint: disable=invalid-name
    def setUp(self):
        """Setup the database with in memory sqlite."""
        # pylint: disable=protected-access
        # pylint: disable=no-member
        ExampleModel._meta.database.drop_tables([ExampleModel])
        ExampleModel._meta.database.create_tables([ExampleModel])
        # pylint: enable=no-member

        def run_celery_worker():
            """Run the main solo worker."""
            return celery_main([
                'celery', '-A', 'pacifica.example.tasks', 'worker', '--pool', 'solo',
                '--quiet', '-b', 'redis://127.0.0.1:6379/0'
            ])

        self.celery_thread = threading.Thread(target=run_celery_worker)
        self.celery_thread.start()
        print('Done Starting Celery')
        sleep(3)

    # pylint: disable=invalid-name
    def tearDown(self):
        """Tear down the test and remove local state."""
        try:
            celery_main([
                'celery', '-A', 'pacifica.example.tasks', 'control',
                '-b', 'redis://127.0.0.1:6379/0', 'shutdown'
            ])
        except SystemExit:
            pass
        self.celery_thread.join()
        try:
            celery_main([
                'celery', '-A', 'pacifica.example.tasks', '-b', 'redis://127.0.0.1:6379/0',
                '--force', 'purge'
            ])
        except SystemExit:
            pass
        # pylint: enable=protected-access
