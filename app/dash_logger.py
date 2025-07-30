import logging

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
logger.setLevel(logging.INFO)

# Formatter for all handlers
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

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
