import sys
from os import path

import sdl2.ext
from sdl2 import timer, surface, video, rect

from .utils import bind_in_range, Coord, point_in_rect, to_rgb
from .world.world_generator import WorldGenerator
from .world.world import WorldObject
from .player import Player


class PyCraft():
    WIDTH, HEIGHT = 1300, 700
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
        self.RESOURCES = sdl2.ext.Resources(RESOURCE_DIR)
        sdl2.ext.init()

        self.window = sdl2.ext.Window("Py-craft",
                                      size=(self.WIDTH, self.HEIGHT))
        self.window.show()

        self.p_surface = self.window.get_surface()
        self.c_surface = video.SDL_GetWindowSurface(self.window.window)

        self.font_manager = sdl2.ext.FontManager(
            self.RESOURCES.get_path('helvetica.ttf')
        )
        self.sprite_factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
        self.sprite_renderer = self.sprite_factory\
                                   .create_sprite_render_system(self.window)

        self.offset = Coord(0, 0)  # offset in world coordinates
        self.world = WorldGenerator.generate_world(None, (100, 100))

        self.dirty = True
        self.texture_map = {}
        
        sprite = self.sprite_factory.from_image(
            self.RESOURCES.get_path('player.png')
        )
        self.player = Player(self.world, sprite)

        self.init()
        self.loop()

    def init(self):

        for row in self.world:
            for el in row:
                if el.name not in self.texture_map:
                    if 'image' in el.__dict__:
                        self.texture_map[el.name] = self.sprite_factory.from_image(
                            self.RESOURCES.get_path(el.image)
                        )
                    else:
                        self.texture_map[el.name] = self.sprite_factory.from_color(
                            to_rgb(*el.color),
                            (self.BLOCK_SIZE, self.BLOCK_SIZE)
                        )
        

    def loop(self):

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
                print(int(avg_time))

            avg_time = 0.75 * avg_time + 0.25 * (now - start)

            timer.SDL_Delay(1000 // 60)

    def world_to_screen(self, x, y):
        return (
            (x - self.offset.x) * self.BLOCK_SIZE,
            (y - self.offset.y) * self.BLOCK_SIZE
        )

    def screen_to_world(self, x, y):
        return (
            x / self.BLOCK_SIZE + self.offset.x,
            y / self.BLOCK_SIZE + self.offset.y
        )

    def mark_rect(self, world_rect):
        x1, y1 = list(
            map(int, self.world_to_screen(world_rect[0], world_rect[1]))
        )
        x2, y2 = list(
            map(int, self.world_to_screen(world_rect[2], world_rect[3]))
        )
        x2, y2 = x2 - 1, y2 - 1
        sdl2.ext.line(self.p_surface, 0xff0000, (x1, y1, x2, y1))
        sdl2.ext.line(self.p_surface, 0xff0000, (x2, y1, x2, y2))
        sdl2.ext.line(self.p_surface, 0xff0000, (x1, y1, x1, y2))
        sdl2.ext.line(self.p_surface, 0xff0000, (x1, y2, x2, y2))

    def update_screen(self):

        draw_rect = rect.SDL_Rect(0, 0, 0, 0)
        h = 0
        for y in self.world.in_height(self.offset.y,
                                      self.offset.y + self.blocks_in_height):
            w = 0
            for x in self.world.in_width(self.offset.x,
                                         self.offset.x + self.blocks_in_width):
                if not self.world[x][y].dirty and not self.dirty:
                    w += 1
                    continue

                draw_rect.x = w * self.BLOCK_SIZE
                draw_rect.y = h * self.BLOCK_SIZE

                sdl2.surface.SDL_BlitSurface(
                    self.texture_map[self.world[x][y].name].surface,
                    None, self.c_surface, draw_rect
                )

                if self.world[x][y].pickable:
                    draw_rect.x += self.BLOCK_SIZE // 5
                    draw_rect.y += self.BLOCK_SIZE // 5

                    sdl2.surface.SDL_BlitSurface(
                        self.texture_map[self.world[x][y].drop].surface,
                        rect.SDL_Rect(
                            0, 0,
                            self.BLOCK_SIZE // 2, self.BLOCK_SIZE // 2
                        ),
                        self.c_surface, draw_rect
                    )

                if self.world[x][y].dirty and self.DEBUG:
                    self.mark_rect((x, y, x + 1, y + 1))

                self.world[x][y].dirty = False

                w += 1
            h += 1

    def draw(self):
        if not self.dirty and not self.player.dirty:
            return

        self.update_screen()

        if self.player.dirty or self.dirty:
            self.draw_player()

        self.dirty = False

    def draw_player(self):
        self.player.dirty = False
        screen_pos = list(
            map(int, self.world_to_screen(*self.player.position.pos))
        )

        draw_rect = rect.SDL_Rect(
            screen_pos[0], screen_pos[1],
            self.BLOCK_SIZE, self.BLOCK_SIZE
        )

        sdl2.surface.SDL_BlitSurface(
            self.player.sprite.surface, None,
            self.c_surface, draw_rect
        )

        draw_rect.x = draw_rect.y = 0

        inventory_texture = self.sprite_factory.from_text(
            self.player.inventory_string,
            fontmanager=self.font_manager
        )

        for x in self.world.in_width(self.offset.x, self.offset.x + inventory_texture.size[0] // self.BLOCK_SIZE + 1):
            self.world[x][self.offset.y].dirty = True

        sdl2.surface.SDL_BlitSurface(
            inventory_texture.surface, None,
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
                self.player.position.y - self.blocks_in_height // 2,
                0, self.world.width - self.blocks_in_height)

    def events(self):
        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_QUIT or event.type == sdl2.SDL_KEYDOWN\
                    and event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                return True
            elif event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym in (sdl2.SDLK_LEFT, sdl2.SDLK_a):
                    self.player.move(-1)
                elif event.key.keysym.sym in (sdl2.SDLK_RIGHT, sdl2.SDLK_d):
                    self.player.move(1)
                elif event.key.keysym.sym in (sdl2.SDLK_SPACE, sdl2.SDLK_w):
                    self.player.jump()
            elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                x, y = self.screen_to_world(event.button.x, event.button.y)
                self.player.action(x, y)
