import json
import os

from commands.interfaces import Command
from exceptions import TrainerBuilderCloseException


class PrintTrainerCommand(Command):
    def execute(self, trainer):
        print(json.dumps(trainer.dict(), indent=4))


class ExportTrainerCommand(Command):
    def execute(self, trainer):
        export = "export"
        filename = trainer.name + ".json"
        filepath = os.path.join(export, filename)

        if not os.path.exists(export):
            os.makedirs(export)

        with open(filepath, "w") as file:
            json.dump(trainer.dict(), file, indent=4)


class CloseTrainerBuilderCommand(Command):
    def execute(self, trainer):
        raise TrainerBuilderCloseException
