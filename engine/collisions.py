class Collidable:
    def is_colliding(self, c: Collidable):
        pass

class Rect:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h

    def __iter__(self):
        return [self.x, self.y, self.width, self.height]

    def __getitem__(self, item):
        return self.__iter__()[item]
