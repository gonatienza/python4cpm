from python4cpm.envhandler import EnvHandler, Props
from python4cpm.secrets import ReturnedPassword
import os
import sys


class ReturnHandler(EnvHandler):
    OBJ_PREFIX = "returned_"
    PROPS = Props("password_handle")
    _closed = False

    @classmethod
    def _get_handle(cls) -> int | None:
        key = cls.get_key(cls.PROPS.password_handle)
        value = os.environ.get(key)
        if not value:
            return None
        return int(value)

    @classmethod
    def _is_available(cls) -> bool:
        return (
            sys.platform == "win32"
            and cls._closed is False
            and cls._get_handle() is not None
        )

    @classmethod
    def protect(cls) -> None:
        if cls._is_available():
            os.set_handle_inheritable(cls._get_handle(), False)

    @classmethod
    def return_and_close(cls, secret: ReturnedPassword) -> None:
        if not cls._is_available():
            raise OSError("No return channel from the plugin is available")
        handle = cls._get_handle()
        cls._closed = True
        import msvcrt
        fd = msvcrt.open_osfhandle(handle, os.O_WRONLY)
        with os.fdopen(fd, "w", encoding="ascii") as pipe:
            pipe.write(secret.value)


ReturnHandler.protect()
