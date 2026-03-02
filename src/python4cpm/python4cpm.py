import os
import sys
import atexit
from python4cpm.secrets import Secret, Secrets
from python4cpm.args import Args
from python4cpm.crypto import Crypto
from python4cpm.logger import Logger


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
        self._logger = Logger.get_logger(
            self._name,
            self._args.logging,
            self._args.logging_level
        )
        self.log_debug("Initiating...")
        self._log_env(self._args)
        self._verify_action()
        self._secrets = self._get_secrets()
        self._log_env(self._secrets)
        self._closed = False
        atexit.register(self._on_exit)

    @property
    def args(self) -> Args:
        return self._args

    @property
    def secrets(self) -> Secrets:
        return self._secrets

    def log_debug(self, message: str) -> None:
        if self._logger is not None:
            self._logger.debug(message, stacklevel=2)

    def log_info(self, message: str) -> None:
        if self._logger is not None:
            self._logger.info(message, stacklevel=2)

    def log_warning(self, message: str) -> None:
        if self._logger is not None:
            self._logger.warning(message, stacklevel=2)

    def log_error(self, message: str) -> None:
        if self._logger is not None:
            self._logger.error(message, stacklevel=2)

    @classmethod
    def _get_env_key(cls, key: str) -> str:
        return f"{cls._ENV_PREFIX}{key.upper()}"

    @classmethod
    def _get_args(cls) -> dict:
        args = {}
        for arg in Args.ARGS:
            _arg = os.environ.get(cls._get_env_key(arg))
            args[arg] = _arg if _arg is not None else ""
        return Args(**args)

    def _get_secrets(self) -> dict:
        secrets = {}
        for secret in Secrets.SECRETS:
            _secret = os.environ.get(self._get_env_key(secret))
            secrets[secret] = _secret if _secret is not None else ""
        return Secrets(**secrets)

    def _verify_action(self) -> None:
        if self._args.action not in self._VALID_ACTIONS:
            self.log_warning(f"Unkonwn action -> '{self._args.action}'")

    def _log_env(self, obj: object) -> None:
        for key, value in vars(obj).items():
            _key = key.strip('_')
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
            self.log_debug(f"{_key} -> {logging_value}")

    def close_fail(self, unrecoverable: bool = False) -> None:
        if unrecoverable is False:
            code = self._FAILED_RECOVERABLE_CODE
        else:
            code = self._FAILED_UNRECOVERABLE_CODE
        self.log_error(f"Closing with code {code}")
        self._closed = True
        sys.exit(code)

    def close_success(self) -> None:
        self.log_debug(f"Closing with code {self._SUCCESS_CODE}")
        self._closed = True
        sys.exit(self._SUCCESS_CODE)

    def _on_exit(self):
        if self._closed is False:
            message = "No close signal called"
            self.log_error(message)
            sys.stderr.write(message)
            sys.stderr.flush()
