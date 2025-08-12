# todo refactor these to be more meaningful with more subclasses and then it can be used like
#  UploadIDs.Trees.Upload etc...
class UploadIDs:
    UPLOAD_TREES_DATA = "upload-trees-data"
    SELECTED_TREES_FILENAME = "selected-trees-filename"
    BURN_IN_SELECTION = "burn-in-selection"
    TREES_DATASET_LABEL = "trees-dataset-label"
    CONFIRM_TREES_DATASET_BTN = "confirm-dataset-btn"
    UPLOADED_TREES_DATA_STORE = "uploaded-datasets-store"

    UPLOAD_NODE_ANNOTATIONS = "upload-node-annotations"
    SELECTED_NODE_ANNOTATIONS_FILENAME = "selected-node-annotations-file"
    CONFIRM_NODE_ANNOTATIONS_BTN = "confirm-node-annotation-btn"
    UPLOADED_NODE_ANNOTATIONS_STORE = "uploaded-node-annotations-store"
    NODE_ANNOTATIONS_LABEL = "node-annotations-label"


class GraphOptions:
    TABS = "graph-option-tabs"

    class Graph:
        TAB = "tab-graph-options"
        LAYOUT_SELECTOR = "layout-selector"  # todo find and replace
        RENCENTER_BTN = "recenter-btn"  # todo rename, find and replace

    class Nodes:
        TAB = "tab-node-options"
        ADVANCED_OPTIONS_ICON = "advanced-node-options-button-icon"  # todo find and replace
        ADVANCED_OPTIONS_COLLAPSE = "advanced-node-options-collapse"  # todo find and replace
        ADVANCED_OPTION_TOGGLE_BTN = "advanced-node-option-toggle-btn"
        LABEL_FONT_SIZE = "node-label-font-size"  # todo find and replace
        COLOR_BY_LABEL = "node-color-by-label"
        LABEL_RENAME_ERROR = "node-label-rename-error"
        COLOR_PICKER_CONTAINERS = "node-color-pickers-container"
        COLOR_PICKERS_COLLAPSE = "node-color-pickers-collapse"
        COLOR_STORE = "node-label-color-store"

    class Edges:
        TAB = "tab-edge-options"
        DISPLAY_FILTER = "label-filter"  # todo find usages and replace this
        ANNOTATION_SELECTOR = "edge-annotation-selector"  # todo find and replace
        LABEL_POSITION = "edge-label-position"  # todo find and replace
        SCALE_WIDTH_BY_WEIGHT = "scale-width-toggle"  # todo find and replace
        ADVANCED_OPTIONS_ICON = "advanced-edge-options-button-icon"  # todo find and replace
        ADVANCED_OPTIONS_COLLAPSE = "advanced-edge-options-collapse"  # todo find and replace
        ADVANCED_OPTION_TOGGLE_BTN = "advanced-edge-option-toggle-btn"
        COLOR_BY_LABEL = "color-by-label-toggle"  # todo find and replace
        COLOR_STORE = "label-color-store"  # todo rename and replace
        LABEL_RENAME_ERROR = "rename-error"
        COLOR_PICKER_CONTAINERS = "color-pickers-container"
        COLOR_PICKERS_COLLAPSE = "color-pickers-collapse"
