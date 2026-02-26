import logging
import os


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logs_dir = os.path.join("Logs", "ThirdParty")
    os.makedirs(logs_dir, exist_ok=True)
    logs_file = os.path.join(logs_dir, f"{name}.log")
    handler = logging.FileHandler(logs_file)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
