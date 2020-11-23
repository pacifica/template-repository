#!/usr/bin/python
# -*- coding: utf-8 -*-
"""The ORM module defining the SQL model for example."""
import uuid
import json
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean
from pacifica.auth.user_model import Base, User


def _generate_uuid():
    """Generate a random uuid."""
    return str(uuid.uuid4())


# pylint: disable=too-few-public-methods
class ExampleModel(Base):
    """Example saving some name data."""

    plain_keys = [
        'uuid', 'method', 'value', 'task_uuid', 'user_uuid', 'processing',
        'complete', 'exception'
    ]
    date_keys = ['created', 'updated', 'deleted']
    json_keys = ['numbers']

    __tablename__ = 'examplemodel'
    uuid = Column(String(40), primary_key=True, default=_generate_uuid, index=True)
    method = Column(Text(), default='')
    numbers = Column(Text(), default='')
    value = Column(Text(), default='')
    task_uuid = Column(String(40), unique=True, default=None, index=True)
    user_uuid = Column(String(40), ForeignKey('user.uuid'), index=True)
    user = relationship('User')
    processing = Column(Boolean(), default=False)
    complete = Column(Boolean(), default=False)
    exception = Column(Text(), default='')
    created = Column(DateTime(), default=datetime.utcnow)
    updated = Column(DateTime(), default=datetime.utcnow)
    deleted = Column(DateTime(), default=None)


# pylint: disable=too-few-public-methods
class ExampleEncoder(json.JSONEncoder):
    """Session json encoder."""

    def default(self, o):
        """Default method part of the API."""
        if isinstance(o, ExampleModel):
            ret = {}
            for key in ExampleModel.plain_keys:
                ret[key] = getattr(o, key)
            for key in ExampleModel.json_keys:
                ret[key] = []
                if getattr(o, key):
                    ret[key] = json.loads(getattr(o, key))
            for key in ExampleModel.date_keys:
                ret[key] = getattr(o, key).isoformat() if getattr(o, key) else None
            return ret
        return json.JSONEncoder.default(self, o)


# pylint: disable=invalid-name
def as_example(db, dct):
    """Convert a dictionary to session."""
    if 'uuid' in dct:
        example = db.query(ExampleModel).filter_by(uuid=dct['uuid']).first()
        if not example:
            return None
        for key in ExampleModel.plain_keys:
            if key == 'uuid':
                continue
            if dct.get(key, False):
                setattr(example, key, dct[key])
        for key in ExampleModel.json_keys:
            if dct.get(key, False):
                setattr(example, key, json.dumps(dct[key]))
        for key in ExampleModel.date_keys:
            if dct.get(key, False):
                setattr(example, key, datetime.fromisoformat(dct[key]))
        return example
    return dct


__all__ = [
    'User',
    'Base',
    'ExampleModel',
    'as_example',
    'ExampleEncoder'
]
