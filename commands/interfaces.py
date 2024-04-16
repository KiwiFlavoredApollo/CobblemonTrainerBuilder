from abc import ABC, abstractmethod


class TrainerBuilderCommand(ABC):
    @abstractmethod
    def execute(self, trainer):
        pass