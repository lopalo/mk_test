import time
import json
import unittest

from websocket import create_connection

from data_source import db_updater

TIMEOUT = 1.5
WS_URL = "ws://test_server:80/listen"
DB_HOST = "test_db"


class Client:

    def __init__(self, url, timeout):
        self._conn = create_connection(url, timeout)

    def send(self, payload):
        self._conn.send(json.dumps(payload))

    def recv(self, exp_cmd=None):
        return json.loads(self._conn.recv())

    def close(self):
        self._conn.close()


class TestCase(unittest.TestCase):
    maxDiff = None

    def runTest(self):
        updater = db_updater(
            DB_HOST,
            objects_amount=10,
            update_factor=.6)
        next(updater)
        c1 = self.client()
        c2 = self.client()
        c1.send(["set-limit", 2])
        c2.send(["set-limit", 5])
        self.assertEqual([], c1.recv())
        self.assertEqual([], c2.recv())
        next(updater)
        exp1 = [{'description': 'Description for object: a1b2ce',
                 'object_id': 'a1b2ce',
                 'online': 'online',
                 'status': 'waiting',
                 'x': 46.6606,
                 'y': -2.29902},
                {'description': 'Description for object: a1b2c6',
                 'object_id': 'a1b2c6',
                 'online': 'online',
                 'status': 'flying',
                 'x': 46.78,
                 'y': -14.1951}]
        self.assertEqual(exp1, c1.recv())
        exp2 = [{'description': 'Description for object: a1b2ce',
                 'object_id': 'a1b2ce',
                 'online': 'online',
                 'status': 'waiting',
                 'x': 46.6606,
                 'y': -2.29902},
                {'description': 'Description for object: a1b2c6',
                 'object_id': 'a1b2c6',
                 'online': 'online',
                 'status': 'flying',
                 'x': 46.78,
                 'y': -14.1951},
                {'description': 'Description for object: a1b2c5',
                 'object_id': 'a1b2c5',
                 'online': 'online',
                 'status': 'sleeping',
                 'x': 5.98137,
                 'y': -14.6209},
                {'description': 'Description for object: a1b2c4',
                 'object_id': 'a1b2c4',
                 'online': 'online',
                 'status': 'waiting',
                 'x': -18.9852,
                 'y': 22.9832},
                {'description': 'Description for object: a1b2c3',
                 'object_id': 'a1b2c3',
                 'online': 'online',
                 'status': 'driving',
                 'x': 48.7259,
                 'y': 3.25636}]
        self.assertEqual(exp2, c2.recv())
        time.sleep(3)
        next(updater)
        for _ in range(5):
            c1.recv()
            c2.recv()
        exp1 = [{'description': 'Description for object: a1b2cg',
                 'object_id': 'a1b2cg',
                 'online': 'slow',
                 'status': 'waiting',
                 'x': -19.8553,
                 'y': -20.8909},
                {'description': 'Description for object: a1b2ce',
                 'object_id': 'a1b2ce',
                 'online': 'offline',
                 'status': 'waiting',
                 'x': 46.6606,
                 'y': -2.29902}]
        self.assertEqual(exp1, c1.recv())
        exp2 = [{'description': 'Description for object: a1b2cg',
                 'object_id': 'a1b2cg',
                 'online': 'slow',
                 'status': 'waiting',
                 'x': -19.8553,
                 'y': -20.8909},
                {'description': 'Description for object: a1b2ce',
                 'object_id': 'a1b2ce',
                 'online': 'offline',
                 'status': 'waiting',
                 'x': 46.6606,
                 'y': -2.29902},
                {'description': 'Description for object: a1b2c7',
                 'object_id': 'a1b2c7',
                 'online': 'slow',
                 'status': 'waiting',
                 'x': 21.0253,
                 'y': 28.5048},
                {'description': 'Description for object: a1b2c6',
                 'object_id': 'a1b2c6',
                 'online': 'slow',
                 'status': 'flying',
                 'x': 77.0979,
                 'y': -19.3981},
                {'description': 'Description for object: a1b2c5',
                 'object_id': 'a1b2c5',
                 'online': 'slow',
                 'status': 'waiting',
                 'x': 38.7877,
                 'y': -31.3074}]
        self.assertEqual(exp2, c2.recv())


    def setUp(self):
        super().setUp()
        self._clients = []

    def tearDown(self):
        for c in self._clients:
            c.close()
        self._clients = None

    def client(self):
        c = Client(WS_URL, TIMEOUT)
        self._clients.append(c)
        return c


if __name__ == '__main__':
    unittest.main()
