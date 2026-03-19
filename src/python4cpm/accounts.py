from python4cpm.envhandler import EnvHandler, Props
from python4cpm.secrets import Password, NewPassword


class BaseAccount(EnvHandler):
    PROPS = Props("username", "password")

    def __init__(
        self,
        username: str | None,
        password: str | None
    ) -> None:
        self._username = username
        self._password = Password.from_env_var(password)

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
    def password(self) -> Password:
        return self._password


class TargetAccount(BaseAccount):
    OBJ_PREFIX = "target_"
    PROPS = Props(
        "policy_id",
        "safe_name",
        "object_name",
        "username",
        "password",
        "address",
        "port",
        "new_password"
    )

    def __init__(
        self,
        policy_id: str | None,
        safe_name: str | None,
        object_name: str | None,
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
        self._policy_id = policy_id
        self._safe_name = safe_name
        self._object_name = object_name
        self._address = address
        self._port = port
        self._new_password = NewPassword.from_env_var(new_password)

    @property
    def policy_id(self) -> str | None:
        return self._policy_id

    @property
    def safe_name(self) -> str | None:
        return self._safe_name

    @property
    def object_name(self) -> str | None:
        return self._object_name

    @property
    def address(self) -> str | None:
        return self._address

    @property
    def port(self) -> str | None:
        return self._port

    @property
    def new_password(self) -> NewPassword:
        return self._new_password


class LogonAccount(BaseAccount):
    OBJ_PREFIX = "logon_"


class ReconcileAccount(BaseAccount):
    OBJ_PREFIX = "reconcile_"
