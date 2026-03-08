import os


class Props:
    def __init__(self, *props):
        for prop in props:
            setattr(self, prop, prop)

    def __iter__(self) -> iter:
        return iter(self.__dict__.values())


class EnvHandler:
    PREFIX = "python4cpm_"
    OBJ_PREFIX = ""
    PROPS = Props()

    @classmethod
    def get_key(cls, key: str) -> str:
        env_key = f"{cls.PREFIX}{cls.OBJ_PREFIX}{key}"
        return env_key.upper()

    @classmethod
    def get(cls) -> object:
        kwargs = {}
        for prop in cls.PROPS:
            value = os.environ.get(cls.get_key(prop))
            kwargs[prop] = value if value is not None else ""
        return cls(**kwargs)
