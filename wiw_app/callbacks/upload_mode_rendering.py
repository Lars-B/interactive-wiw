from dash import Input, Output, html

from wiw_app.app import app as myapp
from wiw_app.dash_logger import logger
from wiw_app.layouts import breath_upload, oubreaker_rds_upload, custom_csv_upload, metadata_upload


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
            return breath_upload
        case "transphylo":
            return wip
        case "outbreaker":
            return oubreaker_rds_upload
        case "metadata":
            return metadata_upload
        case "custom-csv":
            return custom_csv_upload
        case _:
            return wip
