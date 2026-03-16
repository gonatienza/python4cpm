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
    _DEFAULT_LEVEL = "error"

    @classmethod
    def get_logger(
        cls,
        name: str,
        logging_level: str | None
    ) -> logging.Logger:
        os.makedirs(cls._LOGS_DIR, exist_ok=True)
        uid = os.urandom(4).hex()
        logger = logging.getLogger(uid)
        _logging_level = (logging_level or cls._DEFAULT_LEVEL).lower()
        if _logging_level not in cls._LOGGING_LEVELS:
            _logging_level = cls._DEFAULT_LEVEL
        logger.setLevel(cls._LOGGING_LEVELS[_logging_level])
        file_name = f"{__name__}_{_logging_level}_{name}.log"
        logs_file = os.path.join(cls._LOGS_DIR, file_name)
        handler = RotatingFileHandler(
            filename=logs_file,
            maxBytes=1024 ** 2,
            backupCount=1
        )
        fmt = (
            "%(asctime)s.%(msecs)03d | %(name)s | %(levelname)s | "
            "%(module)s | %(funcName)s | %(message)s"
        )
        datefmt = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
