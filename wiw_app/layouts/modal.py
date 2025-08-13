import dash_bootstrap_components as dbc
from dash import html

data_loading_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Processing Dataset")),
        dbc.ModalBody([
            html.P("Please wait while we process your file..."),
            dbc.Spinner(size="md", color="primary", type="border"),
        ]),
    ],
    id="loading-modal",
    is_open=False,
    backdrop="static",  # prevents closing by clicking outside
    keyboard=False,  # disables Esc key
    centered=True,
)
