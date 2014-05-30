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
    chance_for_mountain = 0.1
    max_inclination = 3

    def __init__(self, width, height):
        self.world = World(width, height)

    def generate(self, callback=None):
        self._update_callback = callback
        self._ground()
        self._mountains()
        self._smooth_mountains()
        self._caves()
        return self.world

    def _caves(self):
        pass

    def _ground(self):
        for width in self.world.in_width():
            for height in self.world.in_height():
                if height < self.air_to_ground * self.world.height:
                    self.world[width][height] = WorldObject('air')
                else:
                    self.world[width][height] = WorldObject('ground')

    def __ground_height(self, at):
        if at < 0:
            at = 0
        elif at >= self.world.width:
            at = self.world.width - 1

        for cell in self.world.in_height():
            if self.world[at][cell] == WorldObject('ground'):
                return cell
        return 0

    def __inclination_diff(self, a, b):
        return abs(self.__ground_height(a) - self.__ground_height(b))

    def __set_ground_height(self, at, height):
        for h in self.world.in_height():
            if h < height:
                self.world[at][h] = WorldObject('air')
            else:
                self.world[at][h] = WorldObject('ground')

    def _mountains(self):
        last_mountain = -1000
        for col in self.world.in_width():
            if random_chance(self.chance_for_mountain):
                self._mountain_at(col)
                last_mountain = col

    def __smooth_part(self, diff, at):
        left, right = self.__ground_height(at), self.__ground_height(at + 1)

        if left < right:
            self.__set_ground_height(at, left + diff // 2)
            self.__set_ground_height(at, right - diff // 2)
        else:
            self.__set_ground_height(at, left - diff // 2)
            self.__set_ground_height(at, right + diff // 2)

    def __smooth_pass(self):
        has_unsmoothness = False
        for width in self.world.in_width(0, self.world.width - 1):
            diff = self.__inclination_diff(width, width + 1)
            if diff > self.max_inclination:
                has_unsmoothness = True
                self.__smooth_part(diff, width)
        return has_unsmoothness

    def _smooth_mountains(self):
        max_passes = 100
        while self.__smooth_pass() and max_passes > 0:
            if self._update_callback != None:
                self._update_callback(self.world)
            max_passes -= 1

    def _mountain_at(self, at):
        mountain_width = 20
        up_slope = [c for c in range(at - mountain_width // 2, at) 
                    if 0 < c < self.world.width]
        down_slope = [c for c in range(at, at + mountain_width // 2) 
                      if 0 < c < self.world.width]

        for col in up_slope:
            prev_height = self.__ground_height(col - 1)
            self.__set_ground_height(
                col, 
                prev_height - randint(
                    -self.max_inclination // 2,
                    self.max_inclination
                )
            )

        for col in down_slope:
            prev_height = self.__ground_height(col - 1)
            self.__set_ground_height(
                col,
                prev_height + randint(
                    -self.max_inclination // 2,
                    self.max_inclination
                )
            )

    @staticmethod
    def generate_world(callback=None):
        return WorldGenerator(1000, 300).generate(callback)
