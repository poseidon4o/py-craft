from collections import defaultdict

from .world.world import World
from sdl2 import timer
from .utils import Coord, signof, ceil_abs, point_in_rect


class Player:

    def __init__(self, world, sprite):
        self.inventory = {
            'ground': 0
        }

        self.position = Coord()

        self.dirty = True
        self.dirty_rect = (0, 0, 0, 0)

        self.sprite = sprite
        self.size = Coord(1, 2)
        self.range = Coord(2, 2)

        self.auto_jump = False
        self.speed = 1
        self.velocity = Coord(0, self.speed)

        self.world = world
        self.last_tick = timer.SDL_GetTicks()

        self.reposition()
        self.inventory_string = ''
        self.update_inventory_string()

    def update_inventory_string(self):
        new_str = ''.join(
            [str(key) + ':' + str(value) + ' '
             for key, value in self.inventory.items()]
        )
        
        if new_str != self.inventory_string:
            self.inventory_string = new_str
            self.dirty = True

    # position self at center of the world
    def reposition(self):
        self.position.pos = [self.world.width / 2, 10]
        self.tick()

    def under_me(self, x, y):
        return point_in_rect(
            (x, y), (
                self.position.x,
                self.position.y,
                self.position.x + self.size.x - 1,
                self.position.y + self.size.y - 1
            )
        )

    def in_range(self, x, y):
        return point_in_rect(
            (x, y),
            (
                self.position.x - self.range.x,
                self.position.y - self.range.y,
                self.position.x + self.range.x,
                self.position.y + self.range.y
            )
        ) and not self.under_me(x, y)

    def action(self, x, y):
        x, y = int(x), int(y)
        if not self.in_range(x, y):
            return


        if self.world[x][y].solid:
            self.world.dig(x, y)
        else:
            if self.inventory['ground'] > 0:
                self.inventory['ground'] -= 1
                self.world.build(x, y)

        self.update_inventory_string()
        self.dirty = True
        self.world[x][y].dirty = True

    def pick(self):
        for x in self.world.in_width(self.position.x,
                                     self.position.x + self.size.x):
            for y in self.world.in_height(self.position.y,
                                          self.position.y + self.size.y):
                pick = self.world.pick(x, y)
                self.world[x][y].dirty = True
                if pick:
                    self.inventory[pick] += 1
                    self.update_inventory_string()

    def tick(self):
        self.pick()

        now = timer.SDL_GetTicks()
        if now - self.last_tick <= 33:
            return
        self.last_tick = now

        prev_pos = Coord(*self.position.pos)

        if self.world.valid(self.position.x, self.position.y + self.size.y)\
            and not self.world[self.position.x][self.position.y + self.size.y]\
                .solid:
            self.velocity.y += 1
        elif self.world.valid(self.position.x, self.position.y - 1) and\
            self.world[self.position.x][self.position.y - 1].solid and\
                self.velocity.y < 0:
            self.velocity.y = 0
        elif self.velocity.y > 0:
            self.velocity.y = 0

        x_direction = signof(self.velocity.x)

        for x in self.world.pointed_range(
                self.position.x + self.size.x * (x_direction == 1),
                self.position.x + ceil_abs(self.velocity.x)
                + self.size.x * (x_direction == 1)):
            solid = False
            for y in self.world.in_height(self.position.y,
                                          self.position.y + self.size.y):
                solid = self.world[x][y].solid or solid

            if not solid:
                step = x_direction if abs(self.velocity.x) >= 1\
                    else self.velocity.x
                self.position.x += step
                self.velocity.x -= step
                self.pick()
            else:
                self.velocity.x = 0
                if self.auto_jump:
                    self.jump()
                break

        y_direction = signof(self.velocity.y)
        for y in self.world.pointed_range(
                self.position.y + self.size.y * (y_direction == 1),
                self.position.y + self.size.y * (y_direction == 1)
                + self.velocity.y):
            if not self.world[self.position.x][y].solid:
                self.position.y += 1 * y_direction
                self.pick()
            else:
                if self.velocity.y < 0:
                    self.velocity.y = 0
                break

        if prev_pos != self.position:
            self.dirty = True
            for x in self.world.in_width(min(prev_pos.x, self.position.x),
                                         max(prev_pos.x, self.position.x)
                                         + self.size.x):
                for y in self.world.in_height(min(prev_pos.y, self.position.y),
                                              max(prev_pos.y, self.position.y)
                                              + self.size.y):
                    self.world[x][y].dirty = True

    def jump(self):
        # no air jumping
        if not self.world[self.position[0]][self.position[1] + self.size[1]]\
                .solid:
            return

        self.velocity.y -= self.speed * 4

    def move(self, direction):
        self.velocity.x += direction * self.speed
