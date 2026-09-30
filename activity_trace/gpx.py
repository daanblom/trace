import xml.etree.ElementTree as ET
from datetime import datetime

from .activity import Activity, TrackPoint

NS = {"gpx": "http://www.topografix.com/GPX/1/1"}


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_gpx(path: str) -> Activity:
    root = ET.parse(path).getroot()

    name = root.findtext("gpx:trk/gpx:name", default="Activity", namespaces=NS)
    activity_type = root.findtext("gpx:trk/gpx:type", default="unknown", namespaces=NS)

    points: list[TrackPoint] = []
    for point in root.findall(".//gpx:trkpt", namespaces=NS):
        timestamp = point.findtext("gpx:time", namespaces=NS)
        elevation = point.findtext("gpx:ele", namespaces=NS)

        points.append(
            TrackPoint(
                lat=float(point.attrib["lat"]),
                lon=float(point.attrib["lon"]),
                elevation=float(elevation) if elevation is not None else None,
                time=parse_time(timestamp),
            )
        )

    if len(points) < 2:
        raise ValueError("GPX contains fewer than 2 track points")

    return Activity(name=name, type=activity_type, points=points)
