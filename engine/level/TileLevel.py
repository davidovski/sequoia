from engine.level.Level import Level
import random

from engine.level.Tile import Tile


class TileLevel(Level):
    def __init__(self, file):
        self.file = file

        self.width = 400
        self.height = 40

        self.tiles = [[None for o in range(self.height)] for i in range(self.width)]

        # debug population
        for x in range(self.width):
            for y in range(self.height):
                e = random.randint(0, 3)
                if e == 0:
                    self.set_tile(x, y, Tile("game.tiles.metal"))
                elif e == 1:
                    self.set_tile(x, y, Tile("game.tiles.brick"))

    def set_tile(self, x, y, tile):
        self.tiles[x][y] = tile

    def get_tile(self, x, y):
        return self.tiles[x][y]

