import logging

from common import load_json_file
from exceptions import PokemonNotExistSlotException
from pokemonbuilder import PokemonBuilder


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

        self._logger = logging.getLogger(__name__)
        self._properties = load_json_file(self.DEFAULT_TRAINER_FILENAME)

    def add_pokemon_to_team(self, pokemon):
        self._properties[self.TEAM].append(pokemon)

    def dict(self):
        return self._properties

    def get_pokemon_names(self):
        names = []
        for pokemon in self._properties[self.TEAM]:
            n = self._remove_cobblemon_prefix_from_pokemon_name(pokemon["species"])
            names.append(n)
        return names

    def _remove_cobblemon_prefix_from_pokemon_name(self, name):
        return name.replace(PokemonBuilder.COBBLEMON_PREFIX, "")

    def set_win_command(self, win_command):
        self._properties[self.WIN_COMMAND] = win_command

    def set_can_only_beat_once(self, can_only_beat_once):
        self._properties[self.CAN_ONLY_BEAT_ONCE] = can_only_beat_once

    def reset(self):
        self._properties = load_json_file(self.DEFAULT_TRAINER_FILENAME)

    def remove_pokemon(self, slot):
        try:
            self._assert_slot_exist_pokemon(slot)
            self._properties[self.TEAM].pop(slot)
        except PokemonNotExistSlotException:
            pass

    def _assert_slot_exist_pokemon(self, slot):
        maximum_slot = len(self._properties[self.TEAM]) - 1
        if maximum_slot < slot:
            raise PokemonNotExistSlotException

    @property
    def team(self):
        return self._properties[self.TEAM]

    def import_from_json_file(self, filepath):
        try:
            self._properties = load_json_file(filepath)
        except FileNotFoundError:
            self._logger.debug("Following file could not be found: " + self.DEFAULT_TRAINER_FILENAME)

