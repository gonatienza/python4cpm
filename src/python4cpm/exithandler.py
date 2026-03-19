from python4cpm.loggerhandler import LoggerHandler
import atexit
import sys


class ExitHandler:
    _ERROR_MESSAGE = "No close signal called"
    _closed = False

    @classmethod
    def reset(cls) -> None:
        cls._closed = False

    @classmethod
    def set_closed(cls) -> None:
        cls._closed = True

    @classmethod
    def on_exit(cls) -> None:
        if cls._closed is False:
            for logger in LoggerHandler.get_all_loggers():
                logger.error(cls._ERROR_MESSAGE)
            sys.stderr.write(cls._ERROR_MESSAGE)
            sys.stderr.flush()


atexit.register(ExitHandler.on_exit)
