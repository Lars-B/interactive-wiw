from dash import Input, Output


def register_filename_display_callback(app, ids):
    @app.callback(
        Output(ids.SELECTED_FILENAME, "children"),
        Output(ids.DATASET_LABEL, "value"),
        Input(ids.UPLOAD_DATA, "filename"),
    )
    def _update(filename):
        if filename:
            return f"Selected file: {filename}", filename
        return "No file selected yet.", ""
