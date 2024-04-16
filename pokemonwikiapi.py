import logging
import random
from abc import ABC, abstractmethod

import requests

from exceptions import PokemonWikiConnectionNotExistException, PokemonNotExistException


class PokemonWikiApi(ABC):
    @abstractmethod
    def get_pokemon_abilities(self, name):
        raise NotImplementedError

    @abstractmethod
    def is_pokemon_genderless(self, name):
        raise NotImplementedError

    @abstractmethod
    def assert_exist_connection(self):
        raise NotImplementedError

    @abstractmethod
    def assert_exist_pokemon(self, name):
        raise NotImplementedError

    @abstractmethod
    def get_pokemon_moves(self, name):
        raise NotImplementedError


class PokeApi(PokemonWikiApi):
    API_POKEMON_URL_PREFIX = "https://pokeapi.co/api/v2/pokemon/"
    API_POKEMON_SPECIES_URL_PREFIX = "https://pokeapi.co/api/v2/pokemon-species/"

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def get_pokemon_abilities(self, name):
        EMPTY_ABILITIES = [""]
        try:
            pokemon = requests.get(self.API_POKEMON_URL_PREFIX + name).json()
            return [self._get_ability_name(a) for a in pokemon["abilities"]]
        except requests.RequestException:
            return EMPTY_ABILITIES

    def _get_ability_name(self, ability):
        return ability["ability"]["name"].replace("-", "")

    def is_pokemon_genderless(self, name):
        try:
            pokemon = requests.get(self.API_POKEMON_SPECIES_URL_PREFIX + name).json()
            return pokemon["gender_rate"] == -1
        except requests.RequestException:
            safe_guess = False
            self._logger.debug("Failed to request pokemon gender info from PokeAPI")
            return safe_guess

    def assert_exist_connection(self):
        try:
            requests.get(self.API_POKEMON_SPECIES_URL_PREFIX)
        except requests.ConnectionError:
            raise PokemonWikiConnectionNotExistException("Cannot connect to PokeAPI")

    def assert_exist_pokemon(self, name):
        try:
            requests.get(self.API_POKEMON_URL_PREFIX + name).json()
        except requests.RequestException:
            raise PokemonNotExistException("Pokemon {} does not exist".format(name))

    def get_pokemon_moves(self, name):
        DEFAULT_MOVESET = ["tackle"]
        try:
            pokemon = requests.get(self.API_POKEMON_URL_PREFIX + name).json()
            return self._get_move_names(pokemon["moves"])
        except requests.RequestException:
            return DEFAULT_MOVESET

    def _get_move_names(self, moves):
        move_names = []
        for m in moves:
            move_name = m["move"]["name"]
            without_hyphen = move_name.replace("-", "")
            move_names.append(without_hyphen)
        return move_names
