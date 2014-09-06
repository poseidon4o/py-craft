from .world import WorldObject, World
from random import randint


def random_chance(chance):
    return randint(0, 100) < chance * 100


class WorldGenerator:

    """Generates world based on some hardcoded criteria.
    Expect many magic numbers.
    """

    air_to_ground = 0.45
    chance_for_mountain = 0.1

    chance_for_cave = 0.05
    cave_length = 20

    max_inclination = 2

    def __init__(self, width, height):
        self.world = World(width, height)

    def generate(self, callback=None):
        self._update_callback = callback
        self._ground()
        self._mountains()
        self._smooth_mountains()
        self._caves()
        return self.world

    def _hole_at(self, width, height):
        for w in self.world.in_width(width - self.max_inclination,
                                     width + self.max_inclination):
            self.world[w][height] = WorldObject('air')

        for h in self.world.in_height(height - self.max_inclination,
                                      height + self.max_inclination):
            self.world[width][h] = WorldObject('air')

    def _cave_at(self, width, height):
        for w in self.world.in_width(
                width,
                width + randint(self.cave_length, self.cave_length * 3)):
            height = min(height, self.world.height - 1)
            height = max(0, height)
            self._hole_at(w, height)
            height = height + randint(-1, 1)

    def _caves(self):
        for width in self.world.in_width():
            if random_chance(self.chance_for_cave):
                height = self.__ground_height(width)
                height = randint(
                    height + self.max_inclination * 2,
                    self.world.height
                )
                self._cave_at(width, height)
                if self._update_callback is not None:
                    self._update_callback(self.world)

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

    def __smooth_pass(self, direction=1):
        has_unsmoothness = False
        for_range = [
            range(0, self.world.width - 1),
            range(self.world.width - 1, 1, -1)
        ][direction % 2]

        step = [-1, 1][direction % 2]

        for width in for_range:
            diff = self.__inclination_diff(width, width + step)
            if diff > self.max_inclination:
                has_unsmoothness = True
                self.__smooth_part(diff, width)
        return has_unsmoothness

    def _smooth_mountains(self):
        max_passes = 100
        while self.__smooth_pass(max_passes) and max_passes > 0:
            if self._update_callback is not None:
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
    def generate_world(callback=None, dim=(1000, 300)):
        return WorldGenerator(*dim).generate(callback)
