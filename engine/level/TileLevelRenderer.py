import pyglet
from pyglet import gl

from engine.level.Level import Level
from engine.level.TileLevel import TileLevel


class TileLevelRenderer:
    def __init__(self, game):
        self.game = game
        self.current_level = Level()
        self.tilesize = 16

        self.image = None

    def prepare_level(self, level):
        self.current_level = level
        self.image = pyglet.image.Texture.create(width=(self.current_level.width*self.tilesize), height=(self.current_level.height*self.tilesize))
        for tx in range(self.current_level.width):
            for ty in range(self.current_level.height):
                x = tx * self.tilesize
                y = ty * self.tilesize
                tile = self.current_level.get_tile(tx, ty)
                if tile is not None:
                    t = self.game.asset_manager.get(tile.image)
                    self.image.blit_into(t, x, y, 0)

    def render(self):
        self.image.blit(0, 0)

    # def prepare_level(self, level):
    #     if isinstance(level, TileLevel):
    #         self.current_level = level
    #
    #         self.level_surf = pygame.Surface((level.width * self.tilesize, level.height * self.tilesize), pygame.SRCALPHA)
    #
    #         for tx in range(self.current_level.width):
    #             for ty in range(self.current_level.height):
    #                 x = tx * self.tilesize
    #                 y = ty * self.tilesize
    #
    #                 tile = self.current_level.get_tile(tx, ty)
    #                 if tile is not None:
    #                     self.level_surf.blit(self.game.asset_manager.get(tile.image), (x, y))
    #
    def render(self, vp):
        return self.image.get_region(vp[0], vp[1],vp[2], vp[3])
