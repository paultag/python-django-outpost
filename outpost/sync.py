from .core import SyncableModel
from django.conf import settings

import datetime as dt
import threading
import logging
import socket
import queue
import json
import time

log = logging.Logger('outpost')


class NetworkSyncBackend:
    def __init__(self, host, port, backoff=5):
        self.backoff = backoff
        self.host = host
        self.port = port
        SyncableModel._stawp()
        self.connect()

    def connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.host, self.port))
        self.s.send(b"test\n")
        timestamp = dt.datetime.fromtimestamp(int(self.s.recv(10)), dt.timezone.utc)
        for model in SyncableModel.get_models():
            model._catchup(timestamp)

    def sync(self, obj):
        try:
            return self._sync(obj)
        except BrokenPipeError:
            SyncableModel._stawp()
            # We'll be asked for the time again, no need to send dupes.

            time.sleep(self.backoff)
            self.connect()
            return self.sync(obj)

    def _sync(self, obj):
        self.s.send(json.dumps(obj.encapsulate()).encode())
        self.s.send(b'\n')


class Sync:
    def __init__(self, backend):
        self.backend = backend
        self.job = None
        self.running = False

    def start(self):
        self.job = threading.Thread(target=self.run, args=())
        self.job.start()
        return self.job

    def stop(self):
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            q = SyncableModel.get_queue()
            try:
                obj = q.get(timeout=0.5)
            except queue.Empty:
                continue
            self.backend.sync(obj)


def sync(*, backend=NetworkSyncBackend, **kwargs):
    if settings.OUTPOST_ENABLE:
        o = Sync(backend=backend(**kwargs))
        o.start()
        return o
