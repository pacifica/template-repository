#!/usr/bin/python
# -*- coding: utf-8 -*-
"""The ORM module defining the SQL model for example."""
import uuid
import json
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from pacifica.auth.user_model import Base, User


def _generate_uuid():
    """Generate a random uuid."""
    return str(uuid.uuid4())


class ExampleModel(Base):
    """Example saving some name data."""

    uuid = Column(String(40), primary_key=True, default=_generate_uuid, index=True)
    value = Column(Text(), default='')
    user_uuid = Column(String(40), ForeignKey('user.uuid'), index=True)
    user = relationship('User')
    created = Column(DateTime(), default=datetime.utcnow)
    updated = Column(DateTime(), default=datetime.utcnow)
    deleted = Column(DateTime(), default=None)


# pylint: disable=too-few-public-methods
class ExampleEncoder(json.JSONEncoder):
    """Session json encoder."""

    def default(self, o):
        """Default method part of the API."""
        plain_keys = [
            'uuid', 'value', 'user_uuid'
        ]
        if isinstance(o, ExampleModel):
            ret = {}
            for key in plain_keys:
                ret[key] = getattr(o, key)
            for key in ['created', 'updated', 'deleted']:
                ret[key] = getattr(o, key).isoformat()
            return ret
        return json.JSONEncoder.default(self, o)


# pylint: disable=invalid-name
def as_example(db, dct):
    """Convert a dictionary to session."""
    if 'uuid' in dct:
        example = db.query(ExampleModel).filter_by(uuid=dct['uuid']).first()
        if not example:
            return None
        for key in ['value', 'user_uuid']:
            if dct.get(key, False):
                setattr(example, key, dct[key])
        for key in ['created', 'updated', 'deleted']:
            if dct.get(key, False):
                setattr(example, key, datetime.fromisoformat(dct[key]))
        return example
    return dct


__all__ = [
    'Session',
    'User',
    'Base'
]