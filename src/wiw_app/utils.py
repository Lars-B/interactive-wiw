import time
from contextlib import contextmanager

from wiw_app.dash_logger import logger


@contextmanager
def log_time(label="Operation"):
    start = time.time()
    yield
    duration = time.time() - start
    logger.info(f"{label} took {duration:.2f} seconds")


def humanize_label(key):
    """
    Function to make labels/ids for dropdowns nice
    """
    return key.replace("_", " ").replace("-", " ").capitalize()
