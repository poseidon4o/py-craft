import sys

import sdl2.ext
from sdl2 import timer

from .utils import bind_in_range
from .world.world_generator import WorldGenerator
from .world.world import WorldObject
from .player import Player

class PyCraft():
    WIDTH, HEIGHT = 1200, 800
    BLOCK_SIZE = 40

    blocks_in_width = WIDTH // BLOCK_SIZE
    blocks_in_height = HEIGHT // BLOCK_SIZE


    def __init__(self, RESOURCE_DIR):
        WorldObject.init(RESOURCE_DIR)
        sdl2.ext.init()

        self.window = sdl2.ext.Window("Py-craft", 
                                       size=(self.WIDTH, self.HEIGHT))
        self.window.show();
        self.surface = self.window.get_surface()
        self.world = WorldGenerator.generate_world(None, (300, 50))

        self.offset = [0, 0]
        
        self.player = Player(self.world)

        self.color_map = {}
        self.loop()

    def loop(self):
        for row in self.world:
            for el in row:
                if el.name not in self.color_map:
                    self.color_map[el.name] = self._to_rgb(*el.color)
                    # self.color_map[el.name] = sdl2.ext.Color(*el.color)

        last_tick = timer.SDL_GetTicks()
        while True:
            start = timer.SDL_GetTicks()

            if self.events():
                return

            self.player.tick()
            self.focus_player()
            self.draw()
            self.window.refresh()

            now = timer.SDL_GetTicks()
            if now - last_tick > 1000:
                last_tick = now
                print(now - start)

            timer.SDL_Delay(1000 // 60)

    def _to_rgb(self, r, g, b):
        return r << 16 | g << 8 | b

    def draw(self):
        sdl2.ext.fill(self.surface, 0x000000)
        
        from_height, to_height =\
            self.offset[1], self.offset[1] + self.blocks_in_height
        from_width, to_width =\
            self.offset[0], self.offset[0] + self.blocks_in_width
        
        player_pos = (-10, -10)
        h = 0
        for y in self.world.in_height(from_height, to_height):
            w = 0
            for x in self.world.in_width(from_width, to_width):
        
                sdl2.ext.fill(
                    self.surface,
                    self.color_map[self.world[x][y].name],
                    (
                        w * self.BLOCK_SIZE,
                        h * self.BLOCK_SIZE,
                        self.BLOCK_SIZE, self.BLOCK_SIZE
                    )
                )
                if [x, y] == self.player.position:
                    player_pos = (w * self.BLOCK_SIZE, h * self.BLOCK_SIZE)
                    
                w += 1
            h += 1       

        sdl2.ext.fill(self.surface, sdl2.ext.Color(255, 0, 0), (
            player_pos[0], player_pos[1],
            self.player.size[0] * self.BLOCK_SIZE,
            self.player.size[1] * self.BLOCK_SIZE            
        ))

    def focus_player(self):
        self.offset[0] = bind_in_range(
            self.player.position[0] - self.blocks_in_width // 2,
            0, self.world.width - self.blocks_in_width)

        self.offset[1] = bind_in_range(
            self.player.position[1] - self.blocks_in_width // 2,
            0, self.world.width - self.blocks_in_height)

    def events(self):
        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_QUIT or event.type == sdl2.SDL_KEYDOWN\
                and event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                return True
            if event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_LEFT:
                    self.player.move(-1)
                elif event.key.keysym.sym == sdl2.SDLK_RIGHT:
                    self.player.move(1)
                elif event.key.keysym.sym == sdl2.SDLK_SPACE:
                    self.player.jump()
                

        self.player.position[0] = bind_in_range(self.player.position[0],
            0, self.world.width)
        self.player.position[1] = bind_in_range(self.player.position[1],
            0, self.world.height)



