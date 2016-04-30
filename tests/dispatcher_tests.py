import threading

import pytest

import db
from dispatcher import Dispatcher
from messenger import Messenger


def setup_module(module):
    db.init('a')
    db.deploy()


@pytest.fixture
def session():
    db.deploy()
    return db.get_session()


def _test_create(session):
    Dispatcher()


def _test_start_stop(session):
    disp = Dispatcher()
    disp.start()
    disp.stop()


def _test_run_once_job(session):
    event = threading.Event()

    def append_job(outbox, params):
        event.set()

    disp = Dispatcher()
    disp.register('/append', append_job)
    disp.start()
    try:
        messenger = Messenger(session)  # db.get_session())
        messenger.send('/append')
        assert event.wait(timeout=1)
    finally:
        disp.stop()


def _test_chain_execution(session):
    def job1(outbox, params):
        print 'did 1'
        outbox.send('do_2')

    def job2(outbox, params):
        print 'did 1'
        outbox.send('do_3')

    def job3(outbox, params):
        print 'did 1'
        outbox.send('done')

    disp = Dispatcher()
    disp.register('do_1', job1)
    disp.register('do_2', job2)
    disp.register('do_3', job3)
    disp.start()
    try:
        messenger = Messenger(session)  # db.get_session())
        assert not messenger.recv()
        messenger.send('do_1')
        messenger.subscribe('done')
        import time
        time.sleep(1)
        assert messenger.recv()
    finally:
        disp.stop()


def test_counter(session):
    event = threading.Event()

    def job(outbox, params):
        print params
        if params.counter == 0:
            event.set()
        else:
            outbox.send('counter', counter=params.counter - 1)

    disp = Dispatcher()
    disp.register('counter', job)
    disp.start()
    try:
        messenger = Messenger(session)
        messenger.send('counter', counter=100)
        assert event.wait(timeout=20)
    finally:
        disp.stop()
