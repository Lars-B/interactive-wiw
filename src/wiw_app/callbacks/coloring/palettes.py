from datetime import datetime
import re
import colorsys

from matplotlib import colormaps
from matplotlib.colors import to_hex

from wiw_app.dash_logger import logger

# hard coded color palettes to use
PLOTLY_10 = [
    "#636EFA",
    "#EF553B",
    "#00CC96",
    "#AB63FA",
    "#FFA15A",
    "#19D3F3",
    "#FF6692",
    "#B6E880",
    "#FF97FF",
    "#FECB52",
]

D3_20 = [
    "#1F77B4",
    "#FF7F0E",
    "#2CA02C",
    "#D62728",
    "#9467BD",
    "#8C564B",
    "#E377C2",
    "#7F7F7F",
    "#BCBD22",
    "#17BECF",
    "#393B79",
    "#637939",
    "#8C6D31",
    "#843C39",
    "#7B4173",
    "#3182BD",
    "#31A354",
    "#756BB1",
    "#636363",
    "#E6550D",
]


def generate_hsv_palette(n):
    """
    Generate n visually separated colors.

    Used when predefined categorical palettes are exhausted.
    """
    colors = []

    for i in range(n):
        hue = i / n
        rgb = colorsys.hsv_to_rgb(hue, 0.65, 0.9)

        colors.append(
            "#{:02x}{:02x}{:02x}".format(
                int(rgb[0] * 255),
                int(rgb[1] * 255),
                int(rgb[2] * 255),
            )
        )

    return colors


def categorical_palette(n):
    """
    Select an appropriate categorical palette.

    Small numbers:
        use curated colors

    Larger numbers:
        generate additional colors
    """
    if n <= len(PLOTLY_10):
        return PLOTLY_10[:n]

    if n <= len(D3_20):
        return D3_20[:n]

    return generate_hsv_palette(n)


def assign_default_colors(labels):
    """
    Assign deterministic colors to labels.
    """
    labels = sorted(labels)

    colors = categorical_palette(len(labels))

    return {
        label: color
        for label, color in zip(labels, colors)
    }


def natural_sort_key(value):
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", str(value))
    ]


def assign_heatmap_colors(labels, colormap):
    values, strategy = interpret_labels(labels)

    logger.info(f"Selected heatmap strategy: {strategy}")

    cmap = colormaps[colormap]

    min_value = min(values)
    max_value = max(values)

    if min_value == max_value:
        normalized = [0.5] * len(values)
    else:
        normalized = [
            (value - min_value) / (max_value - min_value)
            for value in values
        ]

    return {
        label: to_hex(cmap(value))
        for label, value in zip(labels, normalized)
    }


def interpret_labels(labels):
    try:
        values = [float(label) for label in labels]
        return values, "numeric"
    except ValueError:
        pass

    try:
        values = parse_dates(labels)
        return values, "date"
    except ValueError:
        pass

    return list(range(len(labels))), "ordinal"


def parse_dates(labels):
    """
    Parse labels as dates and return Unix timestamps.
    """
    timestamps = []

    date_formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
    ]

    for label in labels:
        for fmt in date_formats:
            try:
                dt = datetime.strptime(str(label), fmt)
                timestamps.append(dt.timestamp())
                break
            except ValueError:
                continue
        else:
            raise ValueError(f"Could not parse '{label}' as a supported date.")

    return timestamps
