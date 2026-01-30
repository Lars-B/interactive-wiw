import base64
import io
import time
from contextlib import contextmanager

from PIL import Image, ImageDraw, ImageFont

from wiw_app.dash_logger import logger

DEFAULT_COLOR_PALETTE = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
]


def assign_default_colors(labels):
    """Assigns a default color per label deterministically"""
    unique_labels = sorted(set(labels))
    return {
        label: DEFAULT_COLOR_PALETTE[i % len(DEFAULT_COLOR_PALETTE)]
        for i, label in enumerate(unique_labels)
    }


@contextmanager
def log_time(label="Operation"):
    start = time.time()
    yield
    duration = time.time() - start
    logger.info(f"{label} took {duration:.2f} seconds")


def draw_legend(node_colors, node_color_title, edge_colors):
    width = 200

    row_height = 30  # height of one legend row
    title_height = 30  # height of a section title ("Node shapes", etc)
    padding = 20  # top/bottom padding
    base_height = 3 * row_height + title_height + padding

    height = base_height \
             + row_height * (len(node_colors) if node_colors else 0) \
             + row_height * (len(edge_colors) if edge_colors else 0)

    legend = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(legend)

    # todo can add size=x here, but that screws up the position and currently does not fit...
    font = ImageFont.load_default()

    y = 10
    spacing = 25
    size = 15

    # --- Node Shapes (hard-coded three) ---
    draw.text((10, y), "Node Shapes:", fill="black", font=font)
    y += spacing

    # Rectangle → Terminal Node
    draw.rectangle([20, y, 20 + size, y + size], fill="gray")
    draw.text((50, y), "Terminal (in or out)", fill="black", font=font)
    y += spacing

    # Triangle → Unseen Node
    draw.polygon([
        (20 + size / 2, y),
        (20, y + size),
        (20 + size, y + size)
    ], fill="gray")
    draw.text((50, y), "Isolated", fill="black", font=font)
    y += spacing

    # Ellipse → Seen Node
    draw.ellipse([20, y, 20 + size, y + size], fill="gray")
    draw.text((50, y), "Regular", fill="black", font=font)
    y += spacing + 10  # extra space before next section

    if node_colors:
        # --- Node Colors ---
        draw.text((10, y), f"Node Colors by {node_color_title}:", fill="black", font=font)
        y += spacing
        for label, color in node_colors.items():
            draw.rectangle([20, y, 40, y + 15], fill=color)
            draw.text((45, y), label, fill="black", font=font)
            y += spacing

        y += 10  # small extra space

    if edge_colors:
        # --- Edge Colors ---
        draw.text((10, y), "Edge Colors:", fill="black", font=font)
        y += spacing
        for label, color in edge_colors.items():
            draw.line([20, y + 7, 40, y + 7], fill=color, width=3)
            draw.text((45, y), label, fill="black", font=font)
            y += spacing

    return legend


def make_image_with_legend_png(image_data, node_colors, node_color_title, edge_colors):
    header, encoded = image_data.split(",")
    img_bytes = base64.b64decode(encoded)
    graph_img = Image.open(io.BytesIO(img_bytes))

    graph_img = graph_img.convert("RGBA")

    legend = draw_legend(node_colors, node_color_title, edge_colors)

    combined_height = max(graph_img.height, legend.height)
    combined = Image.new(
        "RGBA",
        (graph_img.width + legend.width, combined_height),
        (255, 255, 255, 255)
    )
    combined.paste(graph_img, (0, 0))
    combined.paste(legend, (graph_img.width, 0))

    return combined.convert("RGB")


def extract_color_map_from_pallete(container):
    color_map = {}

    for row in container["props"]["children"]:
        cols = row["props"]["children"]

        # color
        color_input = cols[0]["props"]["children"]["props"]
        color_value = color_input["value"]

        # label: could be Label (nodes) or Input (edges)
        label_component = cols[1]["props"]["children"]["props"]

        if "children" in label_component:
            # node case (Label)
            label = label_component["children"]
        else:
            # edge case (Input)
            label = label_component["value"]

        color_map[label] = color_value

    return color_map
