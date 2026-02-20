class Args:
    ARGS = (
        "action",
        "address",
        "username",
        "logon_username",
        "reconcile_username",
        "logging",
        "logging_level"
    )

    def __init__(
        self: str,
        action: str,
        address: str,
        username: str,
        reconcile_username: str,
        logon_username: str,
        logging: str,
        logging_level: str
    ) -> None:
        self._action = action
        self._address = address
        self._username = username
        self._reconcile_username = reconcile_username
        self._logon_username = logon_username
        self._logging = logging
        self._logging_level = logging_level

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

    @property
    def logging_level(self) -> str:
        return self._logging_level
