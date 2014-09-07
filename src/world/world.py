from os import path
import json
import random
from ..utils import ilist, ceil_abs, Drawable, UiHelper


class WorldObject(Drawable):

    @classmethod
    def init(cls, resource_path):
        objects_file = open(path.join(resource_path, 'world_types.json'))
        cls.data = dict()

        for item in json.loads(objects_file.read()):
            cls.data[item['name']] = item

        objects_file.close()

    def __init__(self, object_type):
        if WorldObject.data is None:
            raise RuntimeError('WorldObject not init')

        super().__init__(None)
        for key in WorldObject.data[object_type].keys():
            setattr(self, key, WorldObject.data[object_type][key])
            if key == 'image' and self.image == ''\
                    and 'images' in WorldObject.data[object_type]:
                self.image = WorldObject.data[object_type]['images'][0]

        self.pickable = False

    def has_prop(self, name):
        return name in self.__dict__

    def get_key(self):
        return self.image if self.has_prop('image') else self.name

    def __eq__(self, other):
        return self.name == other.name


class World:

    def __init__(self, width, height):
        self._world = ilist([
            ilist([WorldObject('none') for _ in range(height)])
            for __ in range(width)
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

    def valid(self, x, y):
        return x >= 0 and x < self.width and y >= 0 and y < self.height

    def build(self, x, y, name):
        self._world[x][y] = WorldObject(name)
        self._world[x][y].sprite =\
            UiHelper.texture_map[self._world[x][y].get_key()]

    def dig(self, x, y):
        if not self._world[x][y].solid:
            return

        self._world[x][y].health -= 1

        if self._world[x][y].has_prop('images'):
            self._world[x][y].sprite =\
                UiHelper.texture_map[self._world[x][y].images[0]]

        self._world[x][y].dirty = True

        if self._world[x][y].health == 0:
            old = self._world[x][y]

            self._world[x][y] = WorldObject('air')
            self._world[x][y].sprite =\
                UiHelper.texture_map[self._world[x][y].get_key()]
            self._world[x][y].pickable = True

            if old.has_prop('images'):
                self._world[x][y].drop_sprite =\
                    UiHelper.texture_map[old.images[0]]
                self._world[x][y].drop = old.images[0]
            else:
                self._world[x][y].drop = old.get_key()
                self._world[x][y].drop_sprite = old.sprite

            self._world[x][y].drop_name = old.name

            del old

    def pick(self, x, y):
        if not self._world[x][y].pickable:
            return None

        picked = WorldObject(self._world[x][y].drop_name)
        picked.sprite = self._world[x][y].drop_sprite

        self._world[x][y].pickable = False
        self._world[x][y].drop = None
        return picked

    def tick(self):
        for w in self.in_width():
            for h in self.in_height(0, self.height - 1):
                if self._world[w][h].solid and not self._world[w][h-1].solid\
                        and self._world[w][h].has_prop('images'):
    
                    self._world[w][h].image = self._world[w][h].images[1]
                    self._world[w][h].sprite =\
                        UiHelper.texture_map[self._world[w][h].get_key()]

    def pointed_range(self, low, high, dimention='width'):
        indecies = range(
            ceil_abs(max(min(low, high), 0)),
            ceil_abs(min(max(low, high), getattr(self, dimention)))
        )
        if low >= high:
            indecies = reversed(indecies)
        return indecies
