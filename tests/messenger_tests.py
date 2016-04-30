import pytest

import db
from messenger import Messenger


def setup_module(module):
    db.init()
    db.deploy()


@pytest.fixture
def session():
    db.deploy()
    return db.get_session()


def test_create(session):
    Messenger(session)


def test_send(session):
    m = Messenger(session)
    m.send('test_send', a='b', b=1)


def test_empty_recv(session):
    m = Messenger(session)
    assert not m.recv()


def test_recv(session):
    m = Messenger(session)
    sent_id = m.send('test_recv', a='a', b=1)
    m.subscribe('test_recv')
    incoming = m.recv()

    assert len(incoming) == 1
    mm = incoming.pop()
    assert mm.id == sent_id
    assert mm.destination == 'test_recv'
    assert len(mm.params) == 2
    assert mm.params.a == 'a'
    assert mm.params.b == 1


def test_retire(session):
    m = Messenger(session)
    sent_id = m.send('test_retire', a='a', b=1)
    m.subscribe('test_retire')
    m.retire(sent_id)

    assert not m.recv()


def test_recv_twice(session):
    m = Messenger(session)
    m.send('test_recv_twice', a='a', b=1)
    m.subscribe('test_recv_twice')

    assert len(m.recv()) == 1
    assert len(m.recv()) == 0
