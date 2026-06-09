class EdgeConfig:
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

    LABEL_FONT_DEFAULT = 5
    LABEL_FONT_MIN = 1
    LABEL_FONT_MAX = 30
    LABEL_FONT_STEP = 1
    LABEL_FONT_MARK_INTERVAL = 5

    LABEL_FONT_MARKS = {
        i: str(i)
        for i in range(
            0,
            LABEL_FONT_MAX + 1,
            LABEL_FONT_MARK_INTERVAL,
        )
    }


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
