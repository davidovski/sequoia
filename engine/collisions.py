class Collidable:
    def is_colliding(self, c):
        return True

    def adjust_pos(self, x, y):
        return self


class MultiCollidable(Collidable):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.collisions = []

    def add_collision(self, c: Collidable):
        self.collisions.append(c)

    def is_colliding(self, c: Collidable):
        return True in [c.is_colliding(col.adjust_pos(self.x, self.y)) for col in self.collisions]

    def adjust_pos(self, x, y):
        c = MultiCollidable(self.x + x, self.y + y)
        c.collisions = self.collisions
        return c


class Rect(Collidable):
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h

    def __iter__(self):
        return [self.x, self.y, self.width, self.height]

    def __getitem__(self, item):
        return self.__iter__()[item]

    def adjust_pos(self, x, y):
        return Rect(self.x + x, self.y + y, self.width, self.height)

    def has_point(self, point):
        return self.x <= point.x <= self.x + self.width and self.y <= point.y <= self.y + self.height

    def is_colliding(self, c):
        a1 = Point(c.x, c.y)
        a2 = Point(c.x + c.width, c.y + c.height)

        c1 = Point(self.x, self.y)
        c2 = Point(self.x + self.width, self.y + self.height)

        # print(f"a = {a1.to_string()} {a2.to_string()}\nc = {c1.to_string()} {c2.to_string()}\n")
        return do_overlap(a1, a2, c1, c2)


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def to_string(self):
        return f"({self.x},{self.y})"


def do_overlap(a1, a2, b1, b2):
    if a1.x >= b2.x or a2.x <= b1.x:
        return False

    if a1.y >= b2.y or a2.y <= b1.y:
        return False

    return True
