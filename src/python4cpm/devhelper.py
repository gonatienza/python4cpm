from python4cpm.args import Args
from python4cpm.accounts import TargetAccount, LogonAccount, ReconcileAccount
from python4cpm.crypto import Crypto
import os


class DevHelper:
    @staticmethod
    def _get_secret_value(value: str | None) -> str | None:
        if not value:
            return None
        if Crypto.ENABLED:
            return Crypto.encrypt(value)
        return value

    @classmethod
    def set(
        cls,
        action: str | None = None,
        logging_level: str | None = None,
        target_policy_id: str | None = None,
        target_safe_name: str | None = None,
        target_object_name: str | None = None,
        target_username: str | None = None,
        target_address: str | None = None,
        target_port: str | None = None,
        logon_username: str | None = None,
        reconcile_username: str | None = None,
        target_password: str | None = None,
        logon_password: str | None = None,
        reconcile_password: str | None = None,
        target_new_password: str | None = None
    ) -> None:
        target_password = cls._get_secret_value(target_password)
        logon_password = cls._get_secret_value(logon_password)
        reconcile_password = cls._get_secret_value(reconcile_password)
        target_new_password = cls._get_secret_value(target_new_password)
        keys = (
            Args.get_key(Args.PROPS.action),
            Args.get_key(Args.PROPS.logging_level),
            TargetAccount.get_key(TargetAccount.PROPS.policy_id),
            TargetAccount.get_key(TargetAccount.PROPS.safe_name),
            TargetAccount.get_key(TargetAccount.PROPS.object_name),
            TargetAccount.get_key(TargetAccount.PROPS.username),
            TargetAccount.get_key(TargetAccount.PROPS.address),
            TargetAccount.get_key(TargetAccount.PROPS.port),
            LogonAccount.get_key(LogonAccount.PROPS.username),
            ReconcileAccount.get_key(ReconcileAccount.PROPS.username),
            TargetAccount.get_key(TargetAccount.PROPS.password),
            LogonAccount.get_key(LogonAccount.PROPS.password),
            ReconcileAccount.get_key(ReconcileAccount.PROPS.password),
            TargetAccount.get_key(TargetAccount.PROPS.new_password)
        )
        values = (
            action,
            logging_level,
            target_policy_id,
            target_safe_name,
            target_object_name,
            target_username,
            target_address,
            target_port,
            logon_username,
            reconcile_username,
            target_password,
            logon_password,
            reconcile_password,
            target_new_password
        )
        for i, key in enumerate(keys):
            if values[i] is not None:
                os.environ[key] = values[i]
            else:
                os.environ.pop(key, None)
