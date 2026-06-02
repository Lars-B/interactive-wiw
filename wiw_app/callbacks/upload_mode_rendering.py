from dash import Input, Output, html

from wiw_app.app import app as myapp
from wiw_app.dash_logger import logger
from wiw_app.layouts.upload import metadata, build_upload_panel
from wiw_app.ids import UploadIDs

@myapp.callback(
    Output("upload-ui-container", "children"),
    Input("upload-mode-selector", "value")
)
def render_upload_ui(mode):
    logger.debug(f'This is being loaded with mode: {mode}')
    wip = html.Div([
        html.H5("WIP"),
        html.P("This mode is not implemented yet.")
    ])
    match mode:
        case "breath":
            return build_upload_panel(
                UploadIDs.breath_trees,
                accepted_files=".trees, .tree, .tre",
                include_burnin_slider=True
            )
        case "transphylo":
            return build_upload_panel(
                UploadIDs.transphylo_rds,
                accepted_files=".rds, .Rdata, .RData",
                include_burnin_slider=True
            )
        case "outbreaker":
            return build_upload_panel(
                UploadIDs.outbreaker_rds,
                accepted_files=".rds, .Rdata, .RData"
            )
        case "metadata":
            return metadata
        case "custom-csv":
            return build_upload_panel(
                UploadIDs.custom_csv,
                accepted_files=".csv"
            )
        case _:
            return wip
