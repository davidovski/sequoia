import pygame

from engine.level.Level import Level
from engine.level.TileLevel import TileLevel


class TileLevelRenderer:
    def __init__(self, game):
        self.game = game
        self.current_level = Level()
        self.tilesize = 16

        self.level_surf = None

    def prepare_level(self, level):
        if isinstance(level, TileLevel):
            self.current_level = level

            self.level_surf = pygame.Surface((level.width * self.tilesize, level.height * self.tilesize), pygame.SRCALPHA)

            for tx in range(self.current_level.width):
                for ty in range(self.current_level.height):
                    x = tx * self.tilesize
                    y = ty * self.tilesize

                    tile = self.current_level.get_tile(tx, ty)
                    if tile is not None:
                        self.level_surf.blit(self.game.asset_manager.get(tile.image), (x, y))

    def render(self, viewport):
        cropped = pygame.Surface((viewport[2], viewport[3]))
        cropped.blit(self.level_surf, (0,0), viewport)

        return cropped
