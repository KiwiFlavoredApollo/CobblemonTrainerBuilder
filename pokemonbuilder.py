import logging
import random

from exceptions import PokemonGenderlessException, PokemonCreationFailedException, MovesNotEnoughExistException, \
    PokemonLevelInvalidException
from pokemonwikiapi import PokemonNotExistException, PokemonWikiConnectionNotExistException


class PokemonBuilder:
    COBBLEMON_PREFIX = "cobblemon:"
    MOVESET_SIZE = 4
    MAX_LEVEL = 100
    MIN_LEVEL = 1

    def __init__(self, api):
        self._logger = logging.getLogger(__name__)
        self._api = api

    def create_pokemon(self, name):
        try:
            self._api.assert_exist_connection()
            self._api.assert_exist_pokemon(name)
            return self._create_random_pokemon(name)
        except PokemonWikiConnectionNotExistException as e:
            raise PokemonCreationFailedException(e.message)
        except PokemonNotExistException as e:
            raise PokemonCreationFailedException(e.message)

    def _create_pokemon_species(self, name):
        return self.COBBLEMON_PREFIX + name

    def _create_random_gender(self, name):
        try:
            self._assert_not_pokemon_genderless(name)
            return random.choice(["MALE", "FEMALE"])
        except PokemonGenderlessException:
            return "GENDERLESS"

    def _assert_not_pokemon_genderless(self, name):
        if self._api.is_pokemon_genderless(name):
            raise PokemonGenderlessException

    def _create_random_level(self):
        return random.randint(self.MIN_LEVEL, self.MAX_LEVEL)

    def _create_random_nature(self):
        return PokemonBuilder.select_random_nature()

    @staticmethod
    def select_random_nature():
        NATURES = [
            "hardy", "lonely", "brave", "adamant", "naughty",
            "bold", "docile", "relaxed", "impish", "lax",
            "timid", "hasty", "serious", "jolly", "naive",
            "modest", "mild", "quiet", "bashful", "rash",
            "calm", "gentle", "sassy", "careful", "quirky"
        ]
        return PokemonBuilder.COBBLEMON_PREFIX + random.choice(NATURES)

    def _create_random_ability(self, name):
        abilities = self._api.get_pokemon_abilities(name)
        return random.choice(abilities)

    def _create_random_ivs(self):
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

    def _create_random_moveset(self, name):
        moves = self._api.get_pokemon_moves(name)
        return PokemonBuilder.select_random_moveset(moves)

    @staticmethod
    def select_random_moveset(moves):
        try:
            PokemonBuilder._assert_exist_enough_moves(moves)
            return random.sample(moves, PokemonBuilder.MOVESET_SIZE)
        except MovesNotEnoughExistException as e:
            return e.moves

    @staticmethod
    def _assert_exist_enough_moves(moves):
        if len(moves) < PokemonBuilder.MOVESET_SIZE:
            raise MovesNotEnoughExistException(moves)

    def _create_empty_evs(self):
        return {}

    def _create_non_shiny(self):
        return False

    def _create_empty_held_item(self):
        return "minecraft:air"

    def _create_random_pokemon(self, name):
        return {
            "species": self._create_pokemon_species(name),
            "gender": self._create_random_gender(name),
            "level": self._create_random_level(),
            "nature": self._create_random_nature(),
            "ability": self._create_random_ability(name),
            "moveset": self._create_random_moveset(name),
            "ivs": self._create_random_ivs(),
            "evs": self._create_empty_evs(),
            "shiny": self._create_non_shiny(),
            "heldItem": self._create_empty_held_item()
        }

    @staticmethod
    def assert_valid_pokemon_level(level):
        if not PokemonBuilder.MIN_LEVEL <= level <= PokemonBuilder.MAX_LEVEL:
            raise PokemonLevelInvalidException

    @staticmethod
    def get_pokemon_name(pokemon):
        return pokemon["species"].replace(PokemonBuilder.COBBLEMON_PREFIX, "")
