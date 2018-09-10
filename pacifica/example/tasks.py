#!/usr/bin/python
# -*- coding: utf-8 -*-
"""The Celery tasks module."""
from os import getenv
from celery import Celery, Task
from pacifica.example import Example
from pacifica.example.orm import ExampleModel

CELERY_APP = Celery(
    'notifications',
    broker=getenv('BROKER_URL', 'pyamqp://'),
    backend=getenv('BACKEND_URL', 'rpc://')
)


# pylint: disable=too-few-public-methods
# pylint: disable=abstract-method
class ExampleTask(Task):
    """Example Task Class."""

    def on_success(self, retval, task_id, args, kwargs):
        """On success save the return value to DB."""
        super(ExampleTask, self).on_success(retval, task_id, args, kwargs)
        new_task = ExampleModel(
            uuid=task_id,
            value=retval
        )
        ExampleModel.connect()
        with ExampleModel.atomic():
            new_task.save(force_insert=True)
        ExampleModel.close()


@CELERY_APP.task(base=ExampleTask)
def example_task(method_str, *numbers):
    """Get all the events and see which match."""
    numbers_copy = []
    for value in numbers:
        try:
            numbers_copy.append(int(value))
        except ValueError:
            numbers_copy.append(value)
    return getattr(Example, method_str)(*numbers_copy)
