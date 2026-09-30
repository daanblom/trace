import math

from PIL import Image, ImageDraw, ImageFilter


def mercator_to_pixel(x, y, camera, width, height):
    scale = 256 * (2**camera.zoom)

    lon = math.degrees(x / 6378137.0)
    lat = math.degrees(2 * math.atan(math.exp(y / 6378137.0)) - math.pi / 2)

    cx = (camera.lon + 180) / 360 * scale
    cy = (1 - math.asinh(math.tan(math.radians(camera.lat))) / math.pi) / 2 * scale

    px = (lon + 180) / 360 * scale - cx + width / 2
    py = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * scale - cy + height / 2
    return px, py


def route_pixels(track, camera, width, height):
    return [
        mercator_to_pixel(x, y, camera, width, height)
        for x, y in track.coords
    ]


def draw_route(base, points, width=5, color=(255, 35, 40), glow=18):
    result = base.convert("RGBA")

    glow_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    glow_draw.line(points, fill=(*color, 180), width=max(1, width * 3), joint="curve")
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(glow))
    result.alpha_composite(glow_layer)

    halo = Image.new("RGBA", base.size, (0, 0, 0, 0))
    halo_draw = ImageDraw.Draw(halo)
    halo_draw.line(points, fill=(*color, 220), width=max(1, width * 2), joint="curve")
    result.alpha_composite(halo)

    core = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(core)
    draw.line(points, fill=(255, 55, 60, 255), width=max(1, width), joint="curve")
    result.alpha_composite(core)

    return result
