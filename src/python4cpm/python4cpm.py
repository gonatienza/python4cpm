import sys
import atexit
import logging
from python4cpm.secret import Secret
from python4cpm.args import Args
from python4cpm.logger import Logger
from python4cpm.accounts import TargetAccount, LogonAccount, ReconcileAccount


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

    def __init__(self) -> None:
        self._args = Args.get()
        self._target_account = TargetAccount.get()
        self._logon_account = LogonAccount.get()
        self._reconcile_account = ReconcileAccount.get()
        self._logger = Logger.get_logger(
            f"{self._target_account.policy_id}-{self._target_account.object_name}",
            self._args.logging_level
        )
        self._logger.debug("Initiating...")
        self._log_obj(self._args)
        self._verify_action()
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

    def _verify_action(self) -> None:
        if self._args.action not in self._VALID_ACTIONS:
            self._logger.warning(f"Unkonwn action -> '{self._args.action}'")

    def _log_obj(self, obj: object | None) -> None:
        if obj is not None:
            for key, value in vars(obj).items():
                _key = f"{obj.__class__.__name__}.{key.removeprefix('_')}"
                if value is not None:
                    if not isinstance(value, Secret):
                        logging_value = f"'{value}'"
                    else:
                        logging_value = str(value)
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
