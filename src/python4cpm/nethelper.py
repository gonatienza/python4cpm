from python4cpm.python4cpm import Python4CPM
from python4cpm.args import Args
from python4cpm.secrets import Secrets
from python4cpm.crypto import Crypto
import os


class NETHelper:
    @classmethod
    def set(
        cls,
        action: str = "",
        username: str = "",
        address: str = "",
        port: str = "",
        logon_username: str = "",
        reconcile_username: str = "",
        logging: str = "",
        logging_level: str = "",
        password: str = "",
        logon_password: str = "",
        reconcile_password: str = "",
        new_password: str = ""
    ) -> None:
        _args = [
            action,
            username,
            address,
            port,
            logon_username,
            reconcile_username,
            logging,
            logging_level
        ]
        for i, arg in enumerate(Args.ARGS):
            env_var = Python4CPM._ENV_PREFIX + arg.upper()
            os.environ[env_var] = _args[i]
        _secrets = [
            password,
            logon_password,
            reconcile_password,
            new_password
        ]
        for i, secret in enumerate(Secrets.SECRETS):
            if Crypto.ENABLED:
                _secret = Crypto.encrypt(_secrets[i])
            else:
                _secret = _secrets[i]
            env_var = Python4CPM._ENV_PREFIX + secret.upper()
            os.environ[env_var] = _secret

    @classmethod
    def get(cls) -> Python4CPM:
        return Python4CPM(cls.__name__)
