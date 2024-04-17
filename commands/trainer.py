import inquirer

from commands.interface import Command
from common import load_json_file
from exceptions import EditTrainerCommandCloseException
from trainer import DEFAULT_TRAINER_FILENAME


class EditTrainerCommand(Command):
    def execute(self, trainer):
        try:
            self._edit_trainer(trainer)
        except EditTrainerCommandCloseException:
            pass

    def _edit_trainer(self, trainer):
        while True:
            COMMANDS = [
                ("Return", CloseEditTrainerCommand()),
                ("Reset", ResetTrainerCommand()),
                ("Rename", RenameTrainerCommand()),
                ("winCommand", EditWinCommandCommand()),
                ("canOnlyBeatOnce", EditCanOnlyBeatOnceCommand()),
            ]
            answer = inquirer.prompt([inquirer.List("command", "Select to edit", COMMANDS)])
            answer["command"].execute(trainer)


class CloseEditTrainerCommand(Command):
    def execute(self, trainer):
        raise EditTrainerCommandCloseException


class ResetTrainerCommand(Command):
    def execute(self, trainer):
        trainer.properties = load_json_file(DEFAULT_TRAINER_FILENAME)


class RenameTrainerCommand(Command):
    def execute(self, trainer):
        answer = inquirer.prompt([inquirer.Text("name", "New trainer name", trainer.name)])
        trainer.name = answer["name"]


class EditWinCommandCommand(Command):
    def execute(self, trainer):
        answer = inquirer.prompt([inquirer.Text("command", "Type winCommand")])
        trainer.properties["winCommand"] = answer["command"]


class EditCanOnlyBeatOnceCommand(Command):
    def execute(self, trainer):
        answer = inquirer.prompt(
            [inquirer.Confirm("command", message="Should trainer be beaten only once?", default=False)])
        trainer.properties["canOnlyBeatOnce"] = answer["command"]
