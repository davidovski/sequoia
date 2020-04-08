from random import randint

import pyglet
import os


class AssetManager:
    def __init__(self, name):
        self.table = {}
        self.name = name

        self.missing_texture = pyglet.image.ImageData(16, 16, 'RGB', bytes([randint(0, 255) for i in range(16*16*3)]))

    def load_image(self, namespace, path):
        if not namespace in self.table:
            img = pyglet.image.load(path)
            self.table[namespace] = img

        return self.table[namespace]

    def get(self, namespace):
        if namespace in self.table:
            return self.table[namespace]
        else:
            return self.missing_texture

    def load_pack(self, path):
        self.load_space(self.name, path)

        print(f"Loaded {len(self.table)} assets from {path}")

    def load_space(self, parentnamespace, path):

        for f in os.listdir(path):
            d = os.path.join(path, f)

            if os.path.isdir(d):
                # print("loading space {}".format(d.split("/")[-1]))
                self.load_space(f"{parentnamespace}.{d.split('/')[-1]}", d)

            else:

                if f.endswith(".png"):
                    name = ".".join(f.split("/")[-1].split(".")[:-1])
                    self.load_image(parentnamespace + "." + name, d)


if __name__ == "__main__":
    am = AssetManager("game")

    am.load_pack("../test_game/assets")

    print(am.table)