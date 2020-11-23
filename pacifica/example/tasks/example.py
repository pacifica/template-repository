#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Example tasks for a service."""
import sys
import traceback
from celery import Task
from pacifica.example import Example
from .app import app
from .utils import get_db_session
from .settings import configparser
from ..orm import ExampleModel


# pylint: disable=abstract-method
class ExampleTask(Task):
    """Example Task Class."""

    # pylint: disable=too-many-arguments
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Celery on_failure task wrapper."""
        # exc (Exception) - The exception raised by the task.
        # args (Tuple) - Original arguments for the task that failed.
        # kwargs (Dict) - Original keyword arguments for the task that failed.
        try:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            # pylint: disable=invalid-name
            with get_db_session(configparser) as db:
                # pylint: disable=no-member
                session = db.query(ExampleModel).filter_by(uuid=task_id).first()
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
        super().on_success(retval, task_id, args, kwargs)
        # pylint: disable=invalid-name
        with get_db_session(configparser) as db:
            session = ExampleModel(
                uuid=task_id,
                complete=True,
                value=retval
            )
            # pylint: disable=no-member
            db.add(session)
            db.commit()


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
