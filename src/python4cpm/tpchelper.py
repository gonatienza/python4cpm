from .python4cpm import Python4CPM, Args
from unittest import mock


class TPCHelper:
    @classmethod
    def run(
        cls,
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
    ) -> Python4CPM:
        args = [
            "", # sys.argv[0] is ignored by argparse
            f"--{Args.ARGS[0]}={action}",
            f"--{Args.ARGS[1]}={address}",
            f"--{Args.ARGS[2]}={username}",
            f"--{Args.ARGS[3]}={logon_username}",
            f"--{Args.ARGS[4]}={reconcile_username}",
            f"--{Args.ARGS[5]}={logging}"
        ]
        secrets = [
            password,
            logon_password,
            reconcile_password,
            new_password
        ]
        iter_secrets = iter(secrets)
        with mock.patch(
            "sys.argv",
            args
        ), mock.patch(
            "builtins.input",
            lambda _: next(iter_secrets)
        ):
            return Python4CPM(cls.__name__)
