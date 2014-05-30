class WorldObject:
    type = {
        'ground': {
            'color': (120, 60, 50),
            'id': 1
        },
        'air': {
            'color': (50, 120, 200),
            'id': 2
        },
        'none': {
            'color': (255, 0, 187),
            'id': -1
        }
    }

    def __init__(self, object_type):
        self.type = WorldObject.type[object_type]

    def __eq__(self, other):
        return self.type['id'] == other.type['id']


class World:

    def __init__(self, width, height):
        self._world = [
            [WorldObject('none') for _ in range(height)] for __ in range(width)
        ]
        self.width = len(self._world)
        self.height = len(self._world[0])

    def __getitem__(self, idx):
        return self._world[idx]

    def in_width(self, low=0, high=-1):
        high = self.width if high == -1 else high
        return self.range(low, high, 'width')

    def in_height(self, low=0, high=-1):
        high = self.height if high == -1 else high
        return self.range(low, high, 'height')

    def range(self, low, high, dimention='width'):
        if low >= high:
            low, high = high, low
        if dimention == 'width':
            return range(max(0, low), min(self.width, high))
        else:
            return range(max(0, low), min(self.height, high))