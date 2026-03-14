from python4cpm.envhandler import EnvHandler, Props


class Args(EnvHandler):
    OBJ_PREFIX = "args_"
    PROPS = Props("action", "logging_level")

    def __init__(
        self,
        action: str | None,
        logging_level: str | None
    ) -> None:
        self._action = action
        self._logging_level = logging_level

    @property
    def action(self) -> str | None:
        return self._action

    @property
    def logging_level(self) -> str | None:
        return self._logging_level
