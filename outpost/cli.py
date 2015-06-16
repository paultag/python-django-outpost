from django.conf import settings
from django.apps import apps
import django

from .models import SyncableModel, Outpost

import datetime as dt
import socketserver
import threading
import time
import json


class SyncServerHandler(socketserver.BaseRequestHandler):
    def messages(self):
        data = ""
        while True:
            try:
                data += self.request.recv(4096).decode('utf-8')
            except ConnectionResetError:
                print("EOF")
                break

            if data == "":
                break

            while "\n" in data:
                chunk, data = data.split("\n", 1)
                try:
                    yield json.loads(chunk)
                except ValueError as e:
                    print(e)
                    continue

    def hold(self):
        while True:
            self.request.recv(4096).decode('utf-8')

    def broadcast(self, thing):
        data = json.dumps(thing.encapsulate()).encode()
        for connection in self.server.listeners[:]:
            try:
                connection.send(data + b"\n")
            except ConnectionResetError:
                self.server.listeners.remove(connection)

    def handle(self):
        data = self.request.recv(4096).decode('utf-8')
        lines = data.split("\n")
        if lines == []:
            self.request.close()
            return

        name = lines[0]
        if name == "":
            self.server.listeners.append(self.request)
            return self.hold()

        # Now, get the client.
        try:
            outpost = Outpost.objects.get(id=name)
        except Outpost.DoesNotExist:
            self.request.close()
            return

        when = dt.datetime.utcnow(dt.timezone.utc).timestamp()
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
            incoming.outpost = outpost
            self.broadcast(incoming)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    listeners = []


def daemon():
    django.setup()

    server = ThreadedTCPServer((settings.OUTPOST_SERVER, settings.OUTPOST_PORT),
                               SyncServerHandler)

    ip, port = server.server_address
    server.serve_forever()
