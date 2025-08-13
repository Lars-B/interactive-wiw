import logging
from wiw_app import app as my_app
import wiw_app.callbacks

from wiw_app.dash_logger import logger


if __name__ == "__main__":
    logger.info("Starting wiw_app")
    logger.setLevel(logging.DEBUG)
    my_app.run(debug=True)
