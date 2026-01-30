import base64
import io
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont


@dataclass
class LegendItem:
    kind: str
    label: str = ""
    color: str = "gray"


def build_legend_items(legend_spec):
    items = []

    # Node shapes
    items.append(LegendItem("title", "Node Shapes"))
    items.append(LegendItem("rect", "Terminal (in or out)"))
    items.append(LegendItem("triangle", "Isolated"))
    items.append(LegendItem("ellipse", "Regular"))

    # Node colors
    node_colors = legend_spec.get("node_colors")
    if node_colors:
        items.append(LegendItem("title", f"Node Colors by {legend_spec['node_color_title']}"))
        for label, color in node_colors.items():
            items.append(LegendItem("rect", label, color))

    # Edge colors
    edge_colors = legend_spec.get("edge_colors")
    if edge_colors:
        items.append(LegendItem("title", "Edge Colors"))
        for label, color in edge_colors.items():
            items.append(LegendItem("line", label, color))

    return items


def render_legend_pil(items, width=200):
    # row_height = 30
    spacing = 25
    size = 15

    height = 20 + spacing * len(items)
    legend = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(legend)
    font = ImageFont.load_default()

    y = 20

    for item in items:
        if item.kind == "title":
            draw.text((10, y), item.label + ":", fill="black", font=font)

        else:
            if item.kind == "rect":
                draw.rectangle([20, y, 20 + size, y + size], fill=item.color)

            elif item.kind == "triangle":
                draw.polygon([
                    (20 + size / 2, y),
                    (20, y + size),
                    (20 + size, y + size)
                ], fill=item.color)

            elif item.kind == "ellipse":
                draw.ellipse([20, y, 20 + size, y + size], fill=item.color)

            elif item.kind == "line":
                draw.line([20, y + 7, 40, y + 7], fill=item.color, width=3)

            draw.text((50, y), item.label, fill="black", font=font)

        y += spacing

    return legend


def render_legend_svg(items, width=200):
    spacing = 25
    size = 15
    y = 20
    elements = []

    def text(x, y, s, bold=False):
        weight = "bold" if bold else "normal"
        return f'<text x="{x}" y="{y}" font-size="12" font-weight="{weight}" fill="black">{s}</text>'

    for item in items:
        if item.kind == "title":
            elements.append(text(10, y, item.label + ":", bold=True))

        else:
            if item.kind == "rect":
                elements.append(
                    f'<rect x="20" y="{y - 12}" width="{size}" height="{size}" fill="{item.color}"/>')

            elif item.kind == "triangle":
                elements.append(
                    f'<polygon points="{20 + size / 2},{y - 12} 20,{y - 12 + size} {20 + size},{y - 12 + size}" fill="{item.color}"/>'
                )

            elif item.kind == "ellipse":
                elements.append(
                    f'<ellipse cx="{20 + size / 2}" cy="{y - 12 + size / 2}" rx="{size / 2}" ry="{size / 2}" fill="{item.color}"/>'
                )

            elif item.kind == "line":
                elements.append(
                    f'<line x1="20" y1="{y - 7}" x2="40" y2="{y - 7}" stroke="{item.color}" stroke-width="3"/>'
                )

            elements.append(text(50, y, item.label))

        y += spacing

    height = y + 10

    return f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
        {''.join(elements)}
    </svg>
    """


def compute_legend_spec(
        node_color_options,
        node_color_title,
        node_color_toggle,
        node_color_container,
        edge_color_toggle,
        edge_color_container,
):
    """Compute the node/edge legend info as a neutral object."""

    proper_title = next(
        opt["label"] for opt in node_color_options
        if opt["value"] == node_color_title
    )

    node_colors = None
    if node_color_toggle:
        node_colors = extract_color_map_from_pallete(node_color_container)

    edge_colors = None
    if edge_color_toggle:
        edge_colors = extract_color_map_from_pallete(edge_color_container)

    # Return a simple dictionary describing everything
    return {
        "node_color_title": proper_title,
        "node_colors": node_colors,
        "edge_colors": edge_colors,
    }


def draw_legend(
        node_color_options,
        node_color_title,
        node_color_toggle,
        node_color_container,
        edge_color_toggle,
        edge_color_container,
        svg=False
):
    spec = compute_legend_spec(
        node_color_options,
        node_color_title,
        node_color_toggle,
        node_color_container,
        edge_color_toggle,
        edge_color_container,
    )
    items = build_legend_items(spec)
    if svg:
        return render_legend_svg(items)
    else:
        return render_legend_pil(items)


def make_image_with_legend_png(
        image_data,
        node_color_options,
        node_color_title,
        node_color_toggle,
        node_color_container,
        edge_color_toggle,
        edge_color_container,
):
    header, encoded = image_data.split(",")
    img_bytes = base64.b64decode(encoded)
    graph_img = Image.open(io.BytesIO(img_bytes))

    graph_img = graph_img.convert("RGBA")

    legend = draw_legend(
        node_color_options,
        node_color_title,
        node_color_toggle,
        node_color_container,
        edge_color_toggle,
        edge_color_container,
        svg=False
    )

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

    # Robustness for when nothing is in the graph.
    if ("No " in container["props"]["children"] and
            "data loaded." in container["props"]["children"]):
        return color_map

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
