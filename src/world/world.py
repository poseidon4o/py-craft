from os import path
import json
import random

class WorldObject:
    type = None

    @classmethod
    def init(cls, resource_path):
        objects_file = open(path.join(resource_path, 'world_types.json'))
        cls.type = dict()

        for item in json.loads(objects_file.read()):
            cls._type[item['name']] = item

        objects_file.close()

    def __init__(self, object_type):
        if WorldObject.type is None:
            raise RuntimeError('WorldObject not init')

        for key in WorldObject.type[object_type].keys():
            setattr(self, key, WorldObject.type[object_type][key])

        self._unique_id = random.random()

    def __eq__(self, other):
        return self.type['name'] == other.type['name']


class World:

    def __init__(self, width, height):
        self._world = [
            [WorldObject('none') for _ in range(height)] for __ in range(width)
        ]
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

    def pointed_range(self, low, high, dimention='width'):
        indecies = range(max(min(low, high), 0), min(max(low, high), getattr(self, dimention)))
        if low >= high:
            indecies = reversed(indecies)
        return indecies
