import logging
from app import app as my_app
import app.callbacks

from app.dash_logger import logger


if __name__ == "__main__":
    logger.info("Starting app")
    logger.setLevel(logging.DEBUG)
    my_app.run(debug=True)
