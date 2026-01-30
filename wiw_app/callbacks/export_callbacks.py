import io

import networkx as nx
from dash import Input, Output, State, dcc, ctx, dash
from networkx.drawing.nx_pydot import to_pydot

from wiw_app.app import app as myapp
from wiw_app.dash_logger import logger
from wiw_app.ids import GraphOptions
from wiw_app.plotting_utils import (make_image_with_legend_png,
                                    extract_color_map_from_pallete,
                                    draw_legend)


@myapp.callback(
    Output("download-dot", 'data'),
    Input("btn-get-dot", "n_clicks"),
    State("image-filename-input", "value"),
    State("cytoscape", "elements"),
    prevent_initial_call=True
)
def export_to_dot(n_clicks, filename, elements):
    logger.info("Exporting to dot...")
    G = nx.DiGraph()
    for el in elements:
        data = el.get("data", {})
        if "source" in data and "target" in data:
            G.add_edge(data["source"], data["target"], **data)
        elif "id" in data:
            G.add_node(data["id"], **data)
    logger.info("Writing current graph to dot string...")
    dot_str = to_pydot(G).to_string()
    logger.info("Returning dot string for download...")
    return dcc.send_string(dot_str, f"{filename}.dot")


@myapp.callback(
    Output("cytoscape", "generateImage"),
    [
        Input("btn-get-jpg", "n_clicks"),
        Input("btn-get-png", "n_clicks"),
        Input("btn-get-svg", "n_clicks"),
        State("image-filename-input", "value")
    ]
)
def get_image(get_jpg_clicks, get_png_clicks, get_svg_clicks, filename):
    action = 'store'
    ftype = 'png'
    filename = filename.strip()

    if ctx.triggered_id and ctx.triggered_id.startswith("btn-get-"):
        action = "download"
        ftype = ctx.triggered_id.split("-")[-1]

    return {
        'type': ftype,
        'action': action,
        "filename": filename
    }


@myapp.callback(
    Output("cytoscape", "generateImage", allow_duplicate=True),
    Output("pngplus-requested", "data"),
    Input("btn-get-pngplus", "n_clicks"),
    prevent_initial_call=True
)
def trigger_pngplus(n):
    return {
        "type": "png",
        "action": "store",
    }, True


@myapp.callback(
    Output("download-pngplus", "data"),
    Output("pngplus-requested", "data", allow_duplicate=True),
    State("pngplus-requested", "data"),
    Input("cytoscape", "imageData"),
    State("image-filename-input", "value"),
    State(GraphOptions.Nodes.COLOR_PICKER_CONTAINERS, "children"),
    State(GraphOptions.Nodes.COLOR_BY_LABEL, "value"),
    State(GraphOptions.Nodes.COLOR_LABEL_SELECTOR, "value"),
    State(GraphOptions.Nodes.COLOR_LABEL_SELECTOR, "options"),
    State(GraphOptions.Edges.COLOR_PICKER_CONTAINERS, "children"),
    State(GraphOptions.Edges.COLOR_BY_LABEL, "value"),
    prevent_initial_call=True
)
def export_pngplus(requested,
                   image_data,
                   filename,
                   node_color_container, node_color_toggle, node_color_title, node_color_options,
                   edge_color_container, edge_color_toggle
                   ):
    if not requested:
        return dash.no_update, False

    proper_title = next(
        opt["label"] for opt in node_color_options if opt["value"] == node_color_title
    )

    node_colors = None
    if node_color_toggle:
        node_colors = extract_color_map_from_pallete(node_color_container)

    edge_colors = None
    if edge_color_toggle:
        edge_colors = extract_color_map_from_pallete(edge_color_container)

    full_img = make_image_with_legend_png(image_data, node_colors, proper_title, edge_colors)

    buffer = io.BytesIO()
    full_img.save(buffer, format="PNG")
    buffer.seek(0)

    return (
        dcc.send_bytes(buffer.read(), f"{filename}-legend.png"),
        False
    )


@myapp.callback(
    Output("download-legend", "data"),
    Input("btn-get-legend", "n_clicks"),
    State(GraphOptions.Nodes.COLOR_PICKER_CONTAINERS, "children"),
    State(GraphOptions.Nodes.COLOR_BY_LABEL, "value"),
    State(GraphOptions.Nodes.COLOR_LABEL_SELECTOR, "value"),
    State(GraphOptions.Nodes.COLOR_LABEL_SELECTOR, "options"),
    State(GraphOptions.Edges.COLOR_PICKER_CONTAINERS, "children"),
    State(GraphOptions.Edges.COLOR_BY_LABEL, "value"),
    prevent_initial_call=True
)
def export_legend(
        n_clicks,
        node_color_container, node_color_toggle, node_color_title, node_color_options,
        edge_color_container, edge_color_toggle
):
    logger.debug("Exporting legend...")

    proper_title = next(
        opt["label"] for opt in node_color_options if opt["value"] == node_color_title
    )

    node_colors = None
    if node_color_toggle:
        node_colors = extract_color_map_from_pallete(node_color_container)

    edge_colors = None
    if edge_color_toggle:
        edge_colors = extract_color_map_from_pallete(edge_color_container)

    legend = draw_legend(node_colors, proper_title, edge_colors, svg=True)

    logger.debug("Generated legend...")
    logger.debug(legend)

    return {
        "content": legend,
        "filename": "legend.svg",  # todo might become input option in the future...
        "type": "image/svg+xml",
    }
