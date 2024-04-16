import json
import os

import inquirer

from commands.interface import Command
from exceptions import TrainerBuilderCloseException
from common import is_valid_json_file


class PrintTrainerCommand(Command):
    def execute(self, trainer):
        print(json.dumps(trainer.dict(), indent=4))


class ExportTrainerCommand(Command):
    def execute(self, trainer):
        export_dir = "export"
        filename = trainer.name + ".json"
        filepath = os.path.join(export_dir, filename)

        if not os.path.exists(export_dir):
            os.makedirs(export_dir)

        with open(filepath, "w") as file:
            json.dump(trainer.dict(), file, indent=4)


class ImportTrainerCommand(Command):
    IMPORT_DIR = "import"

    def execute(self, trainer):
        selection = [("Return", CloseImportTrainerCommand())]
        json_files = self._get_valid_json_files()
        selection += [self._get_set_of_json_file_and_command(jf) for jf in json_files]
        answer = inquirer.prompt([inquirer.List("command", "Select to import", selection)])
        answer["command"].execute(trainer)

    def _get_valid_json_files(self):
        return list(filter(self._is_valid_json_file, os.listdir(self.IMPORT_DIR)))

    def _is_valid_json_file(self, filename):
        return is_valid_json_file(self._get_filepath(filename))

    def _get_set_of_json_file_and_command(self, filename):
        return filename, ImportTrainerFileCommand(self._get_filepath(filename))

    def _get_filepath(self, filename):
        return os.path.join(self.IMPORT_DIR, filename)


class CloseTrainerBuilderCommand(Command):
    def execute(self, trainer):
        raise TrainerBuilderCloseException


class CloseImportTrainerCommand(Command):
    def execute(self, trainer):
        pass


class ImportTrainerFileCommand(Command):
    def __init__(self, filepath):
        self._filepath = filepath

    def execute(self, trainer):
        trainer.import_from_json_file(self._filepath)
