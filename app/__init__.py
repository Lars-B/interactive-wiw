import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import Dash

cyto.load_extra_layouts()

template_theme1 = "morph"
template_theme2 = "slate"
url_theme1 = dbc.themes.MORPH
url_theme2 = dbc.themes.SLATE

dbc_css = (
    "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.1/dbc.min.css"
)

app = Dash(
    __name__,
    external_stylesheets=[url_theme1, dbc_css],
    assets_folder="../assets",
)
