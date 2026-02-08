import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from argparse import ArgumentParser


class Args:
    ARGS = (
        "action",
        "address",
        "username",
        "logon_username",
        "reconcile_username",
        "logging"
    )

    def __init__(
        self: str,
        action: str,
        address: str,
        username: str,
        reconcile_username: str,
        logon_username: str,
        logging: str
    ) -> None:
        self._action = action
        self._address = address
        self._username = username
        self._reconcile_username = reconcile_username
        self._logon_username = logon_username
        self._logging = logging

    @property
    def action(self) -> str:
        return self._action

    @property
    def address(self) -> str:
        return self._address

    @property
    def username(self) -> str:
        return self._username

    @property
    def reconcile_username(self) -> str:
        return self._reconcile_username

    @property
    def logon_username(self) -> str:
        return self._logon_username

    @property
    def logging(self) -> str:
        return self._logging


class Secrets:
    SECRETS = (
        "password",
        "logon_password",
        "reconcile_password",
        "new_password"
    )

    def __init__(
        self: str,
        password: str,
        logon_password: str,
        reconcile_password: str,
        new_password: str
    ) -> None:
        self._password = password
        self._logon_password = logon_password
        self._reconcile_password = reconcile_password
        self._new_password = new_password

    @property
    def password(self) -> str:
        return self._password

    @property
    def new_password(self) -> str:
        return self._new_password

    @property
    def logon_password(self) -> str:
        return self._logon_password

    @property
    def reconcile_password(self) -> str:
        return self._reconcile_password


class Python4CPM:
    ACTION_VERIFY = "logon"
    ACTION_CHANGE = "changepass"
    ACTION_PRERECONCILE = "prereconcilepass"
    ACTION_RECONCILE = "reconcilepass"
    _VALID_ACTIONS = (
        ACTION_VERIFY,
        ACTION_CHANGE,
        ACTION_PRERECONCILE,
        ACTION_RECONCILE,
    )
    _FILE_ROOT_DIR = os.path.dirname(__file__)
    _CPM_ROOT_DIR = os.path.dirname(_FILE_ROOT_DIR)
    _LOGS_DIR = os.path.join(_CPM_ROOT_DIR, "Logs", "ThirdParty", "Python4CPM")
    SUCCESS_PROMPT = "SUCCESS"
    FAILED_RECOVERABLE_PROMPT = "FAILED_RECOVERABLE"
    FAILED_UNRECOVERABLE_PROMPT = "FAILED_UNRECOVERABLE"

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

    def log_info(self, message: str) -> None:
        if self._logger is not None:
            self._logger.info(message)

    def log_warning(self, message: str) -> None:
        if self._logger is not None:
            self._logger.warning(message)

    def log_error(self, message: str) -> None:
        if self._logger is not None:
            self._logger.error(message)

    @staticmethod
    def _get_args() -> dict:
        parser = ArgumentParser()
        for arg in Args.ARGS:
            parser.add_argument(f"--{arg}")
        args = parser.parse_args()
        return dict(vars(args))

    def _get_secrets(self) -> dict:
        secrets = {}
        try:
            for prompt in Secrets.SECRETS:
                secrets[prompt] = input(f"{prompt}: ")
                common_message = f"Python4CPM._get_secrets: {prompt} ->"
                if secrets[prompt]:
                    self.log_info(f"{common_message} [*******]")
                else:
                    self.log_info(f"{common_message} [NOT SET]")
        except Exception as e:
            self.log_error(f"Python4CPM._get_secrets: {type(e).__name__}: {e}")
            self.close_fail()
        return secrets

    def _verify_action(self) -> None:
        if self.args.action not in self._VALID_ACTIONS:
            self.log_warning(
                f"Python4CPM._verify_action: unkonwn action "
                f"-> {self.args.action}"
            )

    def _log_args(self) -> None:
        for key, value in self._args.__dict__.items():
            common_message = f"Python4CPM._log_args: {key} ->"
            if value:
                self.log_info(f"{common_message} {value}")
            else:
                self.log_info(f"{common_message} [NOT SET]")

    def _get_logger(self, name: str) -> logging.Logger:
        if self._args.logging and self._args.logging.lower() == "yes":
            os.makedirs(self._LOGS_DIR, exist_ok=True)
            logs_file = os.path.join(self._LOGS_DIR, f"{name}.log")
            logger = logging.getLogger(name)
            logger.setLevel(logging.INFO)
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
        else:
            logger = None
        return logger

    def close_fail(self, unrecoverable: bool = False) -> None:
        if unrecoverable is True:
            prompt = self.FAILED_UNRECOVERABLE_PROMPT
        else:
            prompt = self.FAILED_RECOVERABLE_PROMPT
        self.log_error(f"Python4CPM.close_fail: closing with {prompt}")
        print(prompt)
        sys.exit(1)

    def close_success(self) -> None:
        prompt = self.SUCCESS_PROMPT
        self.log_info(f"Python4CPM.close_success: closing with {prompt}")
        print(prompt)
        sys.exit(0)
