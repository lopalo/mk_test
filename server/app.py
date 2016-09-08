import json
import asyncio

from tornado.platform.asyncio import AsyncIOMainLoop
from tornado.web import Application, RequestHandler, StaticFileHandler
from tornado.websocket import WebSocketHandler
from tornado.log import app_log

from sqlalchemy import select, case
from sqlalchemy.sql import func
from aiopg.sa import create_engine

from models import objects, objects_status, get_engine_args

ROW_LIMITS = 100, 200, 500, 1000


class Listener:

    def __init__(self, ws):
        self._ws = ws
        self._limit = None
        ws.set_message_handler(self.handle_message)

    @property
    def connected(self):
        return self._ws.ws_connection is not None

    def send(self, data):
        if self._limit is None:
            return
        self._ws.write_message(json.dumps(data[:self._limit]))

    def handle_message(self, message):
        (msg_type, payload) = json.loads(message)
        if msg_type == "set-limit":
            assert payload <= ROW_LIMITS[-1], payload
            self._limit = payload


class ListenersHub:

    def __init__(self):
        self._listeners = []

    def add(self, ws):
        self._listeners.append(Listener(ws))
        self._log_listeners()

    def broadcast(self, data):
        listeners = [i for i in self._listeners if i.connected]
        listeners_changed = self._listeners != listeners
        self._listeners = listeners
        for listener in listeners:
            listener.send(data)
        if listeners_changed:
            self._log_listeners()

    def _log_listeners(self):
        app_log.info("Amount of listeners: {}".format(len(self._listeners)))


class WSHandler(WebSocketHandler):

    def initialize(self, hub):
        self._hub = hub
        self._message_handler = None

    def set_message_handler(self, handler):
        self._message_handler = handler

    def open(self):
        self._hub.add(self)

    def on_message(self, message):
        if self._message_handler is not None:
            self._message_handler(message)


class RowLimitsHandler(RequestHandler):

    def get(self):
        self.write({"row_limits": ROW_LIMITS});


async def configure_db(host):
    return await create_engine(**get_engine_args(host))


async def poll_db(loop, db, hub, period):
    o = objects.c
    os = objects_status.c

    recent_status = (
        select([os.object_id, func.max(os.timestamp).label("ts")]).
        group_by(os.object_id).
        order_by(os.object_id.desc()).
        limit(ROW_LIMITS[-1]).
        cte("recent_status")
    )
    rs = recent_status.c
    sel = (
        select([
            o.description,
            os.object_id,
            os.status,
            os.x,
            os.y,
            case([
                (func.extract("seconds", func.now() - rs.ts) <= 1.5, "online"),
                (func.extract("seconds", func.now() - rs.ts) <= 5, "slow"),
            ], else_="offline").label("online")
        ]).
        where(
            (o.id == os.object_id) &
            (os.object_id == rs.object_id) &
            (os.timestamp == rs.ts)
        ).
        order_by(os.object_id.desc())
    )
    while True:
        ts = loop.time()
        async with db.acquire() as conn:
            result_proxy = await conn.execute(sel)
            res = await result_proxy.fetchall()
        hub.broadcast([dict(i) for i in res])
        td = loop.time() - ts
        await asyncio.sleep(max(period - td, 0), loop=loop)


def configure_app(options):
    AsyncIOMainLoop().install()
    loop = asyncio.get_event_loop()
    db = loop.run_until_complete(configure_db(options.pg_host))
    hub = ListenersHub()
    app = Application([
        (r"/row-limits", RowLimitsHandler),
        (r"/listen", WSHandler, {'hub': hub}),
        (r"/(.*)", StaticFileHandler, {"path": "../public"}),
    ])
    loop.create_task(poll_db(loop, db, hub, options.broadcast_period))
    app.listen(options.port)
    return loop


def main():
    from tornado.options import define, options
    define("pg_host", help="Hostname of PostgreSQL")
    define("port", type=int, help="Port for listening to")
    define("broadcast_period", type=int, default=1, help="Period in seconds")
    options.parse_command_line()

    try:
        configure_app(options).run_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

