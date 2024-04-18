import unittest

import requests

from pokemonwikiapi import Sqlite3


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.url = "https://pokeapi.co/api/v2/pokemon/ditto"
        self.response = requests.get(self.url)
        self.database = Sqlite3("pokeapi")

    def test_save_request(self):
        self.database.save_response(self.response)
        cached = self.database.load_response(self.url)
        assert cached == self.response.text

    def test_load_request(self):
        cached = self.database.load_response(self.url)
        assert cached == self.response.text