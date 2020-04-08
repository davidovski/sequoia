from engine.collisions import Collidable, MultiCollidable


class Level(MultiCollidable):
    def __init__(self):
        super().__init__(0, 0)
        self.width = 0
        self.height = 0

    def render(self):
        pass
