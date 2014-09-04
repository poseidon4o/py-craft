import sys
from os import path

import sdl2.ext
from sdl2 import timer, surface, video, rect

from .utils import bind_in_range
from .world.world_generator import WorldGenerator
from .world.world import WorldObject
from .player import Player

class PyCraft():
    WIDTH, HEIGHT = 1200, 800
    BLOCK_SIZE = 20

    blocks_in_width = WIDTH // BLOCK_SIZE
    blocks_in_height = HEIGHT // BLOCK_SIZE


    def __init__(self, RESOURCE_DIR):
        WorldObject.init(RESOURCE_DIR)
        sdl2.ext.init()


        self.window = sdl2.ext.Window("Py-craft", 
                                      size=(self.WIDTH, self.HEIGHT))
        self.window.show();

        self.p_surface = self.window.get_surface()
        self.c_surface = video.SDL_GetWindowSurface(self.window.window)
        
        self.sprite_factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
        self.sprite_renderer = self.sprite_factory\
                                   .create_sprite_render_system(self.window)

        RESOURCES = sdl2.ext.Resources(RESOURCE_DIR)
        
        self.offset = [0, 0]
        self.world = WorldGenerator.generate_world(None, (300, 50))
        
        sprite = self.sprite_factory.from_image(
            RESOURCES.get_path('player.png')
        )
        self.player = Player(self.world, sprite)

        self.color_map = {}
        self.loop()

    def loop(self):
        for row in self.world:
            for el in row:
                if el.name not in self.color_map:
                    self.color_map[el.name] = self.sprite_factory.from_color(
                        self._to_rgb(*el.color), 
                        (self.BLOCK_SIZE, self.BLOCK_SIZE)
                    )

        last_tick = timer.SDL_GetTicks()
        avg_time = 0
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
                print(avg_time)

            avg_time = 0.75 * avg_time + 0.25 * (now - start)

            timer.SDL_Delay(1000 // 60)

    def _to_rgb(self, r, g, b):
        return r << 16 | g << 8 | b

    def draw(self):
        sdl2.ext.fill(self.p_surface, 0x000000)
        
        from_height, to_height =\
            self.offset[1], self.offset[1] + self.blocks_in_height
        from_width, to_width =\
            self.offset[0], self.offset[0] + self.blocks_in_width
        
        player_pos = None
        draw_rect = rect.SDL_Rect(0, 0, self.BLOCK_SIZE, self.BLOCK_SIZE)
        h = 0
        for y in self.world.in_height(from_height, to_height):
            w = 0
            for x in self.world.in_width(from_width, to_width):
        
                draw_rect.x = w * self.BLOCK_SIZE
                draw_rect.y = h * self.BLOCK_SIZE

                sdl2.surface.SDL_BlitSurface(
                    self.color_map[self.world[x][y].name].surface, 
                    None, self.c_surface, draw_rect
                )
                
                if [x, y] == self.player.position:
                    player_pos = (w * self.BLOCK_SIZE, h * self.BLOCK_SIZE)
                    
                w += 1
            h += 1       

        if player_pos:
            draw_rect.x = player_pos[0]
            draw_rect.y = player_pos[1]

            sdl2.surface.SDL_BlitSurface(
                self.player.sprite.surface, None,
                self.c_surface, draw_rect
            )


    def focus_player(self):
        self.offset[0] = bind_in_range(
            self.player.position.x - self.blocks_in_width // 2,
            0, self.world.width - self.blocks_in_width)

        self.offset[1] = bind_in_range(
            self.player.position.y - self.blocks_in_width // 2,
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
                
        self.player.position.x = bind_in_range(self.player.position.x,
            0, self.world.width)
        self.player.position.y = bind_in_range(self.player.position.y,
            0, self.world.height)



