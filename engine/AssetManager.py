import pyglet
import os


class AssetManager:
    def __init__(self, name):
        self.table = {}
        self.name = name

    def load_image(self, namespace, path):
        if not namespace in self.table:
            self.table[namespace] = pyglet.image.load(path)

        return self.table[namespace]

    def get(self, namespace):
        return self.table[namespace]

    def load_pack(self, path):
        self.load_space(self.name, path)

    def load_space(self, parentnamespace, path):

        for f in os.listdir(path):
            d = os.path.join(path, f)

            if os.path.isdir(d):
                # print("loading space {}".format(d.split("/")[-1]))
                self.load_space(parentnamespace + "." + d.split("/")[-1], d)

            else:

                if f.endswith(".png"):
                    name = ".".join(f.split("/")[-1].split(".")[:-1])
                    self.load_image(parentnamespace + "." + name, d)


if __name__ == "__main__":
    am = AssetManager("game")

    am.load_pack("../test_game/assets")

    print(am.table)