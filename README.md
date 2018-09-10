# Pacifica Template Repository
[![Build Status](https://travis-ci.org/pacifica/template-repository.svg?branch=master)](https://travis-ci.org/pacifica/template-repository)
[![Build status](https://ci.appveyor.com/api/projects/status/eg2r1y37yvxi0b5p?svg=true)](https://ci.appveyor.com/project/dmlb2000/template-repository)
[![Maintainability](https://api.codeclimate.com/v1/badges/f2dba248b1a7966e5a49/maintainability)](https://codeclimate.com/github/pacifica/template-repository/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/f2dba248b1a7966e5a49/test_coverage)](https://codeclimate.com/github/pacifica/template-repository/test_coverage)

This repository is to serve as a template for building new
services the Pacifica way. This repository has pipelines
for travis and appveyor to build your code and pre-commit
and pytest to fix your code.

## The Parts

There are several parts to this code as it encompasses
integrating several python libraries together.

 * [PeeWee](http://docs.peewee-orm.com/en/latest/)
 * [CherryPy](https://cherrypy.org/)
 * [Celery](http://www.celeryproject.org/)

For each major library we have integration points in
specific modules to handle configuration of each library.

### PeeWee

The configuration of PeeWee is pulled from an INI file parsed
from an environment variable or command line option. The
configuration in the file is a database
[connection url](http://docs.peewee-orm.com/en/latest/peewee/database.html#connecting-using-a-database-url).

 * [Example PeeWee Model](pacifica/example/orm.py)
 * [Example Config Parser](pacifica/example/config.py)

### CherryPy

The CherryPy configuration has two entrypoints for use. The
WSGI interface and the embedded server through the main
method.

 * [Example Main Method](pacifica/example/__main__.py)
 * [Example WSGI API](pacifica/example/wsgi.py)
 * [Example CherryPy Objects](pacifica/example/rest.py)

### Celery

The Celery tasks are located in their own module and have
an entrypoint from the CherryPy REST objects. The tasks
save state into a PeeWee database that is also accessed
in the CherryPy REST objects.

 * [Example Tasks](pacifica/example/tasks.py)

## Start Up Process

The default way to start up this service is with a shared
SQLite database. The database must be located in the
current working directory of both the celery workers and
the CherryPy web server. The messaging system in
[Travis](.travis.yml) and [Appveyor](appveyor.yml) is
redis, however the default is rabbitmq.

There are three commands needed to start up the services.
Perform these steps in three separate terminals.

 1. `docker-compose up rabbit`
 2. `celery -A pacifica.example.tasks worker -l info`
 3. `python -m pacifica.example`

To test working system run the following in bash:

 1. `UUID=$(curl http://127.0.0.1:8069/dispatch/add/2/2)`
 2. `curl http://127.0.0.1:8069/status/$UUID`
