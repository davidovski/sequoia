import sys

import pyglet
from pyglet import gl

from engine.AssetManager import AssetManager
from engine.level import shader
from engine.level.TileLevel import TileLevel
from engine.level.TileLevelRenderer import TileLevelRenderer


class GameInstance():
    def __init__(self, config):
        self.config = config


        split = config["aspect_ratio"].split(":")
        aspect_ratio = float(split[0]) / float(split[1])

        self.window_size = (int(config["resolution"] * aspect_ratio), int(config["resolution"]))

        r = self.config["mode"] == "fullscreen_windowed"

        self.window = pyglet.window.Window(width=self.window_size[0], height=self.window_size[1], caption=config["name"],  visible=True, resizable=r)
        if r:
            self.window.on_resize = self.on_resize

        if self.config["mode"] == "fullscreen":
            self.window.set_fullscreen(True)

        self.max_fps = int(config["max_fps"])

        pyglet.clock.schedule_interval(self.update, 1.0 / self.max_fps)
        self.fps = pyglet.window.FPSDisplay(self.window)

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)


        self.running = False

        self.mouse = {"left": False,
                      "right": False,
                      "pos": [0,0]
                      }

        self.asset_manager = AssetManager("game")
        self.asset_manager.load_pack(config["asset_pack"])

        self.level_renderer = TileLevelRenderer(self)
        self.level = TileLevel("file")

        self.level_renderer.prepare_level(self.level)

        self.zoom = 4
        self.viewport = [0, 0, self.window_size[0] / self.zoom, self.window_size[1] / self.zoom]

        self.keys = pyglet.window.key.KeyStateHandler()
        self.last_keys = self.keys
        self.window.push_handlers(self.keys)

    def run(self):
        self.running = True
        pyglet.app.run()

    def update(self, dt):
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

        self.tick()

        self.render()

    def render(self):
        self.window.clear()
        level_image = self.level_renderer.render(self.viewport)
        level_image.blit(0, 0, width=self.window_size[0], height=self.window_size[1])

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

        if self.keys[pyglet.window.key.F]:
            self.window.set_fullscreen(True)
        if self.keys[pyglet.window.key.G]:
            self.window.set_fullscreen(False)

        self.viewport = [self.viewport[0], self.viewport[1], int(self.window_size[0] / self.zoom), int(self.window_size[1] / self.zoom)]
        self.last_keys = self.keys
        pass

    def on_resize(self, width, height):
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glMatrixMode(gl.GL_MODELVIEW)
        self.window_size = [width, height]