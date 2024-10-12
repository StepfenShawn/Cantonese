from abc import ABC, abstractmethod


class MetaVar(ABC):
    @abstractmethod
    def replace(self):
        pass
