import re
import colorsys


# Good small categorical palettes
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

# Expand later if needed
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
