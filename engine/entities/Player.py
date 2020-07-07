import pyglet

from engine.AssetManager import AssetManager
# from engine.GameInstance import GameInstance
from engine.collisions import Rect
from engine.entities.Entity import Entity, EntityInputs, WorldEntity


class PlayerEntity(WorldEntity):
    def __init__(self, x, y):
        super().__init__("game.player", x, y, 11, 26)
        self.i = 0

        self.crouching = False
        self.last_crouching = False
        self.looking_left = False

        self.a = 0

    def tick(self, game):
        up = game.keys[pyglet.window.key.W]
        down = game.keys[pyglet.window.key.S]
        left = game.keys[pyglet.window.key.A]
        right = game.keys[pyglet.window.key.D]

        action = game.keys[pyglet.window.key.SPACE]

        sprint = game.keys[pyglet.window.key.LSHIFT]

        if down:
            self.crouching = True
        else:
            if not self.adjust_pos(0, 10).is_colliding(game.level):
                self.crouching = False

        if self.crouching and not self.last_crouching:
            self.collisions[0].height = 2
            self.collisions[1].y = 3
            self.height = 16
        elif not self.crouching and self.last_crouching:
            self.collisions[0].height = 13
            self.collisions[1].y = 14
            self.height = 24

        v = 2 if sprint and not self.crouching else 1
        if up:
            v *= 1.2

        if self.on_ground:
            if left and right:
                self.velocity.x = 0
            elif left:
                self.velocity.x = -v
                self.looking_left = True

            elif right:
                self.velocity.x = v
                self.looking_left = False

            if up:
                self.velocity.y = 8
        else:

            if left and not right:
                if self.velocity.x > -v:
                    self.velocity.x -= 1
            if right and not left:
                if self.velocity.x < v:
                    self.velocity.x += 1

        if self.crouching:
            self.animation_frame = 2 if self.looking_left else 3
        else:
            if not self.velocity.x == 0:
                self.animation_frame = (8 if self.looking_left else 4) + (self.x / 4 % 4)
            else:
                self.animation_frame = 0 if self.looking_left else 1

        self.last_crouching = self.crouching
