import os
import logging
from logging.handlers import RotatingFileHandler


class Logger:
    _LOGS_DIR = os.path.join("Logs", "ThirdParty")
    _LOGGING_LEVELS = {
        "critical": logging.CRITICAL,
        "error": logging.ERROR,
        "warning": logging.WARNING,
        "info": logging.INFO,
        "debug": logging.DEBUG
    }
    _DEFAULT_LEVEL = _LOGGING_LEVELS["error"]

    @classmethod
    def get_logger(
        cls,
        policy_id: str | None,
        logging_level: str | None
    ) -> logging.Logger:
        os.makedirs(cls._LOGS_DIR, exist_ok=True)
        uid = os.urandom(4).hex()
        logger = logging.getLogger(uid)
        is_logging_level_str = isinstance(logging_level, str)
        if is_logging_level_str and logging_level.lower() in cls._LOGGING_LEVELS:
            logger.setLevel(cls._LOGGING_LEVELS[logging_level.lower()])
        else:
            logger.setLevel(cls._DEFAULT_LEVEL)
        logs_file = os.path.join(cls._LOGS_DIR, f"{__name__}-{policy_id}.log")
        handler = RotatingFileHandler(
            filename=logs_file,
            maxBytes=1024 ** 2,
            backupCount=1
        )
        fmt = (
            "%(asctime)s.%(msecs)03d | %(levelname)s | %(name)s | "
            "%(module)s | %(funcName)s | %(message)s"
        )
        datefmt = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
