import networkx as nx
from dash import Input, Output, State, dcc, ctx
from networkx.drawing.nx_pydot import to_pydot

from wiw_app.app import app as myapp
from wiw_app.dash_logger import logger


@myapp.callback(
    Output("download-dot", 'data'),
    Input("btn-get-dot", "n_clicks"),
    Input("image-filename-input", "value"),
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
        Input("image-filename-input", "value")
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
