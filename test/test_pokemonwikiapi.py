import unittest

from pokemonwikiapi import PokeApi


class TestPokeApi(unittest.TestCase):
    def setUp(self):
        self.api = PokeApi()

    def test_get_pokemon_ability(self):
        pokemon = "charmander"
        expected = ["blaze", "solarpower"]
        expected.sort()

        abilities = self.api.get_pokemon_abilities(pokemon)
        abilities.sort()

        assert abilities == expected

    def test_get_random_pokemon_name(self):
        name = self.api.get_random_pokemon_name()
        print(name)
