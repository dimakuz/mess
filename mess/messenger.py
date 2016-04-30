from collections import namedtuple
import json
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from db import Base

_MESSAGE_TUPLE = namedtuple('Message', ('id', 'destination', 'params'))


def _dict_to_namedtuple(d):
    _type = namedtuple('ns', d.keys())
    return _type(**d)


class _Parameter(Base):
    __tablename__ = 'param'

    id = Column(Integer, primary_key=True)
    key = Column(String)
    value = Column(String)
    message_id = Column(Integer, ForeignKey('message.id'))


class _Message(Base):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True)
    destination = Column(String)
    params = relationship(
        '_Parameter',
        cascade='save-update',
    )


class Messenger(object):
    def __init__(self, session):
        self._session = session
        self._subscriptions = set()
        self._retrieved_ids = set()

    def subscribe(self, to):
        self._subscriptions.add(to)

    def unsubscribe(self, to):
        if to in self._subscriptions:
            self._subscriptions.remove(to)

    def send(self, to, **kwargs):
        msg = _Message(
            destination=to,
            params=[
                _Parameter(key=k, value=json.dumps(v))
                for k, v in kwargs.items()
            ],
        )

        self._session.add(msg)
        self._session.commit()

        return msg.id

    def recv(self):
        messages = self._session.query(_Message).filter(
            _Message.destination.in_(self._subscriptions),
        ).filter(
            ~_Message.id.in_(self._retrieved_ids),
        ).all()

        for m in messages:
            self._retrieved_ids.add(m.id)

        return [
            _MESSAGE_TUPLE(
                m.id,
                m.destination,
                _dict_to_namedtuple(
                    {p.key: json.loads(p.value) for p in m.params},
                ),
            )
            for m in messages
        ]

    def retire(self, id, force=False):
        self._session.query(_Parameter).filter(
            _Parameter.message_id == id,
        ).delete()
        self._session.query(_Message).filter(_Message.id == id).delete()
        self._session.commit()
        if force or id in self._retrieved_ids:
            self._retrieved_ids.remove(id)
