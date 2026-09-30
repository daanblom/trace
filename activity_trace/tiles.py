import io
import math
import os

import requests
from PIL import Image

TILE_SIZE = 256
TILE_URL = (
    "https://basemaps.cartocdn.com/rastertiles/dark_nolabels/"
    "{z}/{x}/{y}.png?key={key}"
)


def _tile_xy(lon, lat, zoom):
    n = 2**zoom
    x = (lon + 180.0) / 360.0 * n
    lat = max(-85.05112878, min(85.05112878, lat))
    y = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
    return x, y


def render_map(lon, lat, zoom, width, height, session=None):
    api_key = os.environ.get("CARTO_API_KEY")
    if not api_key:
        raise RuntimeError(
            "CARTO_API_KEY is not set. Export it before running trace."
        )

    # Tiles exist at integer zoom levels. Render at the lower integer zoom,
    # then scale the stitched raster to the requested fractional zoom so the
    # map and route use the exact same camera transform.
    z = int(math.floor(zoom))
    scale_factor = 2 ** (zoom - z)

    source_width = math.ceil(width / scale_factor) + TILE_SIZE * 2
    source_height = math.ceil(height / scale_factor) + TILE_SIZE * 2

    cx, cy = _tile_xy(lon, lat, z)
    center_px = cx * TILE_SIZE
    center_py = cy * TILE_SIZE

    left = center_px - source_width / 2
    top = center_py - source_height / 2

    x0 = math.floor(left / TILE_SIZE)
    y0 = math.floor(top / TILE_SIZE)
    x1 = math.floor((left + source_width - 1) / TILE_SIZE)
    y1 = math.floor((top + source_height - 1) / TILE_SIZE)

    canvas = Image.new("RGB", (source_width, source_height), "#222627")
    own_session = session is None
    session = session or requests.Session()
    session.headers.setdefault("User-Agent", "trace/0.2")

    n = 2**z
    for ty in range(y0, y1 + 1):
        for tx in range(x0, x1 + 1):
            wrapped_x = tx % n
            if ty < 0 or ty >= n:
                continue

            url = TILE_URL.format(z=z, x=wrapped_x, y=ty, key=api_key)
            response = session.get(url, timeout=20)
            response.raise_for_status()

            tile = Image.open(io.BytesIO(response.content)).convert("RGB")
            px = tx * TILE_SIZE - left
            py = ty * TILE_SIZE - top
            canvas.paste(tile, (round(px), round(py)))

    if own_session:
        session.close()

    scaled_width = max(width, round(source_width * scale_factor))
    scaled_height = max(height, round(source_height * scale_factor))
    scaled = canvas.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)

    left_crop = (scaled.width - width) // 2
    top_crop = (scaled.height - height) // 2
    return scaled.crop((
        left_crop,
        top_crop,
        left_crop + width,
        top_crop + height,
    ))
