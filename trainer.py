import json
import logging

from exceptions import PokemonNotExistSlotException
from jsonfileloader import load_json_file
from pokemonbuilder import PokemonBuilder
from pokemonwikiapi import PokemonNotExistException, PokemonWikiConnectionNotExistException


class Trainer:
    TRAINER_TEMPLATE_FILENAME = 'trainer-template.json'

    def __init__(self, name):
        self.name = name

        self._logger = logging.getLogger(__name__)
        self._team = self._load_team_from_template()
        self._win_command = self._load_win_command_from_template()
        self._can_only_beat_once = False  # TODO

    def _load_team_from_template(self):
        EMPTY_TEAM = []
        try:
            template = load_json_file(self.TRAINER_TEMPLATE_FILENAME)
            return template["team"]
        except FileNotFoundError:
            self._logger.debug("Following file could not be found: " + self.TRAINER_TEMPLATE_FILENAME)
            return EMPTY_TEAM

    def add_pokemon_to_team(self, pokemon):
        self._team.append(pokemon)

    def _load_win_command_from_template(self):
        EMPTY_WIN_COMMAND = ""
        try:
            template = load_json_file(self.TRAINER_TEMPLATE_FILENAME)
            return template["winCommand"]
        except FileNotFoundError:
            return EMPTY_WIN_COMMAND

    def dict(self):
        return {
            "team": self._team,
            "winCommand": self._win_command
        }

    def get_pokemon_names(self):
        names = []
        for pokemon in self._team:
            names.append(pokemon["species"].replace(PokemonBuilder.COBBLEMON_PREFIX, ""))
        return names

    def set_win_command(self, win_command):
        self._win_command = win_command

    def set_can_only_beat_once(self):
        self._can_only_beat_once = True

    def unset_can_only_beat_once(self):
        self._can_only_beat_once = False

    def reset(self):
        self._team = self._load_team_from_template()
        self._win_command = self._load_win_command_from_template()
        self._can_only_beat_once = False  # TODO

    def remove_pokemon(self, slot):
        try:
            self._assert_slot_exist_pokemon(slot)
            self._team.pop(slot)
        except PokemonNotExistSlotException:
            pass

    def _assert_slot_exist_pokemon(self, slot):
        maximum_slot = len(self._team) - 1
        if maximum_slot < slot:
            raise PokemonNotExistSlotException

    @property
    def team(self):
        return self._team