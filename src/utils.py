import math


class Coord:

    def __init__(self, x=0, y=0):
        self.pos = [x, y]

    # support splat operator
    def __iter__(self):
        return iter(self.pos)

    @property
    def x(self):
        return self.pos[0]

    @x.setter
    def x(self, value):
        self.pos[0] = value

    @property
    def y(self):
        return self.pos[1]

    @y.setter
    def y(self, value):
        self.pos[1] = value

    def __getitem__(self, idx):
        return self.pos[idx]

    def __setitem__(self, idx, val):
        self.pos[idx] = val

    def __eq__(self, value):
        return self.x == value[0] and self.y == value[1]


def signof(x):
    return (x > 0) - (x < 0)


def ceil(x):
    return int(math.ceil(x))


def floor(x):
    return int(math.floor(x))


def ceil_abs(x):
    return ceil(x) if x > 0 else floor(x)


def bind_in_range(val, low, high):
    if val < low:
        val = low
    if val > high:
        val = high

    return int(val)


def to_rgb(r, g, b):
    return r << 16 | g << 8 | b


def point_in_rect(point, rect):
    """Rect will have upper-left and bottom-right points"""
    return point[0] >= rect[0] and point[0] <= rect[2] and\
        point[1] >= rect[1] and point[1] <= rect[3]


class ilist(list):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, idx):
        return super().__getitem__(int(idx))
