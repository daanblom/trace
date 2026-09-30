# trace prototype

Headless CLI prototype for turning running/cycling GPX or GeoJSON files into portrait map images.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Set your CARTO API key:

```bash
export CARTO_API_KEY="your-key"
```

## Render

```bash
trace ride.gpx -o ride.png
```

Defaults are portrait 1080x1920.

Useful options:

```bash
trace ride.gpx \
  --width 1080 \
  --height 1920 \
  --padding 0.12 \
  --route-width 6 \
  --glow 18 \
  -o ride.png
```

Disable statistics:

```bash
trace ride.gpx --no-stats
```

Use a custom font:

```bash
trace ride.gpx --font /path/to/font.ttf
```

## What the prototype calculates from GPX

- distance
- elapsed time
- moving time (basic speed-threshold heuristic)
- average speed
- max speed (stored for later layouts)
- elevation gain/loss
- running pace

GeoJSON files are still accepted, but because the supplied GeoJSON does not contain timestamps, only geometry-derived stats such as distance/elevation can be meaningful.
