from python4cpm.crypto import Crypto


class Secret:
    def __init__(self, secret: str) -> None:
        self._secret = secret

    def get(self) -> str:
        if Crypto.ENABLED and self._secret:
            return Crypto.decrypt(self._secret)
        else:
            return self._secret


class Secrets:
    SECRETS = (
        "password",
        "logon_password",
        "reconcile_password",
        "new_password"
    )

    def __init__(
        self: str,
        password: str,
        logon_password: str,
        reconcile_password: str,
        new_password: str
    ) -> None:
        self._password = Secret(password)
        self._logon_password = Secret(logon_password)
        self._reconcile_password = Secret(reconcile_password)
        self._new_password = Secret(new_password)

    @property
    def password(self) -> str:
        return self._password

    @property
    def new_password(self) -> str:
        return self._new_password

    @property
    def logon_password(self) -> str:
        return self._logon_password

    @property
    def reconcile_password(self) -> str:
        return self._reconcile_password
