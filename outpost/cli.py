import threading
import socketserver
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
        for data in self.messages():
            print(data)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def daemon():
    HOST, PORT = "localhost", 0
    server = ThreadedTCPServer((HOST, PORT), SyncServerHandler)
    ip, port = server.server_address
    # print("nc {} {}".format(ip, port))
    server.serve_forever()
