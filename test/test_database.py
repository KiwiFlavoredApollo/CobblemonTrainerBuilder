import unittest

import requests

from pokemonwikiapi import Sqlite3


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.url = "https://pokeapi.co/api/v2/pokemon/ditto"
        self.response = requests.get(self.url)
        self.db = Sqlite3("pokeapi")

    def test_save_request(self):
        self.db.save_request(self.response)
        cached = self.db.load_request(self.url)
        assert cached == self.response.text

    def test_load_request(self):
        cached = self.db.load_request(self.url)
        assert cached == self.response.text