import pygame, sys, os
from pygame.locals import *

from world.world_generator import WorldGenerator


def bind(val, top):
    if 0 <= val < top:
        return val

    return 0 if val < 0 else top-1


class Coord:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __mul__(self, mult):
        self.x *= mult
        self.y *= mult
        return self

    def toint(self):
        self.x = int(self.x)
        self.y = int(self.y)
        return self

class PyCraft:
    WIDTH = 800
    HEIGHT = 600
    BLOCK_SIZE = 4

    blocks_in_width = WIDTH // BLOCK_SIZE
    blocks_in_height = HEIGHT // BLOCK_SIZE

    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption('PyCraft')

        self.offset = Coord(0, 0)
        self.world = WorldGenerator.generate_world(self._update_callback)

        self._clear_color = pygame.Color('white')
        self._border_color = pygame.Color('black')
        self._update_colors()

    def _update_callback(self, world):
        self.world = world
        self._update_colors()
        self._clear()
        self._draw()

    def _update_colors(self):
        for x in range(self.world.width):
            for y in range(self.world.height):
                self.world[x][y].type['color'] = self.world[x][y].type['color']

    def _clear(self):
        self.window.fill(pygame.Color('white'))
                
    def _read_input(self):
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key in (K_UP, K_DOWN, K_LEFT, K_RIGHT):
                self.offset += {
                    K_UP: Coord(0, -self.BLOCK_SIZE),
                    K_DOWN: Coord(0, self.BLOCK_SIZE),
                    K_LEFT: Coord(-self.BLOCK_SIZE, 0),
                    K_RIGHT: Coord(self.BLOCK_SIZE, 0)
                }[event.key].toint() * 10

    def _draw(self):
        top_left = (
            bind(self.offset.x // self.BLOCK_SIZE, self.world.width),
            bind(self.offset.y // self.BLOCK_SIZE, self.world.height),
        )

        disposition = (
            bind(
                self.offset.x - top_left[0] * self.BLOCK_SIZE,
                self.world.width
            ),
            bind(
                self.offset.y - top_left[1] * self.BLOCK_SIZE,
                self.world.height
            )
        )

        w = 0
        h = 0

        rectangle = Rect(0, 0, self.BLOCK_SIZE, self.BLOCK_SIZE)

        for y in self.world.range(top_left[1],
                self.blocks_in_height + top_left[1], 'height'):
            w = 0   
            for x in self.world.range(top_left[0],
                    self.blocks_in_width + top_left[0]):

                pygame.draw.rect(
                    self.window,
                    self.world[x][y].type['color'],
                    rectangle.move(
                        self.BLOCK_SIZE * w,
                        self.BLOCK_SIZE * h
                    )
                )
                w += 1
            h += 1

        pygame.display.update()

    def start(self):
        ticker = pygame.time.Clock()

        while True:
            self._clear()
            self._read_input()
            self._draw()
            ticker.tick(60)


if __name__ == '__main__':
    game = PyCraft()
    game.start()