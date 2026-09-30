from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TrackPoint:
    lat: float
    lon: float
    elevation: float | None = None
    time: datetime | None = None


@dataclass
class Activity:
    name: str
    type: str
    points: list[TrackPoint] = field(default_factory=list)

    distance_m: float = 0.0
    duration_s: float = 0.0
    moving_time_s: float = 0.0
    average_speed_kmh: float = 0.0
    max_speed_kmh: float = 0.0
    elevation_gain_m: float = 0.0
    elevation_loss_m: float = 0.0

    @property
    def distance_km(self) -> float:
        return self.distance_m / 1000.0

    @property
    def average_pace_min_km(self) -> float | None:
        if self.distance_km <= 0 or self.moving_time_s <= 0:
            return None
        return self.moving_time_s / 60.0 / self.distance_km


def format_duration(seconds: float) -> str:
    total = max(0, int(round(seconds)))
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def format_pace(seconds_per_km: float | None) -> str:
    if seconds_per_km is None:
        return "—"
    total_seconds = max(0, int(round(seconds_per_km)))
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes}:{seconds:02d} /km"
