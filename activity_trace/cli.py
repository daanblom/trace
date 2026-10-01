from pathlib import Path

import click

from .camera import camera_for_bounds
from .geo import activity_geometry, load_geojson, project_track
from .gpx import load_gpx
from .stats import calculate_stats
from .text import draw_stats
from .tiles import render_map
from .track import draw_route, route_pixels


def load_activity(path: str):
    suffix = Path(path).suffix.lower()
    if suffix == ".gpx":
        return load_gpx(path)
    if suffix in {".geojson", ".json"}:
        return load_geojson(path)
    raise click.ClickException("Input must be a .gpx, .geojson, or .json file")


@click.command()
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--width", default=1080, show_default=True, type=int)
@click.option("--height", default=1920, show_default=True, type=int)
@click.option(
    "--padding",
    default=0.12,
    show_default=True,
    type=click.FloatRange(0.0, 0.49),
    help="Padding as a fraction of image dimensions.",
)
@click.option("--route-width", default=3, show_default=True, type=int)
@click.option("--glow", default=0, show_default=True, type=int)
@click.option("--font", default=None, type=click.Path(exists=True, dir_okay=False), help="Path to a .ttf font.")
@click.option("--stats/--no-stats", default=True, show_default=True)
@click.option("--stat-size", default=150, show_default=True, type=int)
@click.option("--label-size", default=70, show_default=True, type=int)
@click.option("--margin", default=100, show_default=True, type=int)
@click.option("--line-gap", default=15, show_default=True, type=int)
@click.option("-o", "--output", default="run.png", show_default=True, type=click.Path(dir_okay=False, path_type=Path))
def main(input_file, width, height, padding, route_width, glow, font, stats, stat_size, label_size, margin, line_gap, output):
    """Render a running/cycling GPX or GeoJSON activity as a map image."""
    try:
        activity = load_activity(str(input_file))
        calculate_stats(activity)

        track = activity_geometry(activity)
        projected = project_track(track)
        camera = camera_for_bounds(projected.bounds, width, height, padding)

        click.echo(f"activity: {activity.name} ({activity.type})")
        click.echo(f"distance: {activity.distance_km:.2f} km")
        if activity.duration_s:
            click.echo(f"time:     {activity.duration_s:.0f} s")
            click.echo(f"avg:      {activity.average_speed_kmh:.2f} km/h")
        click.echo(f"elevation:+{activity.elevation_gain_m:.0f} m")
        click.echo(
            f"camera:   lon={camera.lon:.5f} lat={camera.lat:.5f} zoom={camera.zoom:.2f}"
        )

        base = render_map(camera.lon, camera.lat, camera.zoom, width, height)
        points = route_pixels(projected, camera, width, height)
        result = draw_route(base, points, width=route_width, glow=glow)

        if stats:
            result = draw_stats(
                result,
                activity,
                font_path=str(font) if font else None,
                margin=margin,
                line_gap=line_gap,
                stat_size=stat_size,
                label_size=label_size,
            )

        output.parent.mkdir(parents=True, exist_ok=True)
        result.convert("RGB").save(output, format="PNG", optimize=True)
        click.echo(f"written:  {output}")

    except Exception as exc:
        raise click.ClickException(str(exc)) from exc
