from python4cpm.crypto import Crypto


class Secret:
    def __init__(self, secret: str) -> None:
        self._secret = secret

    def __bool__(self) -> bool:
        return bool(self._secret)

    def get(self) -> str:
        if Crypto.ENABLED and self._secret:
            return Crypto.decrypt(self._secret)
        else:
            return self._secret
