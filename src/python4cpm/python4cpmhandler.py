from abc import ABC, abstractmethod
from python4cpm.python4cpm import Python4CPM


class Python4CPMHandler(ABC, Python4CPM):
    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)

    def run(self) -> None:
        actions = {
            self.ACTION_VERIFY: self.verify,
            self.ACTION_LOGON: self.logon,
            self.ACTION_CHANGE: self.change,
            self.ACTION_PRERECONCILE: self.prereconcile,
            self.ACTION_RECONCILE: self.reconcile
        }
        action = actions.get(self._args.action)
        if action is not None:
            action()
        else:
            raise ValueError(f"Unknown action: '{self._args.action}'")

    @abstractmethod
    def verify(self) -> None:
        pass

    @abstractmethod
    def logon(self) -> None:
        pass

    @abstractmethod
    def change(self) -> None:
        pass

    @abstractmethod
    def prereconcile(self) -> None:
        pass

    @abstractmethod
    def reconcile(self) -> None:
        pass
