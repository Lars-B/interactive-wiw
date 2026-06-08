from wiw_app.dash_logger import logger


def validate_int(input_value, *, default_value, maximum=None, minimum=None):
    if input_value is None:
        logger.debug(
            f"validate_int: received None, using default value {default_value}."
        )
        return default_value

    try:
        value = int(input_value)
    except (TypeError, ValueError):
        logger.debug(
            f"validate_int: could not convert {input_value!r} to int, "
            f"using default value {default_value}."
        )
        return default_value

    if minimum is not None and value < minimum:
        logger.debug(
            f"validate_int: value {value} below minimum {minimum}, "
            f"clamping to {minimum}."
        )
        value = minimum

    if maximum is not None and value > maximum:
        logger.debug(
            f"validate_int: value {value} above maximum {maximum}, "
            f"clamping to {maximum}."
        )
        value = maximum

    return value
