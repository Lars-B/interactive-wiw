import dash_bootstrap_components as dbc
from dash import html

from wiw_app.ids import UploadIDs

data_loading_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Processing Dataset")),
        dbc.ModalBody([
            html.P("Please wait while we process your file..."),
            dbc.Spinner(size="md", color="primary", type="border"),
        ]),
    ],
    id=UploadIDs.breath_trees.LOADING_MODAL,
    is_open=False,
    backdrop="static",  # prevents closing by clicking outside
    keyboard=False,  # disables Esc key
    centered=True,
)

data_loading_modal_tp = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Processing Dataset")),
        dbc.ModalBody([
            html.P("Please wait while we process your file..."),
            dbc.Spinner(size="md", color="primary", type="border"),
        ]),
    ],
    id=UploadIDs.transphylo_rds.LOADING_MODAL,
    is_open=False,
    backdrop="static",  # prevents closing by clicking outside
    keyboard=False,  # disables Esc key
    centered=True,
)

data_loading_modal_outbreaker = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Processing Dataset")),
        dbc.ModalBody([
            html.P("Please wait while we process your file..."),
            dbc.Spinner(size="md", color="primary", type="border"),
        ]),
    ],
    id=UploadIDs.outbreaker_rds.LOADING_MODAL,
    is_open=False,
    backdrop="static",  # prevents closing by clicking outside
    keyboard=False,  # disables Esc key
    centered=True,
)
