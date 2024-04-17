import logging

from common import load_json_file, resource_path
from exceptions import PokemonNotExistSlotException
from pokemonfactory import PokemonFactory


class Trainer:
    DEFAULT_TRAINER_FILENAME = 'defaults/trainer.json'

    TEAM = "team"
    WIN_COMMAND = "winCommand"
    LOSS_COMMAND = "lossCommand"
    CAN_ONLY_BEAT_ONCE = "canOnlyBeatOnce"
    COOLDOWN_SECONDS = "cooldownSeconds"
    PARTY_MAXIMUM_LEVEL = "partyMaximumLevel"
    DEFEAT_REQUIRED_TRAINERS = "defeatRequiredTrainers"

    def __init__(self, name):
        self.name = name
        self.properties = load_json_file(resource_path(self.DEFAULT_TRAINER_FILENAME))

        self._logger = logging.getLogger(__name__)

    def add_pokemon_to_team(self, pokemon):
        self.properties[self.TEAM].append(pokemon)

    def get_pokemon_names(self):
        names = []
        for pokemon in self.properties[self.TEAM]:
            names.append(PokemonFactory.get_pokemon_name(pokemon))
        return names

    def set_win_command(self, win_command):
        self.properties[self.WIN_COMMAND] = win_command

    def set_can_only_beat_once(self, can_only_beat_once):
        self.properties[self.CAN_ONLY_BEAT_ONCE] = can_only_beat_once

    def reset(self):
        self.properties = load_json_file(self.DEFAULT_TRAINER_FILENAME)

    def remove_pokemon(self, slot):
        try:
            self._assert_slot_exist_pokemon(slot)
            self.properties[self.TEAM].pop(slot)
        except PokemonNotExistSlotException:
            pass

    def _assert_slot_exist_pokemon(self, slot):
        maximum_slot = len(self.properties[self.TEAM]) - 1
        if maximum_slot < slot:
            raise PokemonNotExistSlotException

    @property
    def team(self):
        return self.properties[self.TEAM]

    def import_from_json_file(self, filepath):
        try:
            self.properties = load_json_file(filepath)
            self._print_and_log_import_message(filepath)
        except FileNotFoundError:
            self._logger.debug("Following file could not be found: " + self.DEFAULT_TRAINER_FILENAME)

    def _print_and_log_import_message(self, filepath):
        message = "Imported from {}".format(filepath)
        print(message)
        self._logger.debug(message)