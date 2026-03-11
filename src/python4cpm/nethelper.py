from python4cpm.python4cpm import Python4CPM
from python4cpm.args import Args
from python4cpm.accounts import TargetAccount, LogonAccount, ReconcileAccount
from python4cpm.crypto import Crypto
import os


class NETHelper:
    @classmethod
    def set(
        cls,
        action: str | None = None,
        logging_level: str | None = None,
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
        if Crypto.ENABLED:
            target_password = Crypto.encrypt(target_password)
            logon_password = Crypto.encrypt(logon_password)
            reconcile_password = Crypto.encrypt(reconcile_password)
            target_new_password = Crypto.encrypt(target_new_password)
        keys = (
            Args.get_key(Args.PROPS.action),
            Args.get_key(Args.PROPS.logging_level),
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
                os.environ.update({key: values[i]})

    @classmethod
    def get(cls) -> Python4CPM:
        return Python4CPM(cls.__name__)
