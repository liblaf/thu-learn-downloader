import logging
from enum import StrEnum

from rich.logging import RichHandler

logging.basicConfig(
    format="%(message)s", datefmt="[%X]", level=logging.NOTSET, handlers=[RichHandler()]
)


class LogLevel(StrEnum):
    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
