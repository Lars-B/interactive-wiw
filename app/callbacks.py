import dash_bootstrap_components as dbc
from dash import Input, Output, State
from dash import html
from dash.dependencies import ALL
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import ThemeSwitchAIO

from .app import app as myapp
from .graph_elements import build_graph, get_node_style, get_cytoscape_style, get_edge_style, \
    build_graph_from_file


@myapp.callback(
    Output('cytoscape', 'elements'),
    Output('cytoscape', 'layout'),
    Output('cytoscape', 'stylesheet'),
    Output('cytoscape', 'style'),
    Input("graph-store", "data"),
    Input('label-filter', 'value'),
    Input('layout-selector', 'value'),
    Input('scale-width-toggle', 'value'),
    Input('edge-annotation-selector', 'value'),
    Input("edge-label-position", "value"),
    Input('weight-threshold', 'value'),
    Input("color-by-label-toggle", "value"),
    Input("label-color-store", "data"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def update_elements(graph_data, selected_labels, selected_layout, scale_toggle, annotation_field,
                    label_position, threshold, color_toggle, label_colors, is_light_theme):
    cy_style = get_cytoscape_style(is_light_theme)
    scale_edges = "scale" in scale_toggle
    scale = 5 if scale_edges else 1

    threshold = min(max(threshold or 0, 0), 1)

    # if not graph_data:
    print(graph_data)
    nodes, edges = build_graph(scale_factor=scale, label_colors=label_colors)

    filtered_edges = [e for e in edges if e["data"]["label"] in selected_labels
                      and e["data"].get("weight", 0) >= threshold]
    # todo add it to dcc store graph data
    # todo then use that for plotting?....

    elements = nodes + filtered_edges
    layout = {"name": selected_layout}

    stylesheet = [
        {"selector": "node",
         "style": get_node_style()},
        {"selector": "edge", "style": get_edge_style(annotation_field,
                                                     label_position,
                                                     scale_edges,
                                                     color_toggle,
                                                     is_light_theme)},
    ]

    # print("--- DEBUG ---")
    # print("Elements (first 2):", elements[:2])  # Show first two elements
    # print("Layout:", layout)
    # print("Stylesheet:", stylesheet)
    # print("Style:", cy_style)
    # print("------------------")

    return elements, layout, stylesheet, cy_style


myapp.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks) {
            const container = document.querySelector('[id="cytoscape"]');
            const cy = container && container._cyreg && container._cyreg.cy;
            if (cy) {
                cy.fit();
            }
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('cytoscape', 'elements', allow_duplicate=True),
    Input('recenter-btn', 'n_clicks'),
    prevent_initial_call=True
)


@myapp.callback(
    Output("color-pickers-container", "children"),
    Input("graph-store", "data")  # or trigger when scale/layout/etc. change
)
def generate_color_pickers(_):
    _, edges = build_graph()
    labels = sorted(set(edge["data"]["label"] for edge in edges))
    default_colors = {
        "set1": "#2ECC40",
        "set2": "#0074D9"
    }

    my_color_picker = html.Div(
        style={
            "maxHeight": "300px",  # approx height for ~6 rows, adjust as needed
            "overflowY": "auto",
            "overflowX": "hidden",
            "width": "100%",
            "border": "1px solid #ddd",
            "padding": "5px"
        },
        children=[
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Input(
                            id={"type": "color-input", "index": label},
                            type="color",
                            value=default_colors.get(label, "#AAAAAA"),
                            style={"width": 60, "height": 40, "marginBottom": "2px", "padding": 0,
                                   "border": "none"}
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        dbc.Label(label, style={"lineHeight": "35px", "marginLeft": "10px"}),
                        width="auto",
                    ),
                ],
                align="center",  # vertically center row items
                style={"marginBottom": "8px"},
                key=label
            )
            for label in labels
        ]
    )
    return my_color_picker


@myapp.callback(
    Output("label-color-store", "data"),
    Input({"type": "color-input", "index": ALL}, "value"),
    State({"type": "color-input", "index": ALL}, "id")
)
def collect_colors(values, ids):
    return {id["index"]: val for id, val in zip(ids, values)}


@myapp.callback(
    Output("color-pickers-collapse", "is_open"),
    Input("color-by-label-toggle", "value"),
)
def toggle_color_pickers(toggle_values):
    # Show if 'color' is in checklist values, else hide
    return "color" in toggle_values


@myapp.callback(
    Output("uploaded-datasets-store", "data", allow_duplicate=True),
    Input("confirm-dataset-btn", "n_clicks"),
    State("upload-data", "contents"),
    State("upload-data", "filename"),
    State("dataset-label", "value"),
    State("dataset-color", "value"),
    State("uploaded-datasets-store", "data"),
    prevent_initial_call=True
)
def store_uploaded_dataset(n_clicks, contents, filename, label, color, existing_data):
    if not contents or not label:
        raise PreventUpdate

    new_dataset = {
        "filename": filename,
        "contents": contents,  # base64 string
        "label": label,
        "color": color,
    }

    existing_data = existing_data or []
    existing_data.append(new_dataset)
    return existing_data


@myapp.callback(
    Output("selected-filename", "children"),
    Input("upload-data", "filename"),
)
def display_filename(filename):
    if filename:
        return f"Selected file: {filename}"
    return "No file selected yet."


@myapp.callback(
    Output("graph-store", "data", allow_duplicate=True),
    Input("confirm-dataset-btn", "n_clicks"),
    State("upload-data", "contents"),
    State("dataset-label", "value"),
    State("dataset-color", "value"),
    State("graph-store", "data"),
    prevent_initial_call=True
)
def update_graph_with_dataset(n_clicks, contents, label, color, current_graph_data):
    if not contents or not label:
        raise PreventUpdate

    # Decode the uploaded file
    # content_type, content_string = contents.split(',')
    # decoded = base64.b64decode(content_string).decode("utf-8")
    #
    # # Replace this with actual logic based on your file format
    # try:
    #     data = json.loads(decoded)  # or CSV parser, etc.
    # except Exception as e:
    #     print("File parsing error:", e)
    #     raise PreventUpdate

    print(f"Got label: {label}")
    print(f"Got color: {color}")
    print(f"Got file: {current_graph_data}")

    # Custom logic to generate new nodes/edges
    # todo figure out how to pass along the filename
    data = {}
    new_nodes, new_edges = build_graph_from_file(data, label, color)

    # Merge with current graph (if any)
    current_graph_data = current_graph_data or {"nodes": [], "edges": []}
    all_nodes = current_graph_data["nodes"] + new_nodes
    all_edges = current_graph_data["edges"] + new_edges

    print(all_nodes)
    print(all_edges)
    print("------")
    print(f"Got file: {current_graph_data}")
    print("------")

    return {"nodes": all_nodes, "edges": all_edges}
