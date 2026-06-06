import logging
import threading
import webbrowser
import sys

from wiw_app.dash_logger import logger
from wiw_app import app as my_app
import wiw_app.callbacks

wiw_app.callbacks.register_callbacks(my_app)


def open_browser(port):
    webbrowser.open_new(f"http://127.0.0.1:{port}")


if __name__ == "__main__":

    PACKAGED = getattr(sys, "frozen", False)

    PORT = 12712 if PACKAGED else 8050

    logger.setLevel(logging.INFO if PACKAGED else logging.DEBUG)

    if PACKAGED:
        for log_name in ["werkzeug", "flask.app", "dash"]:
            cur_logger = logging.getLogger(log_name)
            cur_logger.setLevel(logging.WARNING)
            cur_logger.propagate = False

        threading.Timer(1.5, lambda: open_browser(PORT)).start()

    logger.info("Starting wiw_app (packaged=%s)", PACKAGED)

    my_app.run(
        debug=not PACKAGED,
        host="127.0.0.1",
        port=PORT,
        use_reloader=False if PACKAGED else True
    )
