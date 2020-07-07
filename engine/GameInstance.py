import sys

import pyglet
from pyglet import gl

from engine.AssetManager import AssetManager
from engine.entities.Player import PlayerEntity
from engine.level import shader
from engine.level.TileLevel import TileLevel, load_map_file
from engine.level.TileLevelRenderer import TileLevelRenderer


class GameInstance():
    def __init__(self, config):
        self.config = config

        split = config["aspect_ratio"].split(":")
        aspect_ratio = float(split[0]) / float(split[1])

        self.window_size = (int(config["resolution"] * aspect_ratio), int(config["resolution"]))

        r = self.config["mode"] == "fullscreen_windowed"

        self.window = pyglet.window.Window(width=self.window_size[0], height=self.window_size[1], caption=config["name"], visible=True, resizable=r)
        self.window.on_resize = self.on_resize
        # if r:
        #     self.window.on_resize = self.on_resize

        if self.config["mode"] == "fullscreen":
            self.window.set_fullscreen(True)

        self.max_fps = int(config["max_fps"])
        self.tps = self.max_fps
        pyglet.clock.schedule_interval(self.update, 1.0 / self.max_fps)
        pyglet.clock.schedule_interval(self.render, 1.0 / self.max_fps)

        self.fps = pyglet.window.FPSDisplay(self.window)

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        self.running = False

        self.mouse = {"left": False,
                      "right": False,
                      "pos": [0, 0]
                      }

        self.asset_manager = AssetManager("game")
        self.asset_manager.load_pack(config["asset_pack"])

        self.level_renderer = TileLevelRenderer(self)
        self.level = load_map_file(config["start"])

        self.level_renderer.prepare_level(self.level)

        self.zoom = 4
        self.viewport = [0, 0, self.window_size[0] / self.zoom, self.window_size[1] / self.zoom]

        self.keys = pyglet.window.key.KeyStateHandler()
        self.last_keys = self.keys
        self.window.push_handlers(self.keys)

        self.entities = []

        self.entities.append(PlayerEntity(32, 32))

        self.shader = self.asset_manager.get_shader("test")

        self.a = 0

    def run(self):
        self.running = True

        for e in self.entities:
            e.calculate_collisions(self.asset_manager)

        self.shader.use()

        pyglet.app.run()

    def update(self, dt):
        self.a += 1
        self.tps = (self.tps + (dt ** -1)) / 2
        for e in self.entities:
            e.update(self)

        self.tick()
        self.last_keys = self.keys

        self.viewport = [self.viewport[0], self.viewport[1], int(self.window_size[0] / self.zoom), int(self.window_size[1] / self.zoom)]

    def render(self, dt):

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

        gl.glClearColor(0.5, 0.6, 0.7, 1.0)
        self.window.clear()

        width, height = self.window_size

        size = 10

        gl.glColor3ub(127, 0, 0)
        gl.glBegin(gl.GL_QUADS)
        # gl.glVertex2f(-size, -size)
        # gl.glVertex2f(size, -size)
        # gl.glVertex2f(size, size)
        # gl.glVertex2f(-size, size)
        # gl.glVertex2f(0, 0)
        # gl.glVertex2f(self.window_size[1], 0)
        # gl.glVertex2f(self.window_size[0], self.window_size[1])
        # gl.glVertex2f(0, self.window_size[1])
        gl.glVertex2f(-width / 2, -height / 2)
        gl.glVertex2f(width / 2, -height / 2)
        gl.glVertex2f(width / 2, height /2)
        gl.glVertex2f(-width / 2, height / 2)
        gl.glEnd()

        # level_image = self.level_renderer.render(self.viewport)
        # level_image.blit(0, 0, width=self.window_size[0], height=self.window_size[1])
        #
        # for e in self.entities:
        #     e.render(self.asset_manager, self.viewport, self.zoom)
        #
        # text = f"tps={round(self.tps)} x={round(self.entities[0].velocity.x, 2)} y={round(self.entities[0].velocity.y, 2)}"
        # label = pyglet.text.Label(text, font_size=36, x=8, y=self.window.height - (36 + 8))
        # label.draw()

        self.fps.draw()

    def tick(self):
        v = 4

        if self.keys[pyglet.window.key.LEFT]:
            self.viewport[0] -= v
        if self.keys[pyglet.window.key.RIGHT]:
            self.viewport[0] += v
        if self.keys[pyglet.window.key.DOWN]:
            self.viewport[1] -= v
        if self.keys[pyglet.window.key.UP]:
            self.viewport[1] += v

        if self.keys[pyglet.window.key.EQUAL]:
            self.zoom *= 1.2
        if self.keys[pyglet.window.key.MINUS]:
            self.zoom /= 1.2

        pass

    def on_resize(self, width, height):
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)

        gl.glLoadIdentity()
        gl.glOrtho(-width / 2, width / 2, -height / 2, height / 2, -1, 1)
        # gl.glOrtho(0, width, 0, height, 0, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)

        self.window_size = [width, height]

