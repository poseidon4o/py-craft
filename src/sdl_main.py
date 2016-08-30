import sys
from os import path, name as OS_NAME

import sdl2.ext
from sdl2 import timer, surface, video, rect

from .utils import bind_in_range, Coord, point_in_rect, to_rgb, UiHelper
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

        UiHelper.font_manager = self.font_manager = sdl2.ext.FontManager(
            self.RESOURCES.get_path('helvetica-neue-bold.ttf')
        )

        UiHelper.sprite_factory = self.sprite_factory =\
            sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)

        UiHelper.BLOCK_SIZE = self.BLOCK_SIZE

        self.offset = Coord(0, 0)  # offset in world coordinates
        self.world = WorldGenerator.generate_world(None, (100, 100))

        self.dirty = True
        UiHelper.texture_map = {}

        sprite = self.sprite_factory.from_image(
            self.RESOURCES.get_path('player.png')
        )
        self.player = Player(self.world, sprite)

        self.init()
        self.world.tick()
        self.loop()

    def init(self):
        for row in self.world:
            for el in row:
                key = el.get_key()
                if key not in UiHelper.texture_map:
                    if el.has_prop('image'):
                        el.sprite = UiHelper.texture_map[key] =\
                            self.sprite_factory.from_image(
                                self.RESOURCES.get_path(el.image)
                            )
                    else:
                        el.sprite = UiHelper.texture_map[key] =\
                            self.sprite_factory.from_color(
                                to_rgb(*el.color),
                                (self.BLOCK_SIZE, self.BLOCK_SIZE)
                            )
                    if el.has_prop('images'):
                        for img in el.images:
                            UiHelper.texture_map[img] =\
                                self.sprite_factory.from_image(
                                    self.RESOURCES.get_path(img)
                                )
                else:
                    el.sprite = UiHelper.texture_map[key]

    def loop(self):

        last_tick = timer.SDL_GetTicks()
        avg_time = 0
        while True:
            start = timer.SDL_GetTicks()

            if self.events():
                return

            self.player.tick()
            # self.world.tick() # optimize to be called on every frame
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
                    self.world[x][y].sprite.surface,
                    None, self.c_surface, draw_rect
                )

                if self.world[x][y].pickable:
                    draw_rect.x += self.BLOCK_SIZE // 5
                    draw_rect.y += self.BLOCK_SIZE // 5

                    sdl2.surface.SDL_BlitSurface(
                        self.world[x][y].drop_sprite.surface,
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
        self.draw_player()

        self.dirty = False

    def draw_player(self):
        screen_pos = list(
            map(int, self.world_to_screen(*self.player.position.pos))
        )

        self.player.draw(self.c_surface, *screen_pos)

        was_dirty = self.player.inventory.dirty
        self.player.inventory.update()
        was_dirty = was_dirty or self.player.inventory.dirty
        screen_pos = (
            self.WIDTH // 2 - self.player.inventory.width // 2,
            0
        )

        self.player.inventory.draw(self.c_surface, *screen_pos)
        if was_dirty:
            from_pos = list(self.screen_to_world(*screen_pos))
            from_pos[0] -= 2
            to_pos = list(self.screen_to_world(
                screen_pos[0] + self.player.inventory.width,
                self.player.inventory.height
            ))
            to_pos[0] += 1
            for x in self.world.in_width(from_pos[0], to_pos[0]):
                for y in self.world.in_height(from_pos[1], to_pos[1]):
                    self.world[x][y].dirty = True

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
                self.player.inventory.action(
                    event.button.x,
                    event.button.y
                )
                self.player.check_dirty()
