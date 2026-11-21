import logging
import os
from datetime import datetime


class SystemLogger:
    def __init__(self, log_path: str = "logs/system.log"):
        self.log_path = log_path
        self._ensure_directory()
        self.logger = logging.getLogger("SoftwareFJ")
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            file_handler = logging.FileHandler(self.log_path, encoding="utf-8")
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def _ensure_directory(self):
        directory = os.path.dirname(self.log_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str, exception: Exception = None):
        if exception is not None:
            self.logger.error("%s | Exception: %s", message, repr(exception))
        else:
            self.logger.error(message)

    def debug(self, message: str):
        self.logger.debug(message)

    def log_event(self, event: str, detail: str = ""):
        self.logger.info("EVENT | %s | %s", event, detail)

    def path(self) -> str:
        return os.path.abspath(self.log_path)
