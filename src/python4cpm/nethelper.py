from python4cpm.python4cpm import Python4CPM
from python4cpm.args import Args
from python4cpm.secrets import Secrets
from python4cpm.crypto import Crypto
import os


class NETHelper:
    @classmethod
    def run(
        cls,
        action: str = "",
        address: str = "",
        username: str = "",
        logon_username: str = "",
        reconcile_username: str = "",
        logging: str = "",
        logging_level: str = "",
        password: str = "",
        logon_password: str = "",
        reconcile_password: str = "",
        new_password: str = ""
    ) -> Python4CPM:
        _args = [
            action,
            address,
            username,
            logon_username,
            reconcile_username,
            logging,
            logging_level
        ]
        for i, arg in enumerate(Args.ARGS):
            os.environ[f"PYTHON4CPM_{arg.upper()}"] = _args[i]
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
            os.environ[f"PYTHON4CPM_{secret.upper()}"] = _secret
        return Python4CPM(cls.__name__)
