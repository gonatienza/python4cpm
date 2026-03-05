class Args:
    ARGS = (
        "action",
        "logging",
        "logging_level"
    )

    def __init__(
        self: str,
        action: str,
        logging: str,
        logging_level: str
    ) -> None:
        self._action = action
        self._logging = logging
        self._logging_level = logging_level

    @property
    def action(self) -> str:
        return self._action

    @property
    def logging(self) -> str:
        return self._logging

    @property
    def logging_level(self) -> str:
        return self._logging_level
