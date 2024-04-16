import inquirer

from commands.interfaces import TrainerBuilderCommand
from exceptions import EditTrainerCommandCloseException


class EditTrainerCommand(TrainerBuilderCommand):
    def execute(self, trainer):
        try:
            self._edit_trainer(trainer)
        except EditTrainerCommandCloseException:
            pass

    def _edit_trainer(self, trainer):
        while True:
            choices = [
                ("Return", CloseEditTrainerCommand()),
                ("Reset", ResetTrainerCommand()),
                ("Rename", RenameTrainerCommand()),
                ("winCommand", EditWinCommandCommand()),
                ("canOnlyBeatOnce", EditCanOnlyBeatOnceCommand())
            ]
            answer = inquirer.prompt([inquirer.List("command", "Select to edit", choices)])
            answer["command"].execute(trainer)


class CloseEditTrainerCommand(TrainerBuilderCommand):
    def execute(self, trainer):
        raise EditTrainerCommandCloseException


class ResetTrainerCommand(TrainerBuilderCommand):
    def execute(self, trainer):
        trainer.reset()


class RenameTrainerCommand(TrainerBuilderCommand):
    def execute(self, trainer):
        answer = inquirer.prompt([inquirer.Text("name", "New trainer name", trainer.name)])
        trainer.name = answer["name"]


class EditWinCommandCommand(TrainerBuilderCommand):
    def execute(self, trainer):
        answer = inquirer.prompt(inquirer.Text("command", "Type winCommand"))
        trainer.set_win_command(answer["command"])


class EditCanOnlyBeatOnceCommand(TrainerBuilderCommand):
    def execute(self, trainer):
        answer = inquirer.prompt(inquirer.Confirm("command", message="Should trainer be beaten only once?"))
        if answer["command"]:
            trainer.set_can_only_beat_once()
        else:
            trainer.unset_can_only_beat_once()


class ImportTrainerCommand(TrainerBuilderCommand):
    def execute(self, trainer):
        pass
