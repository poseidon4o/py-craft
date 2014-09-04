from .world.world import World
from sdl2 import timer
from .utils import Coord, signof

class Player:
    
    def __init__(self, world, sprite):
        self.position = Coord()

        self.sprite = sprite
        self.size = Coord(1, 2)
        self.speed = 2
        self.velocity = Coord(0, self.speed)

        self.world = world
        self.last_tick = timer.SDL_GetTicks()

        self.reposition()

    # position self at center of the world
    def reposition(self):
        self.position.pos = [self.world.width // 2, 10]
        self.tick()

    def tick(self):
        if self.world[self.position.x][self.position.y + self.size.y].solid and self.velocity.y > 0:
            self.velocity.y = 0
        else:
            self.velocity.y += 1


        x_direction = signof(self.velocity.x)

        for x in self.world.pointed_range(self.position.x + self.size.x * (x_direction == 1), self.position.x + int(self.velocity.x) + self.size.x * (x_direction == 1)):
            solid = False
            for y in self.world.in_height(self.position.y, self.position.y + self.size.y):
                solid = self.world[x][y].solid or solid

            if not solid:
                self.position.x += 1 * x_direction
                self.velocity.x -= 1 * x_direction
            else:
                self.velocity.x = 0
                break

        y_direction = signof(self.velocity.y)
        for y in self.world.pointed_range(self.position.y + self.size.y * (y_direction == 1), self.position.y + self.size.y * (y_direction == 1) + int(self.velocity.y)):
            if not self.world[self.position.x][y].solid:
                self.position.y += 1 * y_direction

    def jump(self):
        #no air jumping
        if not self.world[self.position[0]][self.position[1] + self.size[1]].solid:
            return

        self.velocity.y -= self.speed * 2

    def move(self, direction):
        self.velocity.x += direction * self.speed
