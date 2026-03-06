from python4cpm.secret import Secret


class BaseAccount:
    def __init__(
        self: str,
        username: str,
        password: str
    ) -> None:
        self._username = username
        self._password = Secret(password)

    @property
    def username(self) -> str:
        return self._username

    @property
    def password(self) -> Secret:
        return self._password


class TargetAccount(BaseAccount):
    ENV_VARS = (
        "target_username",
        "target_password",
        "target_address",
        "target_port",
        "target_new_password"
    )
    def __init__(
        self: str,
        username: str,
        password: str,
        address: str,
        port: str,
        new_password: str
    ) -> None:
        super().__init__(
            username,
            password
        )
        self._address = address
        self._port = port
        self._new_password = Secret(new_password)

    @property
    def address(self) -> str:
        return self._address

    @property
    def port(self) -> str:
        return self._port

    @property
    def new_password(self) -> Secret:
        return self._new_password


class LogonAccount(BaseAccount):
    ENV_VARS = (
        "logon_username",
        "logon_password"
    )


class ReconcileAccount(BaseAccount):
    ENV_VARS = (
        "reconcile_username",
        "reconcile_password"
    )
