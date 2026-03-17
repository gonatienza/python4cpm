from python4cpm.crypto import Crypto


class Secret:
    def __init__(self, secret: str) -> None:
        self._secret = secret

    @classmethod
    def from_env_var(cls, secret: str | None) -> object | None:
        if secret is not None:
            return cls(secret)
        return None

    def __str__(self) -> str:
        if Crypto.ENABLED:
            return "[ENCRYPTED]"
        return "[SET]"

    def get(self) -> str:
        if Crypto.ENABLED:
            return Crypto.decrypt(self._secret)
        return self._secret
