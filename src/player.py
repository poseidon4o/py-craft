from collections import OrderedDict

from .world.world import World
import sdl2
from .utils import Coord, signof, ceil_abs, point_in_rect, Drawable, UiHelper,\
                   to_rgb


class InventoryItem(Drawable):

    def __init__(self, world_object):
        if world_object.has_prop('images'):
            sprite = UiHelper.texture_map[world_object.images[0]]
        else:
            sprite = world_object.sprite
        super().__init__(sprite)
        self.qty = 1
    
    def draw(self, surface, x, y):
        super().draw(surface, x, y)

        qty_texture = UiHelper.sprite_factory.from_text(
            str(self.qty), fontmanager=UiHelper.font_manager
        )

        super().draw(surface, x, y, sprite=qty_texture)


class Inventory(Drawable):

    def __init__(self):
        super().__init__(None)
        self.padding = 5
        self.size = UiHelper.BLOCK_SIZE
        self.height = self.size + self.padding * 2

        self.selected_index = None
        self.selection_sprite = UiHelper.sprite_factory.from_color(
            to_rgb(255, 0, 0),
            (self.height, self.height)
        )

        self.width = 0
        self.slots = OrderedDict()
        self.last_pos = [
            0, 0, 0
        ]

    def __getitem__(self, name):
        if name in self.slots:
            return self.slots[name]
        else:
            None

    def action(self, x, y):
        if point_in_rect((x, y), (
                    self.last_pos[0], self.last_pos[1],
                    self.last_pos[0] + self.last_pos[2],
                    self.last_pos[1] + self.height
                )
            ):
            self.selected_index = (x - self.last_pos[0]) // self.height
            self.dirty = True


    def selected(self):
        if self.selected_index is not None:
            return list(self.slots.keys())[self.selected_index]
        else:
            return None

        
    def add(self, world_object):
        self.dirty = True
        if world_object.name in self.slots:
            self.slots[world_object.name].qty += 1
        else:
            self.slots[world_object.name] = InventoryItem(world_object)

    def remove(self, name):
        self.dirty = True
        self.slots[name].qty -= 1
        if self.slots[name].qty == 0:
            del self.slots[name]
            self.selected_index = None

    def update(self):
        if len(self.slots) == 0:
            self.width = 0
            return False

        if self.dirty:
            self.width = len(self.slots) * self.size +\
                (len(self.slots) + 1) * self.padding
            del self.sprite
            self.sprite = UiHelper.sprite_factory.from_color(
                to_rgb(0, 0, 0),
                (self.width, self.height)
            )
        self.dirty = False
        return True

    def draw(self, surface, x, y):
        if not self.update():
            return

        self.last_pos = [x, y, self.width]

        super().draw(surface, x, y)
        y += self.padding
        for index, item in enumerate(self.slots.values()):
            if self.selected_index == index:
                super().draw(
                    surface, x, y - self.padding, sprite=self.selection_sprite
                )
            x += self.padding
            item.draw(surface, x, y)
            x += self.size


class Player(Drawable):

    def __init__(self, world, sprite):
        super().__init__(sprite)


        self.position = Coord()

        self.size = Coord(1, 2)

        self.inventory = Inventory()
        self.range = Coord(3, 3)

        self.auto_jump = False
        self.speed = 1
        self.velocity = Coord(0, self.speed)

        self.world = world
        self.last_tick = sdl2.timer.SDL_GetTicks()

        self.position.pos = [self.world.width // 2, 0]
        self.tick()

    def check_dirty(self):
        self.dirty = self.dirty or self.inventory.dirty

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
            if self.inventory.selected():
                self.inventory.remove(self.inventory.selected())
                self.world.build(x, y, self.inventory.selected())

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
                    self.inventory.add(pick)

    def tick(self):
        self.pick()
        self.inventory.update()

        now = sdl2.timer.SDL_GetTicks()
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
        
        self.check_dirty()

    def jump(self):
        # no air jumping
        if not self.world[self.position[0]][self.position[1] + self.size[1]]\
                .solid:
            return

        self.velocity.y -= self.speed * 3

    def move(self, direction):
        self.velocity.x += direction * self.speed
