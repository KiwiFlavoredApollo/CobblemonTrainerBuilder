import json
import os

from commands.interfaces import TrainerBuilderCommand
from exceptions import TrainerBuilderCloseException


class PrintTrainerCommand(TrainerBuilderCommand):
    def execute(self, trainer):
        print(json.dumps(trainer.dict(), indent=4))


class ExportTrainerCommand(TrainerBuilderCommand):
    def execute(self, trainer):
        export = "export"
        filename = trainer.name + ".json"
        filepath = os.path.join(export, filename)

        if not os.path.exists(export):
            os.makedirs(export)

        with open(filepath, "w") as file:
            json.dump(trainer.dict(), file, indent=4)


class CloseTrainerBuilderCommand(TrainerBuilderCommand):
    def execute(self, trainer):
        raise TrainerBuilderCloseException
