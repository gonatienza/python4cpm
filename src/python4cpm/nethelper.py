from python4cpm.python4cpm import Python4CPM
from python4cpm.crypto import Crypto
import os


class NETHelper:
    @classmethod
    def set(
        cls,
        action: str = "",
        target_username: str = "",
        target_address: str = "",
        target_port: str = "",
        logon_username: str = "",
        reconcile_username: str = "",
        logging: str = "",
        logging_level: str = "",
        target_password: str = "",
        logon_password: str = "",
        reconcile_password: str = "",
        target_new_password: str = ""
    ) -> None:
        if Crypto.ENABLED:
            target_password = Crypto.encrypt(target_password)
            logon_password = Crypto.encrypt(logon_password)
            reconcile_password = Crypto.encrypt(reconcile_password)
            target_new_password = Crypto.encrypt(target_new_password)
        env = {
            "ACTION": action,
            "TARGET_USERNAME": target_username,
            "TARGET_ADDRESS": target_address,
            "TARGET_PORT": target_port,
            "LOGON_USERNAME": logon_username,
            "RECONCILE_USERNAME": reconcile_username,
            "LOGGING": logging,
            "LOGGING_LEVEL": logging_level,
            "TARGET_PASSWORD": target_password,
            "LOGON_PASSWORD": logon_password,
            "RECONCILE_PASSWORD": reconcile_password,
            "TARGET_NEW_PASSWORD": target_new_password
        }
        for key, value in env.items():
            env_var = Python4CPM._ENV_PREFIX + key
            os.environ[env_var] = value

    @classmethod
    def get(cls) -> Python4CPM:
        return Python4CPM(cls.__name__)
