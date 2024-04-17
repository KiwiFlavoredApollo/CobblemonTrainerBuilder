import json
import logging
import os

import inquirer

from commands.interface import Command
from exceptions import TrainerBuilderCloseException
from common import is_valid_json_file, load_json_file


class PrintTrainerCommand(Command):
    def execute(self, trainer):
        print(json.dumps(trainer.properties, indent=2))


class ExportTrainerCommand(Command):
    EXPORT_DIR = "export"

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def execute(self, trainer):
        filename = self._get_filename(trainer)
        filepath = self._get_filepath(filename)
        answer = inquirer.prompt([inquirer.Confirm("export", message="Export to {}?".format(filepath))])
        if answer["export"]:
            self._export_json_file(trainer)

    def _export_json_file(self, trainer):
        if not os.path.exists(self.EXPORT_DIR):
            os.makedirs(self.EXPORT_DIR)

        filename = self._get_filename(trainer)
        filepath = self._get_filepath(filename)

        with open(filepath, "w") as file:
            json.dump(trainer.properties, file, indent=2)

        self._print_and_log_export_message(filepath)

    def _get_filename(self, trainer):
        return trainer.name + ".json"

    def _get_filepath(self, filename):
        return os.path.join(self.EXPORT_DIR, filename)

    def _print_and_log_export_message(self, filepath):
        message = "Exported to {}".format(filepath)
        print(message)
        self._logger.debug(message)


class ImportTrainerCommand(Command):
    IMPORT_DIR = "import"

    def execute(self, trainer):
        commands = [("Return", CloseImportTrainerCommand())]
        json_files = self._get_valid_json_files()
        commands += [self._get_set_of_json_file_and_command(jf) for jf in json_files]
        answer = inquirer.prompt([inquirer.List("command", "Select to import", commands)])
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
        trainer.properties = load_json_file(self._filepath)
