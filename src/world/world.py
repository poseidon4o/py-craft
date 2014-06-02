from os import path
import json

class WorldObject:
    type = None

    @classmethod
    def init(cls, resource_path):
        objects_file = open(path.join(resource_path, 'world_types.json'))
        cls.type = dict()

        for item in json.loads(objects_file.read()):
            cls.type[item['name']] = item

        objects_file.close()

    def __init__(self, object_type):
        if WorldObject.type is None:
            raise RuntimeError('WorldObject not init')
        self.type = WorldObject.type[object_type]

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
        if dimention == 'width':
            return range(max(0, low), min(self.width, high))
        else:
            return range(max(0, low), min(self.height, high))