from .ui_state_callbacks import *
from .clientside_callbacks import *
from .graph_callbacks import *
from .export_callbacks import *
from .upload_mode_rendering import *
from .upload import *
from .filename_display_upload import register_filename_display_callback
from ..ids import UploadIDs


def register_callbacks(app):
    register_filename_display_callback(app, UploadIDs.outbreaker_rds)
    register_filename_display_callback(app, UploadIDs.transphylo_rds)
    register_filename_display_callback(app, UploadIDs.custom_csv)
    register_filename_display_callback(app, UploadIDs.breath_trees)
