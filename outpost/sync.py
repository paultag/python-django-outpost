from .models import SyncableModel
import threading
import queue

import socket
import json


class NetworkSyncBackend:
    def __init__(self, host, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
        # defer s.close()

    def sync(self, obj):
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
