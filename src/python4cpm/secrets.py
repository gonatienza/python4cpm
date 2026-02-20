from python4cpm.crypto import Crypto


class SecureString:
    def __init__(self, secret: str) -> None:
        self._secret = secret
        self._is_encrypted = Crypto.ENABLED

    @property
    def is_encrypted(self):
        return self._is_encrypted

    def get(self) -> str:
        if self._is_encrypted:
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
        self._password = SecureString(password)
        self._logon_password = SecureString(logon_password)
        self._reconcile_password = SecureString(reconcile_password)
        self._new_password = SecureString(new_password)

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
