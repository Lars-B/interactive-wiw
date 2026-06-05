import logging
from datetime import datetime, timedelta
import uuid
from logging.handlers import RotatingFileHandler
from pathlib import Path

from platformdirs import user_log_dir

# Where logs will be stored for browser display
log_buffer = []


class DashLogHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        log_buffer.append(msg)
        if len(log_buffer) > 100:
            log_buffer.pop(0)  # keep last 100 lines


def cleanup_old_logs(log_dir: Path, days: int = 10):
    cutoff = datetime.now() - timedelta(days=days)
    deleted = []
    found = []

    for log_file in log_dir.glob("*.log"):
        try:
            if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff:
                log_file.unlink()
                deleted.append(log_file.name)
            else:
                found.append(log_file.name)
        except Exception:
            pass

    return deleted, found


# Create and configure the logger
logger = logging.getLogger("dash_app")

# Formatter for all handlers
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s"
)

# File log path in /tmp
session_id = uuid.uuid4().hex[:8]

log_dir = Path(user_log_dir("wiw_visualization_app"))
log_dir.mkdir(parents=True, exist_ok=True)

# removing logs older than 10 days...
deleted_logs, found = cleanup_old_logs(log_dir, days=10)
print(f"Found and removed {len(deleted_logs)} log files...")
print(f"There are {len(found)} log files remaining...")

log_file_path = log_dir / f"{session_id}.log"

file_handler = RotatingFileHandler(
    log_file_path,
    maxBytes=2_000_000,
    backupCount=3,
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
