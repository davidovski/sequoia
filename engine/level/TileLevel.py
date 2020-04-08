import os
from zipfile import ZipFile

import yaml

from engine.level.Level import Level
from engine.level.Tile import Tile


class TileLevel(Level):
    def __init__(self):

        self.width = 400
        self.height = 40
        self.tilesize = 64
        self.tiles = [[None for o in range(self.height)] for i in range(self.width)]

        # debug population
        # for x in range(self.width):
        #     for y in range(self.height):
        #         e = random.randint(0, 2)
        #         if e == 0:
        #             self.set_tile(x, y, Tile("game.tiles.metal"))
        #         elif e == 1:
        #             self.set_tile(x, y, Tile("game.tiles.brick"))

    def set_tile(self, x, y, tile):
        self.tiles[x][y] = tile

    def get_tile(self, x, y):
        return self.tiles[x][y]


class TileLevelLoader:
    def load(self, file):
        mapyml = {}
        if file.endswith(".zip"):
            print("Loading compressed map...")
            with ZipFile(file, 'r') as zipObj:
                listOfFileNames = zipObj.namelist()
                for fileName in listOfFileNames:
                    if fileName.endswith('.yml'):
                        zipObj.extract(fileName, 'temp')
                        print("Extracted map")
                        with open("temp/"+fileName) as f:
                            mapyml = yaml.load(f, Loader=yaml.FullLoader)

                        print("Cleaning up...")
                        os.remove("temp/"+fileName)
                        os.rmdir("temp")

        elif file.endswith(".yml"):
            with open(file) as f:
                mapyml = yaml.load(f, Loader=yaml.FullLoader)
            print("Loaded raw map")

        else:
            print("Invalid map!")

        self.create_instance(mapyml)

    def create_instance(self, map_data):

        w = map_data["properties"]["width"]
        h = map_data["properties"]["height"]
        tiles_list = map_data["tile_table"]
        tiles = {}

        for t in tiles_list:
            name = t["name"]
            collisions = t["collisions"]
            tile = Tile(name)
            tile.set_collisions(collisions)

            tiles[name] = tile


        level = TileLevel()

        level.width = w
        level.height = h

        for i in range(len(map_data["map"])):
            x, y = i*w, i*w + i
            t = tiles[map_data["map"][i]]
            level.set_tile(x, y, t)