import logging
import random
from abc import ABC, abstractmethod

from common import load_json_file, resource_path, to_lowercase
from exceptions import PokemonGenderlessException, PokemonCreationFailedException, MovesNotEnoughExistException, \
    InvalidPokemonLevelException, InvalidPokemonNameException, PokemonSpeciesNotExistException
from pokemonwikiapi import ApiRequestFailedException

DEFAULT_POKEMON_FILEPATH = "defaults/pokemon.json"
MOVESET_SIZE = 4
MAX_LEVEL = 100
MIN_LEVEL = 1
COBBLEMON_PREFIX = "cobblemon:"


class PokemonFactory(ABC):
    @abstractmethod
    def create(self, name):
        raise NotImplementedError


class RandomizedPokemonFactory(PokemonFactory):
    def __init__(self, api):
        self._logger = logging.getLogger(__name__)
        self._api = api
        self._default = load_json_file(resource_path(DEFAULT_POKEMON_FILEPATH))

    def create(self, name):
        try:
            self._assert_valid_pokemon_name(name)
            return self._create_pokemon(to_lowercase(name))
        except InvalidPokemonNameException as e:
            raise PokemonCreationFailedException(e.message)
        except PokemonSpeciesNotExistException:
            raise PokemonCreationFailedException("Pokemon {} does not exist".format(name.capitalize()))

    def _assert_valid_pokemon_name(self, name):
        if name == "":
            raise InvalidPokemonNameException("Pokemon's name cannot be empty string")
        if name.isdigit():
            raise InvalidPokemonNameException("Pokemon's name cannot be number string")

    def _create_pokemon(self, name):
        return {
            "species": self._create_species(name),
            "gender": self._create_gender(name),
            "level": self._create_level(),
            "nature": self._create_nature(),
            "ability": self._create_ability(name),
            "moveset": self._create_moveset(name),
            "ivs": self._create_ivs(),
            "evs": self._create_evs(),
            "shiny": self._create_shiny(),
            "heldItem": self._create_held_item()
        }

    def _create_species(self, name):
        try:
            self._api.assert_exist_pokemon_species(name)
            return COBBLEMON_PREFIX + name.replace("-", "")
        except ApiRequestFailedException as e:
            self._logger.info(e.message)
            raise PokemonSpeciesNotExistException

    def _create_gender(self, name):
        try:
            self._assert_not_pokemon_genderless(name)
            return random.choice(["MALE", "FEMALE"])
        except PokemonGenderlessException:
            return "GENDERLESS"
        except ApiRequestFailedException as e:
            self._logger.info(e.message)
            return self._default["gender"]

    def _assert_not_pokemon_genderless(self, name):
        if self._api.is_pokemon_genderless(name):
            raise PokemonGenderlessException

    def _create_level(self):
        return self._default["level"]

    def _create_nature(self):
        return select_random_nature()

    def _create_ability(self, name):
        try:
            abilities = self._api.get_pokemon_abilities(name)
            return random.choice(abilities)
        except ApiRequestFailedException as e:
            self._logger.info(e.message)
            return self._default["ability"]

    def _create_ivs(self):
        return {
            "hp": self._create_random_iv_value(),
            "attack": self._create_random_iv_value(),
            "defence": self._create_random_iv_value(),
            "special_attack": self._create_random_iv_value(),
            "special_defence": self._create_random_iv_value(),
            "speed": self._create_random_iv_value(),
        }

    def _create_random_iv_value(self):
        MIN_IV_VALUE = 0
        MAX_IV_VALUE = 31
        return random.randint(MIN_IV_VALUE, MAX_IV_VALUE)

    def _create_moveset(self, name):
        try:
            moves = self._api.get_pokemon_moves(name)
            return select_random_moveset(moves)
        except ApiRequestFailedException as e:
            self._logger.info(e.message)
            return self._default["moveset"]

    def _create_evs(self):
        return self._default["evs"]

    def _create_shiny(self):
        return self._default["shiny"]

    def _create_held_item(self):
        return self._default["heldItem"]


def select_random_nature():
    NATURES = [
        "hardy", "lonely", "brave", "adamant", "naughty",
        "bold", "docile", "relaxed", "impish", "lax",
        "timid", "hasty", "serious", "jolly", "naive",
        "modest", "mild", "quiet", "bashful", "rash",
        "calm", "gentle", "sassy", "careful", "quirky"
    ]
    return COBBLEMON_PREFIX + random.choice(NATURES)


def assert_valid_pokemon_level(level):
    if not MIN_LEVEL <= level <= MAX_LEVEL:
        raise InvalidPokemonLevelException


def get_random_pokemon_level():
    return random.randint(MIN_LEVEL, MAX_LEVEL)


def get_pokemon_name(pokemon):
    return pokemon["species"].replace(COBBLEMON_PREFIX, "")


def select_random_moveset(moves):
    try:
        _assert_exist_enough_moves(moves)
        return random.sample(moves, MOVESET_SIZE)
    except MovesNotEnoughExistException as e:
        return e.moves


def _assert_exist_enough_moves(moves):
    if len(moves) < MOVESET_SIZE:
        raise MovesNotEnoughExistException(moves)
