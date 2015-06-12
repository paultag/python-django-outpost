from .models import SyncableModel
import threading
import queue

import datetime as dt
import socket
import json
import time


class NetworkSyncBackend:
    def __init__(self, host, port, backoff=5):
        self.backoff = backoff
        self.host = host
        self.port = port
        self.connect()

    def connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.host, self.port))

        # Right, ok. Let's just catchup from here on out.
        SyncableModel._stawp()

        timestamp = dt.datetime.fromtimestamp(int(self.s.recv(10)))
        for model in SyncableModel.get_models():
            model._catchup(timestamp)

    def sync(self, obj):
        try:
            return self._sync(obj)
        except BrokenPipeError:
            time.sleep(self.backoff)
            self.connect()
            return self.sync(obj)

    def _sync(self, obj):
        self.s.send(json.dumps({
            "type": {"label": obj._meta.app_label,
                     "model": obj._meta.object_name},
            "object": obj.serialize(),
        }).encode())
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
        q = SyncableModel.get_queue()
        self.running = True
        while self.running:
            try:
                obj = q.get(timeout=0.5)
            except queue.Empty:
                continue
            self.backend.sync(obj)


def sync(*, backend=NetworkSyncBackend, **kwargs):
    o = Sync(backend=backend(**kwargs))
    o.start()
    return o
