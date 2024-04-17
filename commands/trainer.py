import inquirer

from commands.interface import Command
from common import load_json_file
from exceptions import EditTrainerCommandCloseException, PokemonLevelInvalidException
from pokemonfactory import assert_valid_pokemon_level
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
                ("lossCommand", EditLossCommandCommand()),
                ("canOnlyBeatOnce", EditCanOnlyBeatOnceCommand()),
                ("cooldownSeconds", EditCooldownSecondsCommand()),
                ("partyMaximumLevel", EditPartyMaximumLevelCommand()),
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
        
        
class EditLossCommandCommand(Command):
    def execute(self, trainer):
        answer = inquirer.prompt([inquirer.Text("command", "Type lossCommand")])
        trainer.properties["lossCommand"] = answer["command"]


class EditCanOnlyBeatOnceCommand(Command):
    def execute(self, trainer):
        answer = inquirer.prompt(
            [inquirer.Confirm("command", message="Should trainer be beaten only once?", default=False)])
        trainer.properties["canOnlyBeatOnce"] = answer["command"]


class EditCooldownSecondsCommand(Command):
    def execute(self, trainer):
        try:
            answer = inquirer.prompt([inquirer.Text("cooldown", "Type cooldownSeconds")])
            cooldown = int(answer["cooldown"])
            trainer.properties["cooldownSeconds"] = cooldown
        except ValueError:
            pass


class EditPartyMaximumLevelCommand(Command):
    def execute(self, trainer):
        try:
            answer = inquirer.prompt([inquirer.Text("level", "Type partyMaximumLevel")])
            level = int(answer["level"])
            assert_valid_pokemon_level(level)
            trainer.properties["partyMaximumLevel"] = level
        except PokemonLevelInvalidException:
            pass