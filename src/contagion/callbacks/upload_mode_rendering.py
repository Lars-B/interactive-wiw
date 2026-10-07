from dash import Input, Output, html

from contagion.app import app as myapp
from contagion.dash_logger import logger
from contagion.layouts.upload import metadata, build_upload_panel
from contagion.ids import UploadIDs

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
        case "scotti":
            return build_upload_panel(
                UploadIDs.scotti_trees,
                accepted_files=".trees, .tree, .tre",
                include_burnin_slider=True
            )
        case "transphylo":
            return build_upload_panel(
                UploadIDs.transphylo_rds,
                accepted_files=".rds, .RDS, Rds",
                include_burnin_slider=True,
                input_types=[
                    ("MCMC chain", "mcmc"),
                    ("WIW matrix", "wiw_matrix"),
                ]
            )
        case "outbreaker2":
            return build_upload_panel(
                UploadIDs.outbreaker_rds,
                accepted_files=".rds, .RDS, Rds"
            )
        case "metadata":
            return metadata
        case "custom-csv":
            return build_upload_panel(
                UploadIDs.custom_csv,
                accepted_files=".csv"
            )
        case "dot-file":
            return build_upload_panel(
                UploadIDs.dot_file,
                accepted_files=".dot, .gv"
            )
        case _:
            return wip
