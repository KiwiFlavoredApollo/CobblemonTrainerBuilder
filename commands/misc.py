import json
import os

import inquirer

from commands.interfaces import Command
from exceptions import TrainerBuilderCloseException
from jsonfileloader import is_valid_json_file


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
    def execute(self, trainer):
        valid_json_files = self._get_valid_json_files()
        answer = inquirer.prompt([inquirer.List("file", "Select to import", valid_json_files)])
        print(answer["file"])  # TODO

    def _get_valid_json_files(self):
        import_dir = "import"
        filesets = [self._get_fileset(import_dir, f) for f in os.listdir(import_dir)]
        return list(filter(self._is_valid_json_file, filesets))

    def _get_fileset(self, import_dir, file):
        filepath = os.path.join(import_dir, file)
        return file, filepath

    def _is_valid_json_file(self, fileset):
        filepath = fileset[1]
        return is_valid_json_file(filepath)


class CloseTrainerBuilderCommand(Command):
    def execute(self, trainer):
        raise TrainerBuilderCloseException
