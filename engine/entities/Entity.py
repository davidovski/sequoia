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
    def __init__(self, name, x, y, width, height):
        super().__init__(x, y)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.name = name
        self.animation_frame = 0

    def set_pos(self, x, y):
        self.x = x
        self.y = y

    def move(self, x, y):
        self.x += x
        self.y += y

    def update(self, game):
        self.tick(game)

    def get_image(self, asset_manager: AssetManager):
        data = asset_manager.get_data(self.name)
        img = asset_manager.get(self.name)

        if not data == {} and "animation" in data:
            a = int(self.animation_frame) % len(data["animation"])
            frame = data["animation"][a]

            return asset_manager.get_section(self.name, frame)

        else:
            return img

    def tick(self, game):
        self.animation_frame += 1
        pass

    def render(self, asset_manager: AssetManager, offset, scale):

        gl
        t = self.get_image(asset_manager).get_texture()
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

        t.blit((self.x - offset[0]) * scale, (self.y - offset[1]) * scale, 0, width=t.width * scale, height=t.height * scale)

    def calculate_collisions(self, asset_manager):
        if len(self.collisions) == 0:
            data = asset_manager.get_data(self.name)
            if "collisions" in data:
                for col in data["collisions"]:
                    self.add_collision(Rect(col[0], col[1], col[2], col[3]))
            else:
                self.add_collision(Rect(0, 0, self.width, self.height))

            print(f"calcuated {len(self.collisions)} collisions for {self.name}")


class WorldEntity(Entity):
    def __init__(self, name, x, y, width, height):
        super().__init__(name, x, y, width, height)
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
                    if self.on_ground:
                        bumped = False
                        for h in range(9):
                            nc = self.adjust_pos(v, h)
                            if not nc.is_colliding(game.level):
                                self.move(v, h)
                                bumped = True
                                break

                        if not bumped:
                            self.velocity.x = 0
                    else:
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


