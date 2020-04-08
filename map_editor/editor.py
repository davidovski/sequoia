from random import randint

import pyglet

from engine.GameInstance import GameInstance
import yaml
from engine.collisions import Rect
from engine.level.tiles.Tile import Tile
from engine.level.TileLevel import TileLevel

def save_level(level: TileLevel):
    map_data = {}
    map = []
    tiles_contents = []
    for x in range(level.width):
        for y in range(level.height):
            t = level.get_tile(x, y)
            if t is not None:
                if not t.image in [e["name"] for e in tiles_contents]:
                    tiles_contents.append({
                        "name": t.image,
                        "collisions": [c.__iter__() for c in t.collisions]
                    })
                map.append(t.image)
            else:
                map.append("")

    print(f"There are {len(tiles_contents)} unique tiles")
    map_data["properties"] = {}
    map_data["tile_table"] = tiles_contents
    map_data["properties"]["width"] = level.width
    map_data["properties"]["height"] = level.height
    map_data["properties"]["tile_size"] = level.tilesize

    map_data["map"] = map

    with open(game.config["start"], 'w') as file:
        yaml.dump(map_data, file)


def tick():
    v = 4
    if game.keys[pyglet.window.key.LEFT]:
        game.viewport[0] -= v
    if game.keys[pyglet.window.key.RIGHT]:
        game.viewport[0] += v
    if game.keys[pyglet.window.key.DOWN]:
        game.viewport[1] -= v
    if game.keys[pyglet.window.key.UP]:
        game.viewport[1] += v

    if game.keys[pyglet.window.key.A]:
        sel[0] -= 1
        update()

    if game.keys[pyglet.window.key.D]:
        sel[0] += 1
        update()

    if game.keys[pyglet.window.key.S]:
        sel[1] -= 1
        update()

    if game.keys[pyglet.window.key.W]:
        sel[1] += 1
        update()


    if game.keys[pyglet.window.key.F2]:
        save_level(game.level)

    if game.keys[pyglet.window.key.SPACE]:
        n ="game.tiles.brick"
        if randint(0, 1) == 0:
            n = "game.tiles.metal"
        t = Tile(n)
        t.set_collisions([Rect(0, 0, 16, 16)])
        game.level.set_tile(sel[0], sel[1], t)
        update()

    if game.keys[pyglet.window.key.U]:
        n ="game.tiles.step"

        t = Tile(n)
        t.set_collisions([Rect(0, 0, 16, 8), Rect(8, 8, 8, 8)])
        game.level.set_tile(sel[0], sel[1], t)
        update()

    if game.keys[pyglet.window.key.I]:
        n ="game.tiles.slope"

        t = Tile(n)
        t.set_collisions([
            Rect(0, 0, 9, 9),
            Rect(0, 9, 7, 2),
            Rect(0, 11, 5, 2),
            Rect(0, 13, 3, 2),
            Rect(9, 0, 2, 7),
            Rect(11, 0, 2, 5),
            Rect(13, 0, 3, 3)

        ])
        game.level.set_tile(sel[0], sel[1], t)
        update()

    if game.keys[pyglet.window.key.Q]:

        game.level.set_tile(sel[0], sel[1], None)
        update()

    if game.keys[pyglet.window.key.EQUAL]:
        game.zoom *= 1.2
    if game.keys[pyglet.window.key.MINUS]:
        game.zoom /= 1.2


def update():
    sel[0] %= game.level.width
    sel[1] %= game.level.height

    game.level_renderer.prepare_level(game.level)
    game.level_renderer.image.blit_into(selection_img, sel[0] * game.level.tilesize, sel[1] * game.level.tilesize, 0)


sel = [0, 0]

if __name__ == "__main__":
    config = {}

    with open('config.yml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    game = GameInstance(config)
    game.tick = tick

    selection_img = pyglet.image.load("sel.png")

    game.run()
