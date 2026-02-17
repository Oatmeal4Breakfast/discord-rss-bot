import logging 
import os 

from src.config import config, Config

def get_logger(name: str, config: Config) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.hasHandlers():
        return logger
    
    log_level = config.log_level
    log_file = config.log_file

    file_handler = logging.RotatingFileHandler(log_file, maxBytes=5*1024*1024, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.formatter('[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    logger.addHandler(file_handler)

    return logger
