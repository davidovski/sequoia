import math
import os
from zipfile import ZipFile

import yaml

from engine.collisions import Collidable
from engine.level.Level import Level
from engine.level.tiles.Tile import Tile


class TileLevel(Level):
    def __init__(self):
        super().__init__()
        self.width = 400
        self.height = 40
        self.tilesize = 16
        self.tiles = [[None for o in range(self.height)] for i in range(self.width)]

        self.gravity = 1

        # debug population
        # for x in range(self.width):
        #     for y in range(self.height):
        #         e = random.randint(0, 2)
        #         if e == 0:
        #             self.set_tile(x, y, Tile("game.tiles.metal"))
        #         elif e == 1:
        #             self.set_tile(x, y, Tile("game.tiles.brick"))

        for x in range(self.width):
            for y in range(self.height):
                t = self.get_tile(x, y)
                if t is not None:
                    for c in t.collisions:
                        self.add_collision(c.adjust_pos(x * self.tilesize, y * self.tilesize))

    def set_tile(self, x, y, tile):

        self.tiles[x][y] = tile

    def get_tile(self, x, y):
        return self.tiles[x][y]

    def is_colliding(self, target):
        # Iterating through tiles
        # OPTIMiSE: only iterate through tiles near target rect

        for x in range(self.width):
            for y in range(self.height):
                t = self.get_tile(x, y)
                if t is not None:

                    if abs(target.x - x*self.tilesize) < 16 and abs(target.y - y*self.tilesize) < 64:
                        for c in t.collisions:
                            if c.adjust_pos(x*self.tilesize, y*self.tilesize).is_colliding(target):
                                return True


def create_level_instance(map_data):
    tile_size = map_data["properties"]["tile_size"]
    w = map_data["properties"]["width"]
    h = map_data["properties"]["height"]
    tiles_list = map_data["tile_table"]
    tiles = {}

    for t in tiles_list:
        name = t["name"]
        collisions = t["collisions"]
        t = Tile(name)
        t.set_collisions(collisions)
        tiles[name] = t

    level = TileLevel()

    level.width = w
    level.height = h
    level.tilesize = tile_size

    for i in range(len(map_data["map"])):
        x = math.floor(i / h)
        y = i - (x * h)
        n = map_data["map"][i]
        if n == "":
            t = None
        else:
            t = tiles[n]

        level.set_tile(x, y, t)

    return level


def load_map_file(file):
    mapyml = {}
    if not os.path.exists(file):
        print("file not found, creating empty map")
        return TileLevel()
    else:
        if file.endswith(".zip"):
            print("Loading compressed map...")
            with ZipFile(file, 'r') as zipObj:
                listOfFileNames = zipObj.namelist()
                for fileName in listOfFileNames:
                    if fileName.endswith('.yml'):
                        zipObj.extract(fileName, 'temp')
                        print("Extracted map")
                        with open("temp/" + fileName) as f:
                            mapyml = yaml.load(f, Loader=yaml.FullLoader)

                        print("Cleaning up...")
                        os.remove("temp/" + fileName)
                        os.rmdir("temp")

        elif file.endswith(".yml"):
            with open(file) as f:
                mapyml = yaml.load(f, Loader=yaml.FullLoader)
            print("Loaded raw map")

        else:
            print("Invalid map!")

    return create_level_instance(mapyml)
