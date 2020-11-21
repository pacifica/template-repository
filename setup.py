#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Setup and install the pacifica service."""
from os import path
from setuptools import setup, find_packages


setup(
    name='pacifica-example',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    description='Pacifica Example Library',
    url='https://github.com/pacifica/template-repository/',
    long_description=open(path.join(
        path.abspath(path.dirname(__file__)),
        'README.md')).read(),
    long_description_content_type='text/markdown',
    author='David Brown',
    author_email='dmlb2000@gmail.com',
    packages=find_packages(),
    namespace_packages=['pacifica'],
    entry_points={
        'console_scripts': [
            'pacifica-example=pacifica.example.__main__:main'
        ]
    },
    install_requires=[
        'celery',
        'cherrypy',
        'sqlalchemy',
        'pacifica-auth'
    ]
)
