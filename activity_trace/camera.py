import math
from dataclasses import dataclass

TILE_SIZE = 256


@dataclass
class Camera:
    lon: float
    lat: float
    zoom: float


def lonlat_to_world(lon: float, lat: float, zoom: float):
    scale = TILE_SIZE * (2**zoom)
    x = (lon + 180.0) / 360.0 * scale
    lat = max(-85.05112878, min(85.05112878, lat))
    y = (1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * scale
    return x, y


def world_to_lonlat(x: float, y: float, zoom: float):
    scale = TILE_SIZE * (2**zoom)
    lon = x / scale * 360.0 - 180.0
    n = math.pi - 2.0 * math.pi * y / scale
    lat = math.degrees(math.atan(math.sinh(n)))
    return lon, lat


def camera_for_bounds(bounds, width, height, padding):
    minx, miny, maxx, maxy = bounds

    def mercator_to_lonlat(x, y):
        lon = math.degrees(x / 6378137.0)
        lat = math.degrees(2 * math.atan(math.exp(y / 6378137.0)) - math.pi / 2)
        return lon, lat

    minlon, minlat = mercator_to_lonlat(minx, miny)
    maxlon, maxlat = mercator_to_lonlat(maxx, maxy)

    # Keep the requested padding as a fraction of image dimensions.
    pad_x = width * padding
    pad_y = height * padding
    usable_w = max(1.0, width - 2 * pad_x)
    usable_h = max(1.0, height - 2 * pad_y)

    x1, y1 = lonlat_to_world(minlon, maxlat, 0)
    x2, y2 = lonlat_to_world(maxlon, minlat, 0)

    span_x = max(abs(x2 - x1), 1e-9)
    span_y = max(abs(y2 - y1), 1e-9)

    zoom_x = math.log2(usable_w / span_x)
    zoom_y = math.log2(usable_h / span_y)
    zoom = max(1.0, min(18.0, min(zoom_x, zoom_y)))

    center_x = (x1 + x2) / 2 * (2**zoom)
    center_y = (y1 + y2) / 2 * (2**zoom)
    lon, lat = world_to_lonlat(center_x, center_y, zoom)

    return Camera(lon, lat, zoom)
