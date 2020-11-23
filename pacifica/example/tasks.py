#!/usr/bin/python
# -*- coding: utf-8 -*-
"""The Celery tasks module."""
import sys
from os import getenv
from os.path import join
from argparse import Namespace
from collections import defaultdict
import traceback
from celery import Celery, Task
from pacifica.auth import create_configparser
from pacifica.example import Example
from .orm import ExampleModel
from .config import example_config

configparser = create_configparser(
    Namespace(config=getenv('CONFIG_FILE', 'config.ini')),
    example_config
)
_broker_dir = configparser.get('celery', 'filesystem_broker_dir')
broker_transport_options = defaultdict(
    data_folder_in=join(_broker_dir, 'out'),
    data_folder_out=join(_broker_dir, 'out'),
    data_folder_processed=join(_broker_dir, 'processed')
)
celery_settings = defaultdict(
    loglevel='INFO',
    traceback=True,
    broker_url=configparser.get('celery', 'broker_url'),
    result_backend=configparser.get('celery', 'backend_url'),
)
if 'filesystem' in celery_settings['broker_url']:
    celery_settings['broker_transport_options'] = broker_transport_options
    celery_settings['task_serializer'] = 'json'
    celery_settings['result_serializer'] = 'json'
    celery_settings['accept_content'] = ['json']
    celery_settings['result_persistent'] = False
app = Celery('ingest')
app.conf.update(**celery_settings)

# pylint: disable=abstract-method
class ExampleTask(Task):
    """Example Task Class."""

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # exc (Exception) - The exception raised by the task.
        # args (Tuple) - Original arguments for the task that failed.
        # kwargs (Dict) - Original keyword arguments for the task that failed.
        try:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            with get_db_session(configparser) as db:
                # pylint: disable=no-member
                session = db.query(ExampleModel).filter_by(task_uuid=task_id).first()
                session.complete = True
                session.exception = """
Exception: {}
Backtrace:
================
{}
                """.format(
                    str(exc),
                    ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                )
                db.add(session)
                db.commit()
        finally:
            print('{0!r} failed: {1!r}'.format(task_id, exc))

    def on_success(self, retval, task_id, args, kwargs):
        """On success save the return value to DB."""
        super(ExampleTask, self).on_success(retval, task_id, args, kwargs)
        with get_db_session(configparser) as db:
        new_task = ExampleModel(
            uuid=task_id,
            value=retval
        )
        ExampleModel.connect()
        with ExampleModel.atomic():
            new_task.save(force_insert=True)
        ExampleModel.close()


@app.task(base=ExampleTask)
def example_task(method_str, *numbers):
    """Get all the events and see which match."""
    numbers_copy = []
    for value in numbers:
        try:
            numbers_copy.append(int(value))
        except ValueError:
            numbers_copy.append(value)
    return getattr(Example, method_str)(*numbers_copy)
