import os
import sys
import atexit
import logging
from python4cpm.secret import Secret
from python4cpm.args import Args
from python4cpm.crypto import Crypto
from python4cpm.logger import Logger
from python4cpm.accounts import (
    BaseAccount,
    TargetAccount,
    LogonAccount,
    ReconcileAccount
)

class Python4CPM:
    ACTION_VERIFY = "verifypass"
    ACTION_LOGON = "logon"
    ACTION_CHANGE = "changepass"
    ACTION_PRERECONCILE = "prereconcilepass"
    ACTION_RECONCILE = "reconcilepass"
    _VALID_ACTIONS = (
        ACTION_VERIFY,
        ACTION_LOGON,
        ACTION_CHANGE,
        ACTION_PRERECONCILE,
        ACTION_RECONCILE,
    )
    _SUCCESS_CODE = 10
    _FAILED_RECOVERABLE_CODE = 81
    _FAILED_UNRECOVERABLE_CODE = 89
    _ENV_PREFIX = "PYTHON4CPM_"

    def __init__(self, name: str) -> None:
        self._name = name
        self._args = self._get_args()
        self._logger = Logger.get_logger(self._name, self._args.logging_level)
        self._logger.debug("Initiating...")
        self._log_obj(self._args)
        self._verify_action()
        self._target_account = self._get_account(TargetAccount)
        self._logon_account = self._get_account(LogonAccount)
        self._reconcile_account = self._get_account(ReconcileAccount)
        self._log_obj(self._target_account)
        self._log_obj(self._logon_account)
        self._log_obj(self._reconcile_account)
        self._closed = False
        atexit.register(self._on_exit)

    @property
    def args(self) -> Args:
        return self._args

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @property
    def target_account(self) -> TargetAccount:
        return self._target_account

    @property
    def logon_account(self) -> LogonAccount:
        return self._logon_account

    @property
    def reconcile_account(self) -> ReconcileAccount:
        return self._reconcile_account

    @classmethod
    def _get_env_key(cls, key: str) -> str:
        return f"{cls._ENV_PREFIX}{key.upper()}"

    @classmethod
    def _get_args(cls) -> Args:
        kwargs = {}
        for kwarg in Args.ARGS:
            _kwarg = os.environ.get(cls._get_env_key(kwarg))
            kwargs[kwarg] = _kwarg if _kwarg is not None else ""
        return Args(**kwargs)

    def _get_account(self, account_class: BaseAccount) -> BaseAccount:
        args = []
        for arg in account_class.ENV_VARS:
            _arg = os.environ.get(self._get_env_key(arg))
            args.append(_arg if _arg is not None else "")
        return account_class(*args)

    def _verify_action(self) -> None:
        if self._args.action not in self._VALID_ACTIONS:
            self._logger.warning(f"Unkonwn action -> '{self._args.action}'")

    def _log_obj(self, obj: object) -> None:
        for key, value in vars(obj).items():
            _key = f"{obj.__class__.__name__}.{key.strip('_')}"
            if value:
                if not isinstance(value, Secret):
                    logging_value = f"'{value}'"
                else:
                    if Crypto.ENABLED is True:
                        logging_value = "[ENCRYPTED]"
                    else:
                        logging_value = "[SET]"
            else:
                logging_value = "[NOT SET]"
            self._logger.debug(f"{_key} -> {logging_value}")

    def close_fail(self, unrecoverable: bool = False) -> None:
        if unrecoverable is False:
            code = self._FAILED_RECOVERABLE_CODE
        else:
            code = self._FAILED_UNRECOVERABLE_CODE
        self._logger.error(f"Closing with code {code}")
        self._closed = True
        sys.exit(code)

    def close_success(self) -> None:
        self._logger.debug(f"Closing with code {self._SUCCESS_CODE}")
        self._closed = True
        sys.exit(self._SUCCESS_CODE)

    def _on_exit(self):
        if self._closed is False:
            message = "No close signal called"
            self._logger.error(message)
            sys.stderr.write(message)
            sys.stderr.flush()
