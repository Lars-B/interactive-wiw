from dash import Input, Output, html
from wiw_app.app import app as myapp
from wiw_app.dash_logger import logger
from wiw_app.layouts.breath_upload_tabs import breath_upload_tabs
from wiw_app.layouts.outbreaker2_upload import outbreaker_upload

@myapp.callback(
    Output("upload-ui-container", "children"),
    Input("upload-mode-selector", "value")
)
def render_upload_ui(mode):
    logger.debug(f'This is being loaded with mode: {mode}')
    if mode == "breath":
        return breath_upload_tabs

    elif mode == "transphylo":
        return html.Div([
            html.H5("WIP"),
            html.P("This mode is not implemented yet.")
        ])

    elif mode == "outbreaker":
        return outbreaker_upload

    elif mode == "empty":
        return html.Div([
            html.H5("WIP"),
            html.P("This mode is not implemented yet.")
        ])

    return html.Div()