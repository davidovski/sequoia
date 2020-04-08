from engine.collisions import Rect, Collidable


class Tile(Collidable):
    def __init__(self, namespace):
        self.image = namespace

        self.collisions = []

    def set_collisions(self, collisions_list):
        for c in collisions_list:
            self.collisions.append(Rect(c[0], c[1], c[2], c[3]))

    def is_colliding(self, c: Collidable):
        return True in [c.is_colliding(col) for col in self.collisions]
