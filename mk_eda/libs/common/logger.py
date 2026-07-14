import logging
import os
from logging import Logger
from logging.handlers import RotatingFileHandler

from mk_eda.libs.common.constants import MB


def get_logger(name: str) -> Logger:
    MAX_BYTES = 16 * MB
    BACKUP_COUNT = 5

    os.makedirs("logs", exist_ok=True)
    strfmt = "[%(asctime)s] [%(name)s] [%(levelname)s] > %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt=strfmt, datefmt=datefmt)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)

    debug_handler = RotatingFileHandler("logs/debug.log", maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT)
    debug_handler.setFormatter(formatter)
    debug_handler.setLevel(logging.DEBUG)
    logger.addHandler(debug_handler)

    error_handler = RotatingFileHandler("logs/error.log", maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT)
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    logger.addHandler(error_handler)

    return logger
