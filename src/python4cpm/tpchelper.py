from .python4cpm import Python4CPM, Args
from unittest import mock


class TPCHelper:
    def __init__(
        self,
        action: str = "",
        address: str = "",
        username: str = "",
        logon_username: str = "",
        reconcile_username: str = "",
        logging: str = "",
        password: str = "",
        logon_password: str = "",
        reconcile_password: str = "",
        new_password: str = ""
    ) -> None:
        self._action = action
        self._address = address
        self._username = username
        self._logon_username = logon_username
        self._reconcile_username = reconcile_username
        self._logging = logging
        self._password = password
        self._logon_password = logon_password
        self._reconcile_password = reconcile_password
        self._new_password = new_password

    def run(self) -> Python4CPM:
        args = [
            "", # sys.argv[0] is ignored by argparse
            f"--{Args.ARGS[0]}={self._action}",
            f"--{Args.ARGS[1]}={self._address}",
            f"--{Args.ARGS[2]}={self._username}",
            f"--{Args.ARGS[3]}={self._logon_username}",
            f"--{Args.ARGS[4]}={self._reconcile_username}",
            f"--{Args.ARGS[5]}={self._logging}"
        ]
        secrets = [
            self._password,
            self._logon_password,
            self._reconcile_password,
            self._new_password
        ]
        iter_secrets = iter(secrets)
        with mock.patch(
            "sys.argv",
            args
        ), mock.patch(
            "builtins.input",
            lambda _: next(iter_secrets)
        ):
            return Python4CPM(self.__class__.__name__)
