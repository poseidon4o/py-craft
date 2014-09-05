import sys
from os import path

import sdl2.ext
from sdl2 import timer, surface, video, rect

from .utils import bind_in_range, Coord, point_in_rect, to_rgb
from .world.world_generator import WorldGenerator
from .world.world import WorldObject
from .player import Player

class PyCraft():
    WIDTH, HEIGHT = 1200, 800
    BLOCK_SIZE = 20

    DEBUG = False

    blocks_in_width = WIDTH // BLOCK_SIZE
    blocks_in_height = HEIGHT // BLOCK_SIZE

    move_padding = (
        WIDTH // (5 * BLOCK_SIZE),
        HEIGHT // (5 * BLOCK_SIZE)
    )


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
        
        self.offset = Coord(0, 0) # offset in world coordinates
        self.world = WorldGenerator.generate_world(None, (300, 100))
        
        sprite = self.sprite_factory.from_image(
            RESOURCES.get_path('player.png')
        )
        self.player = Player(self.world, sprite)


        self.dirty = True
        self.texture_map = {}
        self.loop()

    def loop(self):
        for row in self.world:
            for el in row:
                if el.name not in self.texture_map:
                    self.texture_map[el.name] = self.sprite_factory.from_color(
                        to_rgb(*el.color), 
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
      
    def world_to_screen(self, x, y):
        return (
            (x - self.offset.x) * self.BLOCK_SIZE,
            (y - self.offset.y) * self.BLOCK_SIZE
        )

    def mark_rect(self, world_rect):
        x1, y1 = list(map(int, self.world_to_screen(world_rect[0], world_rect[1])))
        x2, y2 = list(map(int, self.world_to_screen(world_rect[2], world_rect[3])))

        sdl2.ext.line(self.p_surface, 0xff0000, (x1, y1, x2, y1))
        sdl2.ext.line(self.p_surface, 0xff0000, (x2, y1, x2, y2))
        sdl2.ext.line(self.p_surface, 0xff0000, (x1, y1, x1, y2))
        sdl2.ext.line(self.p_surface, 0xff0000, (x1, y2, x2, y2))


    def update_area(self, world_rect):
        start_w = int(world_rect[0] - self.offset.x)
        start_h = int(world_rect[1] - self.offset.y)

        draw_rect = rect.SDL_Rect(0, 0, self.BLOCK_SIZE, self.BLOCK_SIZE)
        h = start_h
        for y in self.world.in_height(world_rect[1], world_rect[3]):
            w = start_w
            for x in self.world.in_width(world_rect[0], world_rect[2]):
        
                draw_rect.x = w * self.BLOCK_SIZE
                draw_rect.y = h * self.BLOCK_SIZE

                resp = sdl2.surface.SDL_BlitSurface(
                    self.texture_map[self.world[x][y].name].surface, 
                    None, self.c_surface, draw_rect
                )
                w += 1
            h += 1

        if self.DEBUG:
            self.mark_rect(world_rect)


    def draw(self):
        if not self.dirty and not self.player.dirty:
            return

        if self.player.dirty and not self.dirty:
            from_height, to_height =\
                self.player.dirty_rect[1], self.player.dirty_rect[3]
            from_width, to_width =\
                self.player.dirty_rect[0], self.player.dirty_rect[2]

            start_w = int(from_width - self.offset.x)
            start_h = int(from_height - self.offset.y)
        else:
            self.dirty = False
            sdl2.ext.fill(self.p_surface, 0x000000)
            from_height, to_height =\
                self.offset[1], self.offset[1] + self.blocks_in_height
            from_width, to_width =\
                self.offset[0], self.offset[0] + self.blocks_in_width

            start_w, start_h = 0, 0

        self.update_area((
            from_width, from_height,
            to_width, to_height
        ))
     
        if self.player.dirty or self.dirty:
            self.draw_player()

    def draw_player(self):
        screen_pos = list(map(int, self.world_to_screen(*self.player.position.pos)))

        draw_rect = rect.SDL_Rect(
            screen_pos[0], screen_pos[1],
            self.BLOCK_SIZE, self.BLOCK_SIZE
        )
        
        sdl2.surface.SDL_BlitSurface(
            self.player.sprite.surface, None,
            self.c_surface, draw_rect
        )

    def focus_player(self):
        no_move_rect = (
            self.offset.x + self.move_padding[0],
            self.offset.y + self.move_padding[1],
            self.offset.x + self.blocks_in_width - self.move_padding[0],
            self.offset.y + self.blocks_in_height - self.move_padding[1]
        )

        if not point_in_rect(self.player.position.pos, no_move_rect):
            self.dirty = True

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



