import json
import logging
import sqlite3
from abc import ABC, abstractmethod
from json import JSONDecodeError

import requests

from exceptions import PokemonWikiConnectionNotExistException, PokemonNotExistException, DatabaseRowNotExistException


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
        self._db = Sqlite3("pokeapi")

    def get_pokemon_abilities(self, name):
        EMPTY_ABILITIES = [""]
        try:
            pokemon = self._get_response(self.API_POKEMON_URL_PREFIX + name)
            return [self._get_ability_name(a) for a in pokemon["abilities"]]
        except requests.RequestException:
            return EMPTY_ABILITIES

    def _get_response(self, url):
        try:
            return self._get_response_from_database(url)
        except DatabaseRowNotExistException:
            return self._get_response_from_internet_and_save_to_database(url)

    def _get_response_from_database(self, url):
        try:
            return json.loads(self._db.load_request(url))
        except JSONDecodeError:
            raise requests.RequestException

    def _get_response_from_internet_and_save_to_database(self, url):
        response = requests.get(url)
        self._db.save_request(response)
        return response.json()

    def _get_ability_name(self, ability):
        return ability["ability"]["name"].replace("-", "")

    def is_pokemon_genderless(self, name):
        try:
            pokemon = self._get_response(self.API_POKEMON_SPECIES_URL_PREFIX + name)
            return pokemon["gender_rate"] == -1
        except requests.RequestException:
            safe_guess = False
            self._logger.debug("Failed to request pokemon gender info from PokeAPI")
            return safe_guess

    def assert_exist_connection(self):
        try:
            self._get_response(self.API_POKEMON_SPECIES_URL_PREFIX)
        except requests.ConnectionError:
            raise PokemonWikiConnectionNotExistException("Cannot connect to PokeAPI")

    def assert_exist_pokemon(self, name):
        try:
            self._get_response(self.API_POKEMON_URL_PREFIX + name)
        except requests.RequestException:
            raise PokemonNotExistException("Pokemon {} does not exist".format(name))

    def get_pokemon_moves(self, name):
        DEFAULT_MOVESET = ["tackle"]
        try:
            pokemon = self._get_response(self.API_POKEMON_URL_PREFIX + name)
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
            raise DatabaseRowNotExistException
        return result[0]

    def _is_not_exist_result(self, result):
        return result is None or len(result) == 0
