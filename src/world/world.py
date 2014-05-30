from random import randint
import sys

def random_chance(chance):
    return randint(0, 100) < chance * 100


class WorldObject:
    type = {
        'ground': {
            'color': (120, 60, 50),
            'id': 1
        },
        'air': {
            'color': (50, 120, 200),
            'id': 2
        },
        'none': {
            'color': (255, 0, 187),
            'id': -1
        }
    }

    def __init__(self, object_type):
        self.type = WorldObject.type[object_type]

    def __eq__(self, other):
        return self.type['id'] == other.type['id']


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


class WorldGenerator:
    """Generates world based on some hardcoded criteria.
    Expect many magic numbers.
    """

    air_to_ground = 0.45
    chance_for_mountain = 0.03

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.world = World(width, height)

    def generate(self):
        self._ground()
        self._mountains()
        self._caves()
        return self.world

    def _caves(self):
        pass

    def _ground(self):
        for width in self.world.in_width():
            for height in self.world.in_height():
                if height < self.air_to_ground * self.height:
                    self.world[width][height] = WorldObject('air')
                else:
                    self.world[width][height] = WorldObject('ground')

    def __ground_height(self, at):
        if at < 0:
            at = 0
        elif at >= self.width:
            at = self.width

        for cell in self.world.in_height():
            if self.world[at][cell] == WorldObject('ground'):
                return cell

    def __range(self, a, b):
        if a < b:
            return range(a, b)
        else:
            return range(b, a)

    def __set_ground_height(self, at, height):
        for height in self.world.in_height(height, self.__ground_height(at)):
            self.world[at][height] = WorldObject('ground')

    def _mountains(self):        
        last_mountain = -1000
        for col in self.world.in_width():
            if random_chance(self.chance_for_mountain):
                self._mountain_at(col)
                last_mountain = col

    def _mountain_at(self, at):
        mountain_width = 20
        up_slope = [c for c in range(at - mountain_width//2, at) if 0 < c < self.width]
        down_slope = [c for c in range(at, at + mountain_width//2) if 0 < c < self.width]

        for col in up_slope:
            prev_height = self.__ground_height(col-1)
            self.__set_ground_height(col, prev_height - randint(0, 3))

        for col in down_slope:
            prev_height = self.__ground_height(col-1)
            self.__set_ground_height(col, prev_height + randint(0, 3))

    @staticmethod
    def generate_world():
        return WorldGenerator(1000, 150).generate()
