from django.apps import apps
import django

from .models import SyncableModel

import datetime as dt
import socketserver
import threading
import time
import json


class SyncServerHandler(socketserver.BaseRequestHandler):

    def messages(self):
        data = ""
        while True:
            data += self.request.recv(4096).decode('utf-8')
            if data == "":
                break

            while "\n" in data:
                chunk, data = data.split("\n", 1)
                try:
                    yield json.loads(chunk)
                except ValueError as e:
                    print(e)
                    continue

    def handle(self):
        when = dt.datetime.utcnow().timestamp()
        self.request.send("{}".format(int(when)).encode())
        self.request.send(b"\n")
        for data in self.messages():
            type = data.pop("type")
            obj = data.pop("object")

            model = apps.get_model(app_label=type['label'],
                                   model_name=type['model'])

            if not issubclass(model, SyncableModel):
                continue

            incoming = model.hydrate(obj)
            print(incoming)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def daemon():
    django.setup()

    HOST, PORT = "localhost", 2017
    server = ThreadedTCPServer((HOST, PORT), SyncServerHandler)
    ip, port = server.server_address
    print("nc {} {}".format(ip, port))
    server.serve_forever()
