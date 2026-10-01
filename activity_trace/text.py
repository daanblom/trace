from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .activity import Activity, format_duration, format_pace


FONT_CANDIDATES = [
    "/usr/share/fonts/ClashGrotesk_Complete/Fonts/TTF/ClashGrotesk-Variable.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
]


def default_font_path() -> str:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return path
    raise RuntimeError(
        "No default bold font found. Pass --font /path/to/font.ttf."
    )


def _font(path: str | None, size: int):
    return ImageFont.truetype(path or default_font_path(), size=size)


def draw_stats(
    image: Image.Image,
    activity: Activity,
    font_path: str | None = None,
    margin: int = 100,
    stat_size: int = 1200,
    label_size: int = 40,
    line_gap: int = 10,
):
    result = image.convert("RGBA")
    draw = ImageDraw.Draw(result)

    stats = [
        ("Distance", f"{activity.distance_km:.2f} KM"),
        ("Time", format_duration(activity.moving_time_s)),
    ]

    activity_type = activity.type.lower()
    if activity_type in {"run", "running"}:
        stats.append(("Pace", format_pace(activity.average_pace_min_km)))
    else:
        stats.append(("Average speed", f"{activity.average_speed_kmh:.1f} KM/H"))

    stats.append(("Elevation", f"+{activity.elevation_gain_m:.0f} M"))

    value_font = _font(font_path, stat_size)
    label_font = _font(font_path, label_size)

    x = margin
    y = image.height - margin

    # line_gap = 10

    # Define color for text 
    def getTextColor(colorscheme):
        if colorscheme == "dark":
            textcolor = (255, 255, 255)  # white text for dark background
        elif colorscheme == "light":
            textcolor = (0, 0, 0)  # black text for light background
        else:
            print("Invalid colorscheme.")

        return textcolor

    textColor = getTextColor("light") 

    # Draw from bottom upward so additional stats remain easy to add later.
    for label, value in reversed(stats):
        bbox = draw.textbbox((x, y), value, font=value_font)
        value_height = bbox[3] - bbox[1]
        y -= value_height
        draw.text((x, y), value, font=value_font, fill=(textColor))
        y -= line_gap

        bbox = draw.textbbox((x, y), label, font=label_font)
        label_height = bbox[3] - bbox[1]
        y -= label_height
        draw.text((x, y), label, font=label_font, fill=(textColor))
        y -= stat_size // 2


        print("font:", font_path or default_font_path())
        print("stat size:", stat_size)
        print("label size:", label_size)
    return result
