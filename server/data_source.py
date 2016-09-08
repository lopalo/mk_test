import time
from itertools import permutations
from random import Random

from models import objects, objects_status, get_engine

STATUSES = "waiting", "eating", "sleeping", "flying", "driving"

def id_generator(length):
    for row in permutations("a1b2c3d4e5f6g7", length):
        yield "".join(row)


class Object:
    __slots__ = "random", "id", "description", "status", "x", "y"

    def __init__(self, id, random):
        self.id = id
        self.description = "Description for object: {}".format(id)
        self.x = 0
        self.y = 0
        self.status = STATUSES[0]
        self.random = random

    def update(self):
        r = self.random
        self.status = r.choice([self.status, r.choice(STATUSES)])
        self.x += r.uniform(-50, 50)
        self.y += r.uniform(-50, 50)

class DataSource:

    def __init__(self, *, objects_amount, update_factor, seed=0):
        self._random = rand = Random()
        rand.seed(seed)
        self._update_factor = update_factor
        id_gen = id_generator(6)
        self._objects = [Object(next(id_gen), rand) for _
                         in range(objects_amount)]


    def get_create_expression(self):
        return objects.insert().values([
            {'id': obj.id, 'description': obj.description}
            for obj in self._objects
        ])

    def update_objects(self):
        objects = self._objects
        r = self._random
        amount = int(len(objects) * self._update_factor)
        objects = r.sample(objects, amount)
        for obj in objects:
            obj.update()
        return objects_status.insert().values([
            {'object_id': obj.id,
             'status': obj.status,
             'x': obj.x,
             'y': obj.y}
            for obj in objects
        ])


def db_updater(host, **kwargs):
    source = DataSource(**kwargs)
    engine = get_engine(host)
    with engine.begin() as conn:
        conn.execute(objects_status.delete())
        conn.execute(objects.delete())
        conn.execute(source.get_create_expression())
    yield
    while True:
        upd = source.update_objects()
        engine.execute(upd)
        yield


def start_db_updating(*args, **kwargs):
    updater = db_updater(*args, **kwargs)
    while True:
        ts = time.time()
        next(updater)
        td = time.time() - ts
        time.sleep(max(1 - td, 0))


def main():
    from tornado.options import define, options
    define("pg_host", help="Hostname of PostgreSQL")
    define("objects_amount", type=int, default=1000,
            help="Amount of generated objects")
    define("update_factor", type=float, default=.6,
            help="Fraction of objects updated every second")
    options.parse_command_line()
    start_db_updating(options.pg_host,
                      objects_amount=options.objects_amount,
                      update_factor=options.update_factor)


if __name__ == "__main__":
    main()


