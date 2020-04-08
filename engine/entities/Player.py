import pyglet

from engine.AssetManager import AssetManager
# from engine.GameInstance import GameInstance
from engine.entities.Entity import Entity, EntityInputs, WorldEntity


class PlayerEntity(WorldEntity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.i = 0

    def tick(self, game):

        up = game.keys[pyglet.window.key.W]
        down = game.keys[pyglet.window.key.S]
        left = game.keys[pyglet.window.key.A]
        right = game.keys[pyglet.window.key.D]

        action = game.keys[pyglet.window.key.SPACE]

        v = 3

        if self.on_ground:

            if left and right:
                self.velocity.x = 0
            elif left:
                self.velocity.x = -v
            elif right:
                self.velocity.x = v

            if up:
                self.velocity.y = 8
        else:

            if left and not right:
                if self.velocity.x > -v:
                    self.velocity.x -= 1
            if right and not left:
                if self.velocity.x < v:
                    self.velocity.x += 1

    def get_image(self, asset_manager: AssetManager):
        return asset_manager.get("game.missing")
