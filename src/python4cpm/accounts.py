from python4cpm.envhandler import EnvHandler, Props
from python4cpm.secret import Secret


class BaseAccount(EnvHandler):
    PROPS = Props("username", "password")

    def __init__(
        self,
        username: str | None,
        password: str | None
    ) -> None:
        self._username = username
        self._password = Secret.from_env_var(password)

    @classmethod
    def get(cls) -> object | None:
        kwargs = cls.get_kwargs()
        if all(value is None for value in kwargs.values()):
            return None
        return cls(**kwargs)

    @property
    def username(self) -> str:
        return self._username

    @property
    def password(self) -> Secret:
        return self._password


class TargetAccount(BaseAccount):
    OBJ_PREFIX = "target_"
    PROPS = Props("username", "password", "address", "port", "new_password")

    def __init__(
        self,
        username: str | None,
        password: str | None,
        address: str | None,
        port: str | None,
        new_password: str | None
    ) -> None:
        super().__init__(
            username,
            password
        )
        self._address = address
        self._port = port
        self._new_password = Secret.from_env_var(new_password)

    @property
    def address(self) -> str | None:
        return self._address

    @property
    def port(self) -> str | None:
        return self._port

    @property
    def new_password(self) -> Secret:
        return self._new_password


class LogonAccount(BaseAccount):
    OBJ_PREFIX = "logon_"


class ReconcileAccount(BaseAccount):
    OBJ_PREFIX = "reconcile_"
