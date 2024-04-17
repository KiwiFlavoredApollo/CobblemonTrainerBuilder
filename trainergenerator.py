import logging

import inquirer

from commands.misc import PrintTrainerCommand, CloseTrainerBuilderCommand, ExportTrainerCommand, ImportTrainerCommand
from commands.pokemon import EditTeamCommand
from commands.trainer import EditTrainerCommand
from exceptions import TrainerBuilderCloseException
from trainer import Trainer


class TrainerGenerator:
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._trainer = Trainer("trainer")

    def open_trainer_builder_prompt(self):
        try:
            self._open_command_prompt()
        except TrainerBuilderCloseException:
            pass

    def _open_command_prompt(self):
        while True:
            COMMANDS = [
                ("Print", PrintTrainerCommand()),
                ("Trainer", EditTrainerCommand()),
                ("Pokemon", EditTeamCommand()),
                ("Export", ExportTrainerCommand()),
                ("Import", ImportTrainerCommand()),
                ("Close", CloseTrainerBuilderCommand())
            ]
            answer = inquirer.prompt([inquirer.List("command", "Select command", COMMANDS)])
            answer["command"].execute(self._trainer)
