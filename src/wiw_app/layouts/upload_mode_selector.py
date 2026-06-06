import dash_bootstrap_components as dbc

upload_mode_selector = dbc.Select(
    id="upload-mode-selector",
    options=[
        {"label": "BREATH", "value": "breath"},
        {"label": "Transphylo", "value": "transphylo"},
        {"label": "Outbreaker2", "value": "outbreaker"},
        {"label": "Metadata", "value": "metadata"},
        {"label": "Custom .csv graph", "value": "custom-csv"},
    ],
    value="breath",
)
