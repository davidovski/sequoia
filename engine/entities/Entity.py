from pyglet import gl

from engine.AssetManager import AssetManager
from engine.collisions import Collidable, Rect, MultiCollidable
from engine.vector import Vector


class EntityInputs:
    def __init__(self, up, down, left, right, action):
        self.action = action
        self.right = right
        self.left = left
        self.down = down
        self.up = up


class Entity(MultiCollidable):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16

        # DEBUG collision
        self.add_collision(Rect(0, 0, self.width, self.height))

    def set_pos(self, x, y):
        self.x = x
        self.y = y

    def move(self, x, y):
        self.x += x
        self.y += y

    def update(self, game):
        self.tick(game)

    def get_image(self, asset_manager: AssetManager):
        pass

    def tick(self, game):
        pass

    def render(self, asset_manager: AssetManager, offset, scale):
        t = self.get_image(asset_manager).get_texture()
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

        t.blit((self.x - offset[0]) * scale, (self.y - offset[1]) * scale, 0, width=self.width * scale, height=self.height * scale)


class WorldEntity(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.velocity = Vector(0, 0)
        self.on_ground = False

    def update(self, game):
        super().update(game)

        if not self.velocity.x == 0:
            v = -1 if self.velocity.x < 0 else 1

            for i in range(abs(int(self.velocity.x))):
                nc = self.adjust_pos(v, 0)
                if not nc.is_colliding(game.level):
                    self.move(v, 0)
                else:
                    bumped = False
                    for h in range(9):
                        nc = self.adjust_pos(v, h)
                        if not nc.is_colliding(game.level):
                            self.move(v, h)
                            bumped = True
                            break

                    if not bumped:
                        self.velocity.x = 0
                        break


        if not self.velocity.y == 0:
            nc = self.adjust_pos(0, self.velocity.y)
            if not nc.is_colliding(game.level):
                self.move(0, self.velocity.y)
                if self.velocity.y > 0:
                    self.on_ground = False
            else:
                if self.velocity.y < 0:
                    self.on_ground = True
                self.velocity.y = 0

        if self.on_ground:
            f = 0.5
            if self.velocity.x > f:
                self.velocity.x -= f
            elif self.velocity.x < -f:
                self.velocity.x += f
            else:
                self.velocity.x = 0

        self.velocity.y -= game.level.gravity
