import inquirer

from commands.interface import Command
from common import load_json_file, create_double_logger
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
    def __init__(self):
        self._logger = create_double_logger(__name__)

    def execute(self, trainer):
        trainer.properties = load_json_file(DEFAULT_TRAINER_FILENAME)
        self._logger.info("Reset {trainer} to default".format(trainer=trainer.name))


class RenameTrainerCommand(Command):
    def __init__(self):
        self._logger = create_double_logger(__name__)

    def execute(self, trainer):
        answer = inquirer.prompt([inquirer.Text("name", "New trainer name", trainer.name)])
        trainer.name = answer["name"]
        self._logger.info("Renamed to {trainer}".format(trainer=trainer.name))


class EditWinCommandCommand(Command):
    def __init__(self):
        self._logger = create_double_logger(__name__)

    def execute(self, trainer):
        answer = inquirer.prompt([inquirer.Text("command", "Type winCommand")])
        trainer.properties["winCommand"] = answer["command"]
        self._logger.info("Set winCommand to {command}".format(command=answer["command"]))
        
        
class EditLossCommandCommand(Command):
    def __init__(self):
        self._logger = create_double_logger(__name__)

    def execute(self, trainer):
        answer = inquirer.prompt([inquirer.Text("command", "Type lossCommand")])
        trainer.properties["lossCommand"] = answer["command"]
        self._logger.info("Set lossCommand to {command}".format(command=answer["command"]))


class EditCanOnlyBeatOnceCommand(Command):
    def __init__(self):
        self._logger = create_double_logger(__name__)

    def execute(self, trainer):
        answer = inquirer.prompt(
            [inquirer.Confirm("boolean", message="Should trainer be beaten only once?", default=False)])
        trainer.properties["canOnlyBeatOnce"] = answer["boolean"]
        self._logger.info("Set canOnlyBeatOnce to {boolean}".format(boolean=answer["boolean"]))


class EditCooldownSecondsCommand(Command):
    def __init__(self):
        self._logger = create_double_logger(__name__)

    def execute(self, trainer):
        try:
            answer = inquirer.prompt([inquirer.Text("cooldown", "Type cooldownSeconds")])
            cooldown = int(answer["cooldown"])
            trainer.properties["cooldownSeconds"] = cooldown
            self._logger.info("Set cooldownSeconds to {cooldown}".format(cooldown=cooldown))
        except ValueError:
            self._logger.info("Invalid value was given for cooldownSeconds")


class EditPartyMaximumLevelCommand(Command):
    def __init__(self):
        self._logger = create_double_logger(__name__)

    def execute(self, trainer):
        try:
            answer = inquirer.prompt([inquirer.Text("level", "Type partyMaximumLevel")])
            level = int(answer["level"])
            assert_valid_pokemon_level(level)
            trainer.properties["partyMaximumLevel"] = level
            self._logger.info("Set partyMaximumLevel to {level}".format(level=level))
        except PokemonLevelInvalidException:
            self._logger.info("Invalid value was given for Pokemon level")