import logging
import sys


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("[%(levelname)s] %(asctime)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
