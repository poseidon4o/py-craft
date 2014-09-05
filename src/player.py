from .world.world import World
from sdl2 import timer
from .utils import Coord, signof, ceil_abs

class Player:
    
    def __init__(self, world, sprite):
        self.position = Coord()

        self.dirty = True
        self.dirty_rect = (0, 0, 0, 0)

        self.sprite = sprite
        self.size = Coord(1, 2)
        self.speed = 2
        self.velocity = Coord(0, self.speed)

        self.world = world
        self.last_tick = timer.SDL_GetTicks()

        self.reposition()

    # position self at center of the world
    def reposition(self):
        self.position.pos = [self.world.width / 2, 10]
        self.tick()

    def tick(self):
        prev_pos = Coord(*self.position.pos)

        if not self.world[self.position.x][self.position.y + self.size.y].solid:
            self.velocity.y += 1
        elif self.world[self.position.x][self.position.y - 1].solid and self.velocity.y < 0:
            self.velocity.y = 0
        elif self.velocity.y > 0:
            self.velocity.y = 0

        x_direction = signof(self.velocity.x)

        for x in self.world.pointed_range(self.position.x + self.size.x * (x_direction == 1), self.position.x + ceil_abs(self.velocity.x) + self.size.x * (x_direction == 1)):
            solid = False
            for y in self.world.in_height(self.position.y, self.position.y + self.size.y):
                solid = self.world[x][y].solid or solid

            if not solid:
                step = x_direction if abs(self.velocity.x) >= 1 else self.velocity.x
                self.position.x += step
                self.velocity.x -= step
            else:
                self.velocity.x = 0
                break

        y_direction = signof(self.velocity.y)
        for y in self.world.pointed_range(self.position.y + self.size.y * (y_direction == 1), self.position.y + self.size.y * (y_direction == 1) + self.velocity.y):
            if not self.world[self.position.x][y].solid:
                self.position.y += 1 * y_direction

        if prev_pos != self.position:
            self.dirty = True
            self.dirty_rect = (
                min(prev_pos.x, self.position.x),
                min(prev_pos.y, self.position.y),
                max(prev_pos.x, self.position.x) + self.size.x,
                max(prev_pos.y, self.position.y) + self.size.y
            )
        else:
            self.dirty = False

    def jump(self):
        #no air jumping
        if not self.world[self.position[0]][self.position[1] + self.size[1]].solid:
            return

        self.velocity.y -= self.speed * 2

    def move(self, direction):
        self.velocity.x += direction * self.speed
