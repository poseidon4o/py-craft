from os import path
import json
import random
from ..utils import ilist, ceil_abs

class WorldObject:
    type = None

    @classmethod
    def init(cls, resource_path):
        objects_file = open(path.join(resource_path, 'world_types.json'))
        cls._type = dict()

        for item in json.loads(objects_file.read()):
            cls._type[item['name']] = item

        objects_file.close()

    def __init__(self, object_type):
        if WorldObject._type is None:
            raise RuntimeError('WorldObject not init')

        for key in WorldObject._type[object_type].keys():
            setattr(self, key, WorldObject._type[object_type][key])

        self.dirty = True
        self.pickable = False
        self._unique_id = random.random()

    def __eq__(self, other):
        return self.name == other.name


class World:

    def __init__(self, width, height):
        self._world = ilist([
            ilist([WorldObject('none') for _ in range(height)]) for __ in range(width)
        ])
        self.width = len(self._world)
        self.height = len(self._world[0])

    def __getitem__(self, idx):
        return self._world[idx]

    def in_width(self, low=0, high=-1):
        high = self.width if high == -1 else high
        return self.range(low, high, 'width')

    def in_height(self, low=0, high=-1):
        high = self.height if high == -1 else high
        return self.range(low, high, 'height')

    def range(self, low, high, dimention='width'):
        if low >= high:
            low, high = high, low

        return self.pointed_range(low, high, dimention)

    def build(self, x, y):
        self._world[x][y] = WorldObject('ground')

    def dig(self, x, y):
        if not self._world[x][y].solid:
            return

        self._world[x][y].health -= 1

        if self._world[x][y].health == 0:
            drop = self._world[x][y].name
            self._world[x][y] = WorldObject('air')
            self._world[x][y].pickable = True
            self._world[x][y].drop = drop

    def pick(self, x, y):
        if not self._world[x][y].pickable:
            return None

        name = self._world[x][y].drop
        self._world[x][y].pickable = False
        self._world[x][y].drop = None
        return name

    def pointed_range(self, low, high, dimention='width'):
        indecies = range(
            ceil_abs(max(min(low, high), 0)), 
            ceil_abs(min(max(low, high), getattr(self, dimention)))
        )
        if low >= high:
            indecies = reversed(indecies)
        return indecies
