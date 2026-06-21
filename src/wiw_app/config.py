class EdgeConfig:
    DEFAULT_EDGE_CURVE_STYLE = "bezier"

    SCALE_DEFAULT = 10
    SCALE_MIN = 1
    SCALE_MAX = 100
    SCALE_STEP = 1
    NO_SCALE_DEFAULT = 2

    THRESHOLD_DEFAULT = 0.1
    THRESHOLD_MIN = 0.0
    THRESHOLD_MAX = 0.99
    THRESHOLD_STEP = 0.01

    # this is frail and needs improvements if we increase the max value...
    THRESHOLD_MARKS = {
        i / 10: str(i / 10)
        for i in range(11)
    }

    LABEL_FONT_DEFAULT = 8
    LABEL_FONT_MIN = 1
    LABEL_FONT_MAX = 50
    LABEL_FONT_STEP = 1
    LABEL_FONT_MARK_INTERVAL = 10
    LABEL_FONT_MARKS = {
        i: str(i)
        for i in range(
            0,
            LABEL_FONT_MAX + 1,
            LABEL_FONT_MARK_INTERVAL,
        )
    }

    class LightMode:
        LABEL_COLOR = "#000"
        LABEL_OUTLINE_COLOR = "#000"

    class DarkMode:
        LABEL_COLOR = "#fff"
        LABEL_OUTLINE_COLOR = "#ccc"

class NodeConfig:
    SIZE_DEFAULT = 50
    SIZE_MIN = 5
    SIZE_MAX = 200
    SIZE_STEP = 1
    SIZE_MARK_INTERVAL = 25
    SIZE_MARKS = {
        i: str(i)
        for i in range(SIZE_MIN, SIZE_MAX + 1, SIZE_MARK_INTERVAL)
    }

    LABEL_FONT_DEFAULT = 15
    LABEL_FONT_MIN = 1
    LABEL_FONT_MAX = 50
    LABEL_FONT_STEP = 1
    LABEL_FONT_MARK_INTERVAL = 10
    LABEL_FONT_MARKS = {
        i: str(i)
        for i in range(
            0,
            LABEL_FONT_MAX + 1,
            LABEL_FONT_MARK_INTERVAL,
        )
    }

    LABEL_OUTLINE_WIDTH = 0.2
    class LightMode:
        LABEL_COLOR = "#000"
        LABEL_OUTLINE_COLOR = "#888"
        DEFAULT_NODE_COLOR = "#FFFACD"

    class DarkMode:
        LABEL_COLOR = "#fff"
        LABEL_OUTLINE_COLOR = "#888"
        DEFAULT_NODE_COLOR = "#BDB76B"

    DEFAULT_SHAPE_SELECTION = 'adaptive'
