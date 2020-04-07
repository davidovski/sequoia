import sys

import pygame

from engine.AssetManager import AssetManager
from engine.level.TileLevel import TileLevel
from engine.level.TileLevelRenderer import TileLevelRenderer
from engine.level.shader import shade_light


class GameInstance():
    def __init__(self, config):
        self.config = config

        pygame.init()

        split = config["aspect_ratio"].split(":")
        aspect_ratio = float(split[0]) / float(split[1])

        self.window_size = (int(config["resolution"] * aspect_ratio), int(config["resolution"]))

        self.screen = pygame.display.set_mode(self.window_size, pygame.DOUBLEBUF | pygame.HWSURFACE, 32)
        pygame.display.set_caption(config["name"])

        self.max_fps = config["max_fps"]

        self.frame_clock = pygame.time.Clock()

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

        self.keys = pygame.key.get_pressed()
        self.last_keys = pygame.key.get_pressed()
        self.font = pygame.font.SysFont(None, 24)

    def run(self):
        self.running = True

        while self.running:
            self.tick()

            self.render()
            self.frame_clock.tick(self.max_fps)

            self.event_handler()
            self.input_handler()

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def input_handler(self):
        m = pygame.mouse.get_pressed()
        self.last_keys = self.keys
        self.keys = pygame.key.get_pressed()
        self.mouse = {
            "left": m[0],
            "right": m[1],
            "pos": pygame.mouse.get_pos()
                    }

    def render(self):
        self.screen.fill((20, 20, 40))

        l = self.level_renderer.render(self.viewport)
        shade_light(l, [i / self.zoom for i in self.mouse["pos"]])
        l = pygame.transform.scale(l, self.window_size)

        self.screen.blit(l, (0, 0))

        text = self.font.render("{} fps".format(int(self.frame_clock.get_fps())), True, (255, 255, 255))
        self.screen.blit(text, (20, 20))

        pygame.display.flip()

    def tick(self):
        v = 4
        if self.keys[pygame.K_LEFT]:
            self.viewport[0] -= v
        if self.keys[pygame.K_RIGHT]:
            self.viewport[0] += v
        if self.keys[pygame.K_DOWN]:
            self.viewport[1] += v
        if self.keys[pygame.K_UP]:
            self.viewport[1] -= v

        if self.keys[pygame.K_EQUALS]:
            self.zoom *= 1.2
        if self.keys[pygame.K_MINUS]:
            self.zoom /= 1.2

        self.viewport = [self.viewport[0], self.viewport[1], self.window_size[0] / self.zoom, self.window_size[1] / self.zoom]

        pass
