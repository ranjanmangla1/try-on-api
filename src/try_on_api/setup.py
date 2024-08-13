import inspect
import logging
import re
import sys
from typing import TYPE_CHECKING

from loguru import logger
from try_on_api.config import Config


if TYPE_CHECKING:
    from loguru import Record

_RE_LOG_NAME = re.compile(r"^(src\.)?try_on_api")


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def filter_third_party(record: "Record"):
    if record["level"].no >= 40:
        return True

    return _RE_LOG_NAME.match(record["name"]) or (
        record["module"] == "worker" and record["level"].no >= 20
    )


def setup_logger(source: str):
    # Remove the original logger configuration
    logger.remove()

    def custom_format(record: "Record") -> str:
        extra = record.get("extra", None) or {}
        exception = record.get("exception", None)
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )
        if extra:
            log_format += " | {extra_formatted}"

        if exception:
            log_format += "\n<red>{exception}</red>"

        log_format += "\n"

        record["extra_formatted"] = " ".join(
            f"{key}={value}" for key, value in extra.items()
        )
        return log_format

    logger.add(
        sys.stdout,
        colorize=True,
        level=Config.LOG_LEVEL.upper(),
        format=custom_format,
        filter=filter_third_party,
    )
    if Config.ENABLE_LOG_FILE:
        logger.add(
            f"{Config.LOG_DIR}/{source}.log",
            level=Config.LOG_LEVEL.upper(),
            rotation=f"{Config.LOG_FILE_SIZE_IN_MB}mb",
            format=custom_format,
            filter=filter_third_party,
        )

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
