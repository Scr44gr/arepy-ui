import logging
import sys
from typing import Optional

_logger: Optional[logging.Logger] = None


def get_logger() -> logging.Logger:
    global _logger
    if _logger is None:
        _logger = logging.getLogger("arepy_ui")
        _logger.setLevel(logging.WARNING)

        if not _logger.handlers:
            handler = logging.StreamHandler(sys.stderr)
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter("[%(name)s] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            _logger.addHandler(handler)

    return _logger


def set_level(level: int) -> None:
    get_logger().setLevel(level)


def enable_debug() -> None:
    set_level(logging.DEBUG)


def enable_verbose() -> None:
    set_level(logging.INFO)


def silence() -> None:
    set_level(logging.CRITICAL + 1)


class Logger:
    __slots__ = ("_logger",)

    def __init__(self):
        self._logger = get_logger()

    def debug(self, msg: str, *args, **kwargs) -> None:
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        self._logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs) -> None:
        self._logger.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs) -> None:
        self._logger.exception(msg, *args, **kwargs)


logger = Logger()
