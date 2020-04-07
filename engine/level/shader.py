import math
def shade_light(surface, light):
    for x in range(surface.get_size()[0]):
        for y in range(surface.get_size()[1]):
            c = surface.get_at((x, y))
            d = (math.sqrt((x-light[0])**2 + (y-light[1])**2) / 64) + 0.5
            if d > 0:
                c = [int(i / d) for i in c]

            c = [0 if v < 0 else 255 if v > 255 else v for v in c]

            surface.set_at((x, y), c)

    return surface