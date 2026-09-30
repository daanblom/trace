import json
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import LineString, MultiLineString, shape
from shapely.ops import transform, unary_union

from .activity import Activity, TrackPoint

WGS84_TO_MERCATOR = Transformer.from_crs(
    "EPSG:4326", "EPSG:3857", always_xy=True
).transform


def geometry_from_points(points: list[TrackPoint]):
    return LineString([(p.lon, p.lat) for p in points])


def load_geojson(path: str) -> Activity:
    data = json.loads(Path(path).read_text())
    geometries = []
    name = "Activity"
    activity_type = "unknown"

    if str(data.get("type", "")).lower() == "featurecollection":
        for feature in data.get("features", []):
            properties = feature.get("properties") or {}
            name = properties.get("name") or name
            activity_type = properties.get("type") or activity_type
            geometry = feature.get("geometry")
            if geometry:
                geom = shape(geometry)
                if not geom.is_empty:
                    geometries.append(geom)
    elif str(data.get("type", "")).lower() == "feature":
        properties = data.get("properties") or {}
        name = properties.get("name") or name
        activity_type = properties.get("type") or activity_type
        geometry = data.get("geometry")
        if geometry:
            geometries.append(shape(geometry))
    else:
        geometries.append(shape(data))

    if not geometries:
        raise ValueError("GeoJSON contains no geometry")

    merged = unary_union(geometries)
    if isinstance(merged, LineString):
        coordinates = list(merged.coords)
    elif isinstance(merged, MultiLineString):
        coordinates = [p for line in merged.geoms for p in line.coords]
    elif hasattr(merged, "geoms"):
        lines = [g for g in merged.geoms if isinstance(g, (LineString, MultiLineString))]
        if not lines:
            raise ValueError(f"Unsupported GeoJSON geometry type: {merged.geom_type}")
        merged = unary_union(lines)
        if isinstance(merged, LineString):
            coordinates = list(merged.coords)
        else:
            coordinates = [p for line in merged.geoms for p in line.coords]
    else:
        raise ValueError(f"Unsupported GeoJSON geometry type: {merged.geom_type}")

    points = [TrackPoint(lat=y, lon=x) for x, y, *_ in coordinates]
    return Activity(name=name, type=activity_type, points=points)


def activity_geometry(activity: Activity):
    return geometry_from_points(activity.points)


def project_track(track):
    return transform(WGS84_TO_MERCATOR, track)
