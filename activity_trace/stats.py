from math import atan2, cos, radians, sin, sqrt

from .activity import Activity

EARTH_RADIUS_M = 6_371_000.0
MOVING_SPEED_THRESHOLD_KMH = 1.0
MAX_REASONABLE_SPEED_KMH = 150.0
MIN_ELEVATION_DELTA_M = 1.0


def haversine_m(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    phi1 = radians(lat1)
    phi2 = radians(lat2)
    d_phi = radians(lat2 - lat1)
    d_lambda = radians(lon2 - lon1)

    a = (
        sin(d_phi / 2) ** 2
        + cos(phi1) * cos(phi2) * sin(d_lambda / 2) ** 2
    )
    return 2 * EARTH_RADIUS_M * atan2(sqrt(a), sqrt(max(0.0, 1.0 - a)))


def calculate_stats(activity: Activity) -> Activity:
    points = activity.points
    total_distance = 0.0
    moving_time = 0.0
    max_speed = 0.0
    elevation_gain = 0.0
    elevation_loss = 0.0

    for a, b in zip(points, points[1:]):
        distance = haversine_m(a.lon, a.lat, b.lon, b.lat)
        total_distance += distance

        if a.elevation is not None and b.elevation is not None:
            delta = b.elevation - a.elevation
            if delta >= MIN_ELEVATION_DELTA_M:
                elevation_gain += delta
            elif delta <= -MIN_ELEVATION_DELTA_M:
                elevation_loss += -delta

        if a.time is not None and b.time is not None:
            dt = (b.time - a.time).total_seconds()
            if dt > 0:
                speed_kmh = (distance / 1000.0) / (dt / 3600.0)
                # Ignore GPS spikes for max speed and moving-time classification.
                if speed_kmh <= MAX_REASONABLE_SPEED_KMH:
                    max_speed = max(max_speed, speed_kmh)
                    if speed_kmh >= MOVING_SPEED_THRESHOLD_KMH:
                        moving_time += dt

    duration = 0.0
    if points[0].time is not None and points[-1].time is not None:
        duration = max(0.0, (points[-1].time - points[0].time).total_seconds())

    activity.distance_m = total_distance
    activity.duration_s = duration
    activity.moving_time_s = moving_time if moving_time else duration
    activity.average_speed_kmh = (
        (total_distance / 1000.0) / (activity.moving_time_s / 3600.0)
        if activity.moving_time_s > 0
        else 0.0
    )
    activity.max_speed_kmh = max_speed
    activity.elevation_gain_m = elevation_gain
    activity.elevation_loss_m = elevation_loss
    return activity
