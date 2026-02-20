import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from python4cpm.secrets import Secrets
from python4cpm.args import Args


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
    _LOGS_DIR = os.path.join("Logs", "ThirdParty", "Python4CPM")
    _CPM_ROOT_DIR = "C:\\Program Files (x86)\\CyberArk\\Password Manager"
    if os.path.exists(_CPM_ROOT_DIR):
        _LOGS_DIR = os.path.join(_CPM_ROOT_DIR, _LOGS_DIR)
    _LOGGING_ENABLED_VALUE = "yes"
    _LOGGING_LEVELS = {
        "info": logging.INFO,
        "debug": logging.DEBUG
    }
    _SUCCESS_CODE = 0
    _FAILED_RECOVERABLE_CODE = 81
    _FAILED_UNRECOVERABLE_CODE = 89
    _ENV_PREFIX = "PYTHON4CPM_"

    def __init__(self, name: str) -> None:
        self._name = name
        args = self._get_args()
        self._args = Args(**args)
        self._logger = self._get_logger(self._name)
        self.log_info("Python4CPM.__init__: initiating...")
        self._log_args()
        self._verify_action()
        secrets = self._get_secrets()
        self._secrets = Secrets(**secrets)

    @property
    def args(self) -> Args:
        return self._args

    @property
    def secrets(self) -> Secrets:
        return self._secrets

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    def log_debug(self, message: str) -> None:
        if self._logger is not None:
            self._logger.debug(message)

    def log_info(self, message: str) -> None:
        if self._logger is not None:
            self._logger.info(message)

    def log_warning(self, message: str) -> None:
        if self._logger is not None:
            self._logger.warning(message)

    def log_error(self, message: str) -> None:
        if self._logger is not None:
            self._logger.error(message)

    @classmethod
    def _get_env_key(cls, key: str) -> str:
        return f"{cls._ENV_PREFIX}{key.upper()}"

    @classmethod
    def _get_args(cls) -> dict:
        args = {}
        for arg in Args.ARGS:
            args[arg] = os.environ.get(cls._get_env_key(arg))
        return args

    def _get_secrets(self) -> dict:
        secrets = {}
        for secret in Secrets.SECRETS:
            secrets[secret] = os.environ.get(self._get_env_key(secret))
            common_message = f"Python4CPM._get_secrets: {secret} ->"
            if secrets[secret]:
                self.log_info(f"{common_message} [*******]")
            else:
                self.log_info(f"{common_message} [NOT SET]")
        return secrets

    def _verify_action(self) -> None:
        if self.args.action not in self._VALID_ACTIONS:
            self.log_warning(
                f"Python4CPM._verify_action: unkonwn action -> {self.args.action}"
            )

    def _log_args(self) -> None:
        for key, value in vars(self._args).items():
            common_message = f"Python4CPM._log_args: {key.strip('_')} ->"
            if value:
                self.log_info(f"{common_message} {value}")
            else:
                self.log_info(f"{common_message} [NOT SET]")

    def _get_logger(self, name: str) -> logging.Logger:
        if self._args.logging is None:
            return None
        if self._args.logging.lower() != self._LOGGING_ENABLED_VALUE:
            return None
        os.makedirs(self._LOGS_DIR, exist_ok=True)
        logs_file = os.path.join(self._LOGS_DIR, f"{name}.log")
        logger = logging.getLogger(name)
        logging_level = self._args.logging_level.lower()
        if logging_level in self._LOGGING_LEVELS:
            logger.setLevel(self._LOGGING_LEVELS[logging_level])
        else:
            logger.setLevel(self._LOGGING_LEVELS["info"])
        handler = RotatingFileHandler(
            filename=logs_file,
            maxBytes=1 * 1024 * 1024,
            backupCount=2
        )
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def close_fail(self, unrecoverable: bool = False) -> None:
        if unrecoverable is False:
            code = self._FAILED_RECOVERABLE_CODE
        else:
            code = self._FAILED_UNRECOVERABLE_CODE
        self.log_error(f"Python4CPM.close_fail: closing with code {code}")
        sys.exit(code)

    def close_success(self) -> None:
        self.log_info(
            f"Python4CPM.close_success: closing with code {self._SUCCESS_CODE}"
        )
        sys.exit(self._SUCCESS_CODE)
