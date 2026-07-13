class UploadIDs:
    INFO_TOAST = "info-toast"

    class breath_trees:
        UPLOAD_DATA = "upload-trees-data"
        SELECTED_FILENAME = "selected-trees-filename"
        BURN_IN_SELECTION = "BREATH-burn-in-selection"
        DATASET_LABEL = "trees-dataset-label"
        CONFIRM_BUTTON = "confirm-dataset-btn"
        BURN_IN_CONTAINER = "BREATH-burn-in-container"
        LOADING_MODAL = "loading-modal-breath"

    class metadata:
        UPLOAD_DATA = "upload-node-annotations"
        SELECTED_FILENAME = "selected-node-annotations-file"
        CONFIRM_NODE_ANNOTATIONS_BTN = "confirm-node-annotation-btn"
        UPLOAD_COLUMN_NAME = "upload-column-name-association"
        GRAPH_NODE_INFO_NAME = "graph-node-info-name-association"
        NODE_ANNOTATIONS_LABEL_WARNING = "node-annotations-label-warning"

    class custom_csv:
        UPLOAD_DATA = "outbreaker2-graph-data"
        SELECTED_FILENAME = "outbreaker2-graph-filename"
        DATASET_LABEL = "outbreaker2-dataset-label"
        CONFIRM_BUTTON = "outbreaker2-dataset-button"

    class outbreaker_rds:
        UPLOAD_DATA = "outbreaker_rds-graph-data"
        SELECTED_FILENAME = "outbreaker_rds-graph-filename"
        DATASET_LABEL = "outbreaker_rds-dataset-label"
        CONFIRM_BUTTON = "outbreaker_rds-dataset-button"
        LOADING_MODAL = "loading-modal-outbreaker2"

    class transphylo_rds:
        UPLOAD_DATA = "transphylo-rds-graph-data"
        SELECTED_FILENAME = "transphylo-rds-graph-filename"
        DATASET_LABEL = "transphylo-rds-dataset-label"
        CONFIRM_BUTTON = "transphylo-rds-dataset-button"
        BURN_IN_SELECTION = "TP-burn-in-selection"
        INPUT_TYPE = "TP-input-type"
        BURN_IN_CONTAINER = "TP-burnin-container"
        LOADING_MODAL = "loading-modal-tp"


class GraphOptions:
    TABS = "graph-option-tabs"

    class Legend:
        DOWNLOAD = "download-legend"
        ADD_LEG_NODE = "btn-add-legend-node"
        REMOVE_LEG_NODE = "btn-remove-legend-node"

    class Graph:
        TAB = "tab-graph-options"
        LAYOUT_SELECTOR = "layout-selector"
        RENCENTER_BTN = "recenter-btn"

    class Nodes:
        TAB = "tab-node-options"

        ADVANCED_OPTIONS_ICON = "advanced-node-options-button-icon"
        ADVANCED_OPTIONS_COLLAPSE = "advanced-node-options-collapse"
        ADVANCED_OPTION_TOGGLE_BTN = "advanced-node-option-toggle-btn"

        LABEL_ANNOTATION_SELECTOR = "node-annotation-selector"
        LABEL_FONT_SIZE = "node-label-font-size"

        COLOR_BY_LABEL = "node-color-by-label"
        COLOR_MODE = "node-color-mode"

        COLOR_LABEL_SELECTOR = "node-color-label-selector"
        COLOR_PICKER_CONTAINERS = "node-color-pickers-container"
        COLOR_PICKERS_COLLAPSE = "node-color-pickers-collapse"
        HEATMAP_OPTIONS_COLLAPSE = "node-heatmap-options-collapse"
        CATEGORICAL_COLOR_OPTIONS = "nodes-categorical-color-options-collapse"
        COLORMAP_SELECTOR = "nodes-heatmap-colormap-selector"

        COLOR_STORE = "node-label-color-store"

        SUPPRESS_SINGLETONS = "suppress-singletons"
        SIZE_SELECTOR = "node-label-size-selector"
        SHAPE_SELECTOR = "node-shape-selector"

    class Edges:
        TAB = "tab-edge-options"
        DISPLAY_FILTER = "edge-label-filter"
        ANNOTATION_SELECTOR = "edge-annotation-selector"
        LABEL_POSITION = "edge-label-position"
        SCALE_WIDTH_BY_WEIGHT = "scale-width-toggle"
        ADVANCED_OPTIONS_ICON = "advanced-edge-options-button-icon"
        ADVANCED_OPTIONS_COLLAPSE = "advanced-edge-options-collapse"
        ADVANCED_OPTION_TOGGLE_BTN = "advanced-edge-option-toggle-btn"
        COLOR_BY_LABEL = "color-by-label-toggle"
        COLOR_STORE = "edge-label-color-store"
        LABEL_RENAME_ERROR = "rename-error"
        LABEL_FONT_SIZE = 'edge-label-font-size'
        COLOR_PICKER_CONTAINERS = "color-pickers-container"
        COLOR_PICKERS_COLLAPSE = "color-pickers-collapse"
        DISPLAY_EDGE_THRESHOLD = 'weight-threshold'
        TOGGLE_ARROWS = "edge-arrows"
        SCALE_VALUE_INPUT = "edge-scale-input"
        CURVE_STYLE_SELECTOR = "edge-curve-style-selector"


class DOWNLOAD:
    GET_DOT_BUTTON = "btn-get-dot"
    GET_SVG_BUTTON = "btn-get-svg"
    GET_PNG_BUTTON = "btn-get-png"
    GET_JPG_BUTTON = "btn-get-jpg"
    GET_LEGEND_SVG_BUTTON = "btn-get-legend-svg"
    GET_PNG_WITH_LEGEND = "btn-get-pngplus"
    FILENAME_INPUT = "filename-input"
