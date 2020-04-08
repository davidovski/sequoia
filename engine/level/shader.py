import math
# def shade_light(surface, light):
#     for x in range(surface.get_size()[0]):
#         for y in range(surface.get_size()[1]):
#             c = surface.get_at((x, y))
#             d = (math.sqrt((x-light[0])**2 + (y-light[1])**2) / 64) + 0.5
#             if d > 0:
#                 c = [int(i / d) for i in c]
#
#             c = [0 if v < 0 else 255 if v > 255 else v for v in c]
#
#             surface.set_at((x, y), c)
#
#     return surface
from random import randint

import pyglet
from pyglet.gl import GLubyte, gl


def shade(image):
    light = [0,0]
    rawimage = image.get_image_data()
    format = 'RGBA'
    pitch = rawimage.width * len(format)
    pixels = rawimage.get_data(format, pitch)

    new = []

    for y in range(int(rawimage.height)):
        for x in range(int(rawimage.width)):
            i = (4*rawimage.width * y)+4*x
            c = pixels[i:i+len(format)]

            n = [w for w in c]
            d = (math.sqrt((x-light[0])**2 + (y-light[1])**2) / 64) + 0.5
            if d > 0:
                n = [int(i / d) for i in n]

            n = [0 if v < 0 else 255 if v > 255 else v for v in n]

            new.extend(n)

    new = bytes(new)
    rawimage.set_data(format, pitch, new)

    return rawimage