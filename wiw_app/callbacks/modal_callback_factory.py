from dash import Input, Output, State, ctx

from wiw_app.app import app as myapp


def make_loading_modal_callback(prefix):
    @myapp.callback(
        Output(prefix.LOADING_MODAL, "is_open"),
        Input(prefix.CONFIRM_BUTTON, "n_clicks"),
        State(prefix.LOADING_MODAL, "is_open"),
        State(prefix.UPLOAD_DATA, "contents"),
        prevent_initial_call=True,
    )
    def _toggle(n_clicks, is_open, contents):
        if ctx.triggered_id == prefix.CONFIRM_BUTTON and contents:
            return True
        return is_open
