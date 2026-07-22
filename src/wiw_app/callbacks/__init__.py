from .ui_state_callbacks import *
from .clientside_callbacks import *
from .graph_callbacks import *
from .export_callbacks import *
from .upload_mode_rendering import *
from .upload import *
from .filename_display_upload import register_filename_display_callback
from ..ids import UploadIDs
from .modal_callback_factory import make_loading_modal_callback
from .coloring import *


def register_callbacks(app):
    register_filename_display_callback(app, UploadIDs.outbreaker_rds)
    register_filename_display_callback(app, UploadIDs.transphylo_rds)
    register_filename_display_callback(app, UploadIDs.custom_csv)
    register_filename_display_callback(app, UploadIDs.breath_trees)
    register_filename_display_callback(app, UploadIDs.scotti_trees)
    make_loading_modal_callback(UploadIDs.breath_trees)
    make_loading_modal_callback(UploadIDs.transphylo_rds)
    make_loading_modal_callback(UploadIDs.outbreaker_rds)
    make_loading_modal_callback(UploadIDs.scotti_trees)
