import os
import logging
from logging.handlers import RotatingFileHandler


_LOGS_DIR = os.path.join("Logs", "ThirdParty", "Python4CPM")
_CPM_ROOT_DIR = "C:\\Program Files (x86)\\CyberArk\\Password Manager"
if os.path.exists(_CPM_ROOT_DIR):
    _LOGS_DIR = os.path.join(_CPM_ROOT_DIR, _LOGS_DIR)
_LOGGING_ENABLED_VALUE = "yes"
_LOGGING_LEVELS = {
    "info": logging.INFO,
    "debug": logging.DEBUG
    }


def get_logger(
    name: str,
    args_logging: str,
    args_logging_level: str
) -> logging.Logger:
    if args_logging is None:
        return None
    if args_logging.lower() != _LOGGING_ENABLED_VALUE:
        return None
    os.makedirs(_LOGS_DIR, exist_ok=True)
    logs_file = os.path.join(_LOGS_DIR, f"{name}.log")
    _id = os.urandom(4).hex()
    logger = logging.getLogger(_id)
    logging_level = args_logging_level.lower()
    if logging_level in _LOGGING_LEVELS:
        logger.setLevel(_LOGGING_LEVELS[logging_level])
    else:
        logger.setLevel(_LOGGING_LEVELS["info"])
    handler = RotatingFileHandler(
        filename=logs_file,
        maxBytes=1 * 1024 * 1024,
        backupCount=1
    )
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
