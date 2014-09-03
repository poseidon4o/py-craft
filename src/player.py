from .world.world import World
from sdl2 import timer


class Player:
    
    def __init__(self, world, sprite):
        self.sprite = sprite
        self.size = (1, 2)
        self.speed = 4

        self.world = world
        self.last_tick = timer.SDL_GetTicks()

        self.reposition()

    # position self at center of the world
    def reposition(self):
        self.position = [self.world.width // 2, 0]
        self.tick()

    def tick(self):
        if timer.SDL_GetTicks() - self.last_tick < 100:
            return

        self.last_tick = timer.SDL_GetTicks()

        for y in self.world.pointed_range(self.position[1] + self.size[1], self.position[1] + self.size[1] + int(self.speed * 0.5)):
            if not self.world[self.position[0]][y].solid:
                self.position[1] += 1

    def jump(self):
        #no air jumping
        if not self.world[self.position[0]][self.position[1] + self.size[1]].solid:
            return

        self.last_tick = timer.SDL_GetTicks()
        for y in self.world.pointed_range(self.position[1], self.position[1] + self.speed * 5):
            if not self.world[self.position[0]][y].solid:
                self.position[1] -= 1

    def move(self, disp):
        for x in self.world.pointed_range(self.position[0] + (disp == 1), self.position[0] + self.speed * disp):
            for y in range(self.size[1]):
                if self.world[x][self.position[1] + y].solid:
                    return
            self.position[0] += disp