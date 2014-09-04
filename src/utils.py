

class Coord:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    @property
    def pos(self):
        return (self.x, self.y)

    @pos.setter
    def pos(self, value):
        self.x, self.y = value[0], value[1]

    def __getitem__(self, at):
        return self.pos[at]

    def __eq__(self, value):
        return self.x == value[0] and self.y == value[1]
        

def signof(x):
    return (x > 0) - (x < 0)

def bind_in_range(val, low, high):
    if val < low:
        val = low
    if val > high:
        val = high

    return int(val)