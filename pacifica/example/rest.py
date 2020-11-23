#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy module containing classes for rest interface."""
from configparser import ConfigParser
from json import dumps
import cherrypy
from cherrypy import HTTPError
from pacifica.auth import auth_session
from .orm import ExampleModel, as_example, ExampleEncoder
from .tasks import example_task


def json_handler(*args, **kwargs):
    """Handle the json output nicely."""
    # pylint: disable=protected-access
    value = cherrypy.serving.request._json_inner_handler(*args, **kwargs)
    return dumps(value, sort_keys=True, indent=4, cls=ExampleEncoder).encode('utf-8')


class Root:
    """CherryPy Root Object."""

    exposed = True
    _cp_config = {}

    def __init__(self, configparser: ConfigParser):
        """Create the root object."""
        self.configparser = configparser

    @cherrypy.tools.json_out(handler=json_handler)
    @cherrypy.tools.json_in()
    @auth_session
    # pylint: disable=invalid-name
    # pylint: disable=no-self-use
    def POST(self, uuid=None, **kwargs):
        """Update an existing or create a session."""
        if not uuid:
            example = ExampleModel()
            example.user_uuid = cherrypy.request.user.uuid
            cherrypy.request.db.add(example)
            cherrypy.request.db.commit()
        else:
            example = cherrypy.request.db.query(ExampleModel).filter_by(uuid=uuid).first()
        if example.user_uuid != cherrypy.request.user.uuid:
            return HTTPError(401, 'You do not own this example.')
        cherrypy.request.json['uuid'] = example.uuid
        example = as_example(cherrypy.request.db, cherrypy.request.json)
        if kwargs.get('commit', False) and not example.complete and not example.processing:
            example.processing = True
            cherrypy.request.db.add(example)
            cherrypy.request.db.commit()
            example.task_uuid = str(example_task.delay(example.method, *(example.numbers)))
        cherrypy.request.db.add(example)
        return example

    @cherrypy.tools.json_out(handler=json_handler)
    # pylint: disable=invalid-name
    # pylint: disable=no-self-use
    def GET(self, uuid=None):
        """Get an existing session."""
        if not uuid:
            return [
                {
                    'uuid': example.uuid,
                    'name': example.name,
                    'processing': example.processing,
                    'complete': example.complete,
                    'exception': example.exception
                }
                for example in cherrypy.request.db.query(ExampleModel).filter_by(user_uuid=cherrypy.request.user.uuid)
            ]
        example = cherrypy.request.db.query(ExampleModel).filter_by(uuid=uuid).first()
        return example

    @auth_session
    # pylint: disable=invalid-name
    # pylint: disable=no-self-use
    def DELETE(self, uuid):
        """Delete a given session."""
        example = cherrypy.request.db.query(ExampleModel).filter_by(uuid=uuid).first()
        if example.user_uuid != cherrypy.request.user.uuid:
            raise HTTPError(401, 'You do not own this example.')
        cherrypy.request.db.delete(example)
