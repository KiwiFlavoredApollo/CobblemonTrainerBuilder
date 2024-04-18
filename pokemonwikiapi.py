import json
import random
import sqlite3
import urllib.parse
from abc import ABC, abstractmethod
from json import JSONDecodeError

import requests

from common import create_double_logger, CooldownTimer
from exceptions import PokemonWikiConnectionNotExistException, PokemonNotExistException, \
    CachedResponseNotExistException, GenerationIxPokemonException


class PokemonWikiApi(ABC):
    @abstractmethod
    def get_pokemon_abilities(self, name):
        raise NotImplementedError

    @abstractmethod
    def is_pokemon_genderless(self, name):
        raise NotImplementedError

    @abstractmethod
    def assert_exist_pokemon(self, name):
        raise NotImplementedError

    @abstractmethod
    def get_pokemon_moves(self, name):
        raise NotImplementedError

    @abstractmethod
    def get_random_pokemon_name(self):
        raise NotImplementedError


class PokeApi(PokemonWikiApi):
    API_POKEMON_URL_PREFIX = "https://pokeapi.co/api/v2/pokemon/"
    API_POKEMON_SPECIES_URL_PREFIX = "https://pokeapi.co/api/v2/pokemon-species/"
    COOLDOWN_SECONDS = 1

    def __init__(self):
        self._logger = create_double_logger(__name__)
        self._database = Sqlite3("pokeapi")
        self._timer = CooldownTimer(self.COOLDOWN_SECONDS)

    def get_pokemon_abilities(self, name):
        EMPTY_ABILITIES = [""]
        try:
            url = urllib.parse.urljoin(self.API_POKEMON_URL_PREFIX, name)
            pokemon = self._get_response(url)
            return [self._get_ability_name(a) for a in pokemon["abilities"]]
        except requests.RequestException:
            return EMPTY_ABILITIES

    def _get_response(self, url):
        try:
            return self._get_response_from_database(url)
        except CachedResponseNotExistException:
            return self._get_response_from_internet_and_save_to_database(url)

    def _get_response_from_database(self, url):
        try:
            return json.loads(self._database.load_request(url))
        except JSONDecodeError:
            raise requests.RequestException

    def _get_response_from_internet_and_save_to_database(self, url):
        response = self._get_response_from_internet_after_cooldown_elapsed(url)
        self._database.save_request(response)
        return response.json()

    def _get_response_from_internet_after_cooldown_elapsed(self, url):
        while not self._timer.is_elapsed_cooldown():
            pass

        response = self._get_response_from_internet(url)
        self._timer.reset()
        return response

    def _get_response_from_internet(self, url):
        try:
            return requests.get(url)
        except requests.ConnectionError:
            raise PokemonWikiConnectionNotExistException("Cannot connect to PokeAPI")

    def _get_ability_name(self, ability):
        return ability["ability"]["name"].replace("-", "")

    def is_pokemon_genderless(self, name):
        try:
            url = urllib.parse.urljoin(self.API_POKEMON_SPECIES_URL_PREFIX, name)
            pokemon = self._get_response(url)
            return pokemon["gender_rate"] == -1
        except requests.RequestException:
            safe_guess = False
            self._logger.debug("Failed to request pokemon gender info from PokeAPI")
            return safe_guess

    def assert_exist_pokemon(self, name):
        try:
            url = urllib.parse.urljoin(self.API_POKEMON_URL_PREFIX, name)
            self._get_response(url)
        except requests.RequestException:
            raise PokemonNotExistException("Pokemon {} does not exist".format(name.capitalize()))

    def get_pokemon_moves(self, name):
        DEFAULT_MOVESET = ["tackle"]
        try:
            url = urllib.parse.urljoin(self.API_POKEMON_URL_PREFIX, name)
            pokemon = self._get_response(url)
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

    def get_random_pokemon_name(self):
        return self._get_random_pokemon_name_except_generation_ix()

    def _get_random_pokemon_name_except_generation_ix(self):
        while True:
            try:
                index = self._get_random_pokemon_index()
                url = urllib.parse.urljoin(self.API_POKEMON_SPECIES_URL_PREFIX, str(index))
                pokemon = self._get_response(url)
                name = pokemon["name"]
                self._assert_not_generation_ix(name)
                return name.replace("-", "")
            except GenerationIxPokemonException:
                pass

    def _get_random_pokemon_index(self):
        count = self._get_maximum_pokemon_count()
        return random.randint(1, count)

    def _get_maximum_pokemon_count(self):
        response = self._get_response(self.API_POKEMON_SPECIES_URL_PREFIX)
        return response["count"]

    def _assert_not_generation_ix(self, name):
        if self._get_pokemon_generation(name) == "generation-ix":
            raise GenerationIxPokemonException

    def _get_pokemon_generation(self, name):
        url = urllib.parse.urljoin(self.API_POKEMON_SPECIES_URL_PREFIX, name)
        response = self._get_response(url)
        return response["generation"]["name"]


class Database(ABC):
    @abstractmethod
    def save_request(self, request):
        raise NotImplementedError

    @abstractmethod
    def load_request(self, url):
        raise NotImplementedError


class Sqlite3(Database):
    DB_NAME = "pokemon.db"

    def __init__(self, table):
        self._table = table
        self._conn = sqlite3.connect(self.DB_NAME)
        self._create_table()

    def _create_table(self):
        cursor = self._conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS {table} "
                       "(url TEXT PRIMARY KEY, response TEXT)".format(table=self._table))
        cursor.close()

    def save_request(self, response):
        try:
            self._insert_row(response)
        except sqlite3.IntegrityError:
            self._update_row(response)

    def _insert_row(self, response):
        cursor = self._conn.cursor()

        cursor.execute("INSERT INTO {table} (url, response) VALUES (?, ?)"
                       .format(table=self._table), (response.url, response.text))
        self._conn.commit()

        cursor.close()

    def _update_row(self, response):
        cursor = self._conn.cursor()

        cursor.execute("UPDATE {table} SET response = ? WHERE url = ?"
                       .format(table=self._table), (response.url, response.text))
        self._conn.commit()

        cursor.close()

    def load_request(self, url):
        cursor = self._conn.cursor()

        cursor.execute("SELECT response FROM {table} WHERE url=?".format(table=self._table), (url,))
        result = cursor.fetchone()

        cursor.close()

        if self._is_not_exist_result(result):
            raise CachedResponseNotExistException
        return result[0]

    def _is_not_exist_result(self, result):
        return result is None or len(result) == 0
