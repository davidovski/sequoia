from random import randint

import pyglet
import os

import yaml

from engine import shaders


class AssetManager:
    def __init__(self, name):
        self.table = {}
        self.transformations = {}
        self.name = name
        self.shader_files = {}
        self.missing_texture = pyglet.image.ImageData(16, 16, 'RGB', bytes([randint(0, 255) for i in range(16 * 16 * 3)]))
        self.shaders = {}

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
        print(f"Loaded {len(self.table)} assets from \"{path}\"")

    def create_shader(self, name):
        vs = name + ".vs"
        fs = name + ".fs"
        if vs in self.shader_files and fs in self.shader_files:
            vert_shader = bytes(self.shader_files[vs], "UTF-8")
            frag_shader = bytes(self.shader_files[fs], "UTF-8")

            self.shaders[name] = shaders.from_string(vert_shader, frag_shader)

    def get_shader(self, name):
        if name in self.shaders:
            return self.shaders[name]
        else:
            return None

    def load_space(self, parent_name_space, path):

        for f in os.listdir(path):
            d = os.path.join(path, f)

            if os.path.isdir(d):
                # print("loading space {}".format(d.split("/")[-1]))
                self.load_space(f"{parent_name_space}.{d.split('/')[-1]}", d)

            else:
                name = ".".join(f.split("/")[-1].split(".")[:-1])
                if f.endswith(".png"):
                    self.load_image(parent_name_space + "." + name, d)
                if f.endswith(".yml"):
                    name += ".data"
                    self.load_data(parent_name_space + "." + name, d)

                if f.endswith(".fs") or f.endswith(".vs"):
                    with open(d, "r") as s:
                        self.shader_files[name + (".fs" if f.endswith(".fs") else ".vs")] = s.read()
                    self.create_shader(name)


if __name__ == "__main__":
    am = AssetManager("game")

    am.load_pack("../test_game/assets")

    print(am.table)
