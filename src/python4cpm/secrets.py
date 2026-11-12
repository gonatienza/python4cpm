from python4cpm.crypto import Crypto


class Secret:
    def __init__(self, secret: str) -> None:
        self._value = secret

    @classmethod
    def from_env_var(cls, secret: str | None) -> object | None:
        if secret is not None:
            return cls(secret)
        return None

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        if Crypto.ENABLED:
            return "[ENCRYPTED]"
        return "[SET]"

    def get(self) -> str:
        if Crypto.ENABLED:
            return Crypto.decrypt(self._value)
        return self._value


class Password(Secret):
    pass


class NewPassword(Secret):
    pass


class ReturnedPassword(Secret):
    @classmethod
    def from_string(cls, value: str) -> object:
        if not isinstance(value, str):
            raise TypeError("value must be a str")
        if Crypto.ENABLED:
            return cls(Crypto.encrypt(value))
        return cls(value)
