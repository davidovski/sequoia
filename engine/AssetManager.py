from random import randint

import pyglet
import os

import yaml


class AssetManager:
    def __init__(self, name):
        self.table = {}
        self.transformations = {}
        self.name = name

        self.missing_texture = pyglet.image.ImageData(16, 16, 'RGB', bytes([randint(0, 255) for i in range(16 * 16 * 3)]))

    def load_image(self, namespace, path):
        if not namespace in self.table:
            img = pyglet.image.load(path)
            self.table[namespace] = img

        return self.table[namespace]

    def load_data(self, namespace, path):
        if not namespace in self.table:
            with open(path) as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
                self.table[namespace] = data

        return self.table[namespace]

    def get(self, namespace):
        if namespace in self.table:
            return self.table[namespace]
        else:
            return self.missing_texture

    def get_section(self, namespace, frame):
        key = str(frame)
        if key in self.transformations:
            return self.transformations[key]
        else:
            img = self.get(namespace)
            section = frame["section"]
            flip_opts = frame["flip"]
            reg = img.get_region(section[0], section[1], section[2], section[3]).get_texture()

            h = "h" in flip_opts
            v = "v" in flip_opts

            t = reg.get_transform(flip_x=h, flip_y=v)
            self.transformations[key] = t

            return t

    def get_data(self, namespace):
        if not namespace.endswith(".data"):
            namespace += ".data"
        if namespace in self.table:
            return self.table[namespace]
        else:
            return {}

    def load_pack(self, path):
        self.load_space(self.name, path)
        print(self.table)
        print(f"Loaded {len(self.table)} assets from {path}")

    def load_space(self, parent_name_space, path):

        for f in os.listdir(path):
            d = os.path.join(path, f)

            if os.path.isdir(d):
                # print("loading space {}".format(d.split("/")[-1]))
                self.load_space(f"{parent_name_space}.{d.split('/')[-1]}", d)

            else:

                if f.endswith(".png"):
                    name = ".".join(f.split("/")[-1].split(".")[:-1])
                    self.load_image(parent_name_space + "." + name, d)
                if f.endswith(".yml"):
                    name = ".".join(f.split("/")[-1].split(".")[:-1]) + ".data"
                    self.load_data(parent_name_space + "." + name, d)


if __name__ == "__main__":
    am = AssetManager("game")

    am.load_pack("../test_game/assets")

    print(am.table)
