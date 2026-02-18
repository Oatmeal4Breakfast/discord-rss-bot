import logging
from logging.handlers import RotatingFileHandler
from src.config import Config


def get_logger(name: str, config: Config) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.hasHandlers():
        return logger

    log_level: str = config.log_level
    log_file: str = config.log_file

    file_handler = RotatingFileHandler(
        filename=log_file, maxBytes=5 * 1024 * 1024, encoding="utf-8"
    )
    file_handler.setLevel(level=log_level)
    file_handler.setFormatter(
        fmt=logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level=log_level)
    stream_handler.setFormatter(
        fmt=logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(stream_handler)

    return logger
