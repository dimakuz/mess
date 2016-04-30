import logging
from threading import Thread
import gevent

import db
from messenger import Messenger


class _Outbox(object):
    def __init__(self):
        self.messages = []

    def send(self, to, **params):
        self.messages.append((to, params))


class Dispatcher(object):
    def __init__(self):
        self._mapping = {}
        self._running = False
        self._thread = None
        self._outgoing_messages = []

    def register(self, destination, func):
        self._mapping[destination] = func

    def _dispatch_job(self, msg):
        def job_wrapper():
            outbox = _Outbox()
            try:
                self._mapping[msg.destination](
                    outbox,
                    msg.params,
                )
                self._outgoing_messages.extend(outbox.messages)
            except StandardError:
                logging.exception('Error while running job')

        return gevent.spawn(job_wrapper)

    def start(self):
        self._thread = Thread(target=self._run)
        self._running = True
        self._thread.start()

    def _run(self):
        messenger = Messenger(db.get_session())
        running_jobs = set()

        for dest in self._mapping:
            messenger.subscribe(dest)

        counter = 0
        while self._running:
            print 'counter = ', counter
            counter += 1
            messages = messenger.recv()
            for msg in messages:
                running_jobs.add((msg, self._dispatch_job(msg)))

            gevent.sleep(0.01)
            done = gevent.joinall(
                [j[1] for j in running_jobs],
                timeout=0,
            )

            for j in done:
                for msg, job in running_jobs:
                    if j == job:
                        running_jobs.remove((msg, job))
                        messenger.retire(msg.id)
                        break

            while self._outgoing_messages:
                to, params = self._outgoing_messages.pop()
                messenger.send(to, **params)

    def stop(self):
        self._running = False
        self._thread.join()
