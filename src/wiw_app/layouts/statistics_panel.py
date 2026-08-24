import dash_bootstrap_components as dbc
from dash import html
from wiw_app.ids import GraphStatistics


def create_statistics_panel():
    return dbc.Offcanvas(
        id=GraphStatistics.PANEL,
        is_open=False,
        placement="end",
        children=[
            html.Div(
                id=GraphStatistics.PANEL_CONTENT,
                children=[
                    html.P("No statistics calculated yet.")
                ]
            )
        ],
    )
