#!/usr/bin/python
# -*- coding: utf-8 -*-
"""The main module for executing the CherryPy server."""
from configparser import ConfigParser
from sys import argv as sys_argv
import os
import json
import cherrypy
from sqlalchemy.engine import create_engine
from pacifica.auth import error_page_default, quickstart, create_configparser, create_argparser
from .orm import User, Base, ExampleModel, ExampleEncoder
from .tasks import get_db_session
from .rest import Root
from .config import example_config


def _mount_config(configparser: ConfigParser):
    example_config(configparser)
    common_config = {
        '/': {
            'error_page.default': error_page_default,
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        }
    }
    cherrypy.tree.mount(Root(configparser), '/example', config=common_config)


def main(argv=None):
    """Main method to start the httpd server."""
    quickstart(argv, 'Run the example server.', User, 'pacifica.example.orm.User',
               os.path.dirname(__file__), _mount_config)


def cmd(argv=None):
    """Command line admin tool for managing example."""
    parser = create_argparser(argv, 'Admin command line tool.')
    parser.set_defaults(func=lambda x, y: parser.print_help())
    subparsers = parser.add_subparsers(help='sub-command help')
    setup_task_subparser(subparsers)
    setup_db_subparser(subparsers)
    args = parser.parse_args(argv)
    configparser = create_configparser(args, example_config)
    return args.func(args, configparser)


def setup_task_subparser(subparsers):
    """Add the job subparser."""
    task_parser = subparsers.add_parser(
        'task', help='task help', description='get tasks')
    task_parser.add_argument(
        'task_uuids', type=str, nargs='+',
        help='get tasks from passed options.'
    )
    task_parser.set_defaults(func=task_output)


def setup_db_subparser(subparsers):
    """Setup the dbsync subparser."""
    db_parser = subparsers.add_parser(
        'dbsync',
        description='Update or Create the Database.'
    )
    db_parser.set_defaults(func=dbsync)


def task_output(args, configparser):
    """Dump the jobs requested from the command line."""
    tasks = []
    # pylint: disable=invalid-name
    with get_db_session(configparser) as db:
        for task_uuid in args.task_uuids:
            # pylint: disable=no-member
            tasks.append(db.query(ExampleModel).filter_by(uuid=task_uuid).first())
    print(json.dumps(tasks, sort_keys=True, indent=4, cls=ExampleEncoder))
    return 0


def dbsync(_args, configparser):
    """Create/Update the database schema to current code."""
    engine = create_engine(configparser.get('database', 'db_url'))
    Base.metadata.create_all(engine)
    cherrypy.config.update({
        'SOCIAL_AUTH_USER_MODEL': 'pacifica.example.orm.User',
    })
    # this needs to be imported after cherrypy settings are applied.
    # pylint: disable=import-outside-toplevel
    from social_cherrypy.models import SocialBase
    SocialBase.metadata.create_all(engine)
    return 0


if __name__ == '__main__':
    main(sys_argv[1:])
