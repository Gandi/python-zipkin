import unittest
import threading
import socket
import select

from ..transport.scribeclient import Client
from ..models import Trace, Annotation


class Sinkhole(threading.Thread):
    def __init__(self, *args, **kwargs):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("127.0.0.1", 0))
        self.port = self.sock.getsockname()[1]
        self.sock.listen(5)

        self.stopped = False

        super(Sinkhole, self).__init__()

        self.has_received_data = False
        self.has_data = threading.Lock()
        self.has_data.acquire()

    def run(self):
        sockets = [self.sock]

        while not self.stopped:
            readable, _, _ = select.select(sockets, [], [])

            for s in readable:
                if s is self.sock:
                    connection, _ = s.accept()
                    connection.setblocking(0)
                    sockets.append(connection)
                else:
                    data = s.recv(1024)
                    if not data:
                        sockets.remove(s)
                        s.close()
                    else:
                        self.has_received_data = True
                        self.has_data.release()

        self.sock.close()

    def stop(self):
        self.stopped = True
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect_ex(("127.0.0.1", self.port))
        s.close()
        self.join()


class TestClient(unittest.TestCase):
    def setUp(self):
        self.server = Sinkhole()
        self.server.start()

    def tearDown(self):
        self.server.stop()

    def test_simple(self):
        Client.configure(
            {
                "collector": "127.0.0.1",
                "collector.port": self.server.port,
            },
            "",
        )

        trace = Trace("test")
        trace.record(Annotation.string("foo", "bar"))
        Client.get_connection()

        import time

        time.sleep(1)  # Just to give it time to connect

        Client.log(trace)
        self.server.has_data.acquire()
        self.server.has_data.release()
        self.assertTrue(self.server.has_received_data)
        Client.disconnect()
