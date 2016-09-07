import sys
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


def start_db_updating(host, **kwargs):
    source = DataSource(**kwargs)
    engine = get_engine(host)
    with engine.begin() as conn:
        conn.execute(objects_status.delete())
        conn.execute(objects.delete())
        conn.execute(source.get_create_expression())
    while True:
        ts = time.time()
        upd = source.update_objects()
        engine.execute(upd)
        td = time.time() - ts
        time.sleep(max(1 - td, 0))


if __name__ == "__main__":
    start_db_updating(sys.argv[1], objects_amount=1000, update_factor=.6)


