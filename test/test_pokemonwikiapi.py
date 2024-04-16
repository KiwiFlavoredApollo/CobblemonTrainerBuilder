import unittest

from pokemonwikiapi import PokeApi


class TestPokeApi(unittest.TestCase):
    def test_get_pokemon_ability(self):
        pokemon = "charmander"
        expected = ["blaze", "solar-power"]
        expected.sort()

        abilities = PokeApi().get_pokemon_abilities(pokemon)
        abilities.sort()

        assert(abilities == expected)
