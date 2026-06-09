import dash_bootstrap_components as dbc
from dash import html

from wiw_app.ids import UploadIDs


def make_loading_modal(modal_id, title="Processing Dataset"):
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle(title)),
            dbc.ModalBody([
                html.P("Please wait while we process your file..."),
                html.Div(
                    dbc.Spinner(size="md", color="primary", type="border"),
                    style={"display": "flex", "justifyContent": "center"},
                ),
                html.Hr(),
                html.Small(
                    "This dialog should close automatically when processing completes. "
                    "If it remains open after results appear, you can safely close it.",
                    style={"color": "#888"},
                ),
            ]),
        ],
        id=modal_id,
        is_open=False,
        backdrop="static",
        keyboard=False,
        centered=True,
    )


data_loading_modal = make_loading_modal(
    UploadIDs.breath_trees.LOADING_MODAL,
    title="Processing BREATH Dataset"
)

data_loading_modal_tp = make_loading_modal(
    UploadIDs.transphylo_rds.LOADING_MODAL,
    title="Processing TransPhylo Dataset"
)

data_loading_modal_outbreaker = make_loading_modal(
    UploadIDs.outbreaker_rds.LOADING_MODAL,
    title="Processing outbreaker2 Dataset"
)
