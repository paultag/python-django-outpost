from django.conf import settings
from django.apps import apps
import django

from .models import SyncableModel

import datetime as dt
import socketserver
import threading
import time
import json

import websockets
import asyncio



class WebsocketBroadcaster(threading.Thread):

    @asyncio.coroutine
    def handle(self, websocket, path):
        self.websockets.append(websocket)
        while True:
            yield from websocket.recv()
            # Forever just drain the pipes?

    def send(self, datum):
        return self.loop.call_soon_threadsafe(asyncio.async, self.signal(datum))

    @asyncio.coroutine
    def signal(self, datum):
        yield from self.queue.put(datum)

    @asyncio.coroutine
    def process(self):
        while True:
            datum = yield from self.queue.get()
            for socket in self.websockets:
                yield from socket.send(json.dumps(datum.encapsulate()))

    def run(self):
        start_server = websockets.serve(self.handle, 'localhost', 30009)
        loop = asyncio.new_event_loop()
        self.loop = loop

        self.websockets = []
        self.queue = asyncio.Queue(loop=loop)

        asyncio.set_event_loop(loop)
        asyncio.get_event_loop().run_until_complete(asyncio.gather(
            self.process(),
            start_server
        ))
        asyncio.get_event_loop().run_forever()


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
        # Now, get the client.

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
            self.server.watcher.send(incoming)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    watcher = None


def daemon():
    django.setup()

    ws = WebsocketBroadcaster()
    ws.start()

    server = ThreadedTCPServer((settings.OUTPOST_SERVER, settings.OUTPOST_PORT),
                               SyncServerHandler)
    server.watcher = ws

    ip, port = server.server_address
    print("nc {} {}".format(ip, port))
    server.serve_forever()
