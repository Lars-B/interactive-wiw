import logging
import os
import tempfile
import uuid
from logging.handlers import RotatingFileHandler

# Where logs will be stored for browser display
log_buffer = []


class DashLogHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        log_buffer.append(msg)
        if len(log_buffer) > 100:
            log_buffer.pop(0)  # keep last 100 lines


# Create and configure the logger
logger = logging.getLogger("dash_app")

# Formatter for all handlers
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s"
)

# File log path in /tmp
session_id = uuid.uuid4().hex[:8]

log_file_path = os.path.join(
    tempfile.gettempdir(),
    f"wiw_visualization_app_{session_id}.log"
)

file_handler = RotatingFileHandler(
    log_file_path,
    maxBytes=2_000_000,
    backupCount=5,
    encoding="utf-8"
)

file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# Console output handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Buffer handler for Dash UI
buffer_handler = DashLogHandler()
buffer_handler.setFormatter(formatter)
logger.addHandler(buffer_handler)

# Avoid duplicate logs on reload
logger.propagate = False

logger.info(f"Session started: {session_id}")
logger.info(f"Log file location: {log_file_path}")
