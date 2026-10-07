import dash_bootstrap_components as dbc

upload_mode_selector = dbc.Select(
    id="upload-mode-selector",
    options=[
        {"label": "Metadata", "value": "metadata"},
        {"label": "BREATH", "value": "breath"},
        {"label": "SCOTTI", "value": "scotti"},
        {"label": "TransPhylo", "value": "transphylo"},
        {"label": "Outbreaker2", "value": "outbreaker2"},
        {"label": "DOT file", "value": "dot-file"},
        {"label": "Custom .csv graph", "value": "custom-csv"},
    ],
    value="breath",
)
