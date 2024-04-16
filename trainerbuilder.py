import logging

import inquirer

from commands.misc import PrintTrainerCommand, CloseTrainerBuilderCommand, ExportTrainerCommand, ImportTrainerCommand
from commands.pokemon import EditTeamCommand
from commands.trainer import EditTrainerCommand
from exceptions import TrainerBuilderCloseException
from trainer import Trainer


class TrainerBuilder:
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._trainer = Trainer("trainer")

    def open_trainer_builder_prompt(self):
        try:
            self._build_trainer()
        except TrainerBuilderCloseException:
            pass

    def _build_trainer(self):
        while True:
            COMMANDS = [
                ("Trainer", EditTrainerCommand()),
                ("Pokemon", EditTeamCommand()),
                ("Print", PrintTrainerCommand()),
                ("Export", ExportTrainerCommand()),
                ("Import", ImportTrainerCommand()),
                ("Close", CloseTrainerBuilderCommand())
            ]
            answer = inquirer.prompt([inquirer.List("command", "Select command", COMMANDS)])
            answer["command"].execute(self._trainer)
