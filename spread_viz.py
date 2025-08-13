import logging
import threading
import webbrowser
import wiw_app.callbacks
from wiw_app import app
from wiw_app.dash_logger import logger

PORT = 12712

logger.setLevel(logging.INFO)
logger.info("Starting packaged wiw_app")


def open_browser():
    webbrowser.open_new(f"http://127.0.0.1:{PORT}")


if __name__ == "__main__":
    threading.Timer(1.5, open_browser).start()
    app.run(debug=False, port=PORT, host="127.0.0.1", use_reloader=False)
