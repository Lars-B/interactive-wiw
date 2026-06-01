from dash import Input, Output, html

from wiw_app.app import app as myapp
from wiw_app.dash_logger import logger
from wiw_app.layouts.upload import breath, transphylo, outbreaker_rds, custom_csv, metadata


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
            return breath
        case "transphylo":
            return transphylo
        case "outbreaker":
            return outbreaker_rds
        case "metadata":
            return metadata
        case "custom-csv":
            return custom_csv
        case _:
            return wip
