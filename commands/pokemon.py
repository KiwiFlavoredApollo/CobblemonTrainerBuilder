import json
import logging
import random

import inquirer

from commands.interface import Command
from exceptions import PokemonCreationFailedException, EditTeamCommandCloseException, \
    EditSlotCommandCloseException, PokemonLevelInvalidException, MovesNotEnoughExistException
from pokemonbuilder import PokemonBuilder
from pokemonwikiapi import PokeApi as PokemonWikiApi


class EditTeamCommand(Command):
    def execute(self, trainer):
        try:
            self._edit_team(trainer)
        except EditTeamCommandCloseException:
            pass

    def _edit_team(self, trainer):
        while True:
            buttons = self._create_buttons(trainer)
            answer = inquirer.prompt([inquirer.List("button", "Select Pokemon", buttons)])
            answer["button"].execute(trainer)

    def _create_buttons(self, trainer):
        buttons = self._create_slots(trainer)
        buttons.insert(0, ("Return", CloseEditTeamCommand()))
        return buttons

    def _create_slots(self, trainer):
        slots = [(name.capitalize(), EditSlotCommand(index)) for index, name in enumerate(trainer.get_pokemon_names())]
        slots = self._fill_empty_slots(slots)
        return slots

    def _fill_empty_slots(self, choices):
        while len(choices) < 6:
            choices.append(("Empty", AddPokemonCommand()))
        return choices


class ConfirmAddPokemonCommand(Command):
    def execute(self, trainer):
        answer = inquirer.prompt([inquirer.Confirm("add", message="Add Pokemon?", default=False)])
        if answer["add"]:
            AddPokemonCommand().execute(trainer)


class AddPokemonCommand(Command):
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def execute(self, trainer):
        try:
            name = self._get_pokemon_name()
            pokemon = PokemonBuilder(PokemonWikiApi()).create_pokemon(name)
            trainer.add_pokemon_to_team(pokemon)
        except PokemonCreationFailedException as e:
            self._logger.debug(e.message)

    def _get_pokemon_name(self):
        answer = inquirer.prompt([inquirer.Text("name", "Pokemon Name")])
        return answer["name"].lower()


class EditSlotCommand(Command):
    def __init__(self, slot):
        self._slot = slot

    def execute(self, trainer):
        try:
            self._edit_slot(trainer)
        except EditSlotCommandCloseException:
            pass

    def _edit_slot(self, trainer):
        while True:
            COMMANDS = [
                ("Return", CloseEditSlotCommand()),
                ("Print", PrintPokemonCommand(self._slot)),
                ("Level", EditPokemonLevelCommand(self._slot)),
                ("Ability", EditPokemonAbilityCommand(self._slot)),
                ("Nature", EditPokemonNatureCommand(self._slot)),
                ("Moveset", EditPokemonMovesetCommand(self._slot)),
                ("Remove", RemovePokemonCommand(self._slot))
            ]
            answer = inquirer.prompt([inquirer.List("command", "Select action", COMMANDS)])
            answer["command"].execute(trainer)


class CloseEditSlotCommand(Command):
    def execute(self, trainer):
        raise EditSlotCommandCloseException


class RemovePokemonCommand(Command):
    def __init__(self, slot):
        self._slot = slot

    def execute(self, trainer):
        answer = inquirer.prompt([inquirer.Confirm("remove", message="Remove this pokemon?", default=False)])
        if answer["remove"]:
            trainer.remove_pokemon(self._slot)


class CloseEditTeamCommand(Command):
    def execute(self, trainer):
        raise EditTeamCommandCloseException


class EditPokemonLevelCommand(Command):
    def __init__(self, slot):
        self._slot = slot

    def execute(self, trainer):
        try:
            pokemon = trainer.team[self._slot]
            level = self._get_pokemon_level(pokemon)
            PokemonBuilder.assert_valid_pokemon_level(level)
            pokemon["level"] = level
        except PokemonLevelInvalidException:
            pass

    def _get_pokemon_level(self, pokemon):
        answer = inquirer.prompt([inquirer.Text("level", "Pokemon Level", default=pokemon["level"])])
        return int(answer["level"])


class EditPokemonAbilityCommand(Command):
    def __init__(self, slot):
        self._slot = slot

    def execute(self, trainer):
        pokemon = trainer.team[self._slot]
        name = PokemonBuilder.get_pokemon_name(pokemon)
        ability = self._get_pokemon_ability(name)
        pokemon["ability"] = ability

    def _get_pokemon_ability(self, name):
        abilities = PokemonWikiApi().get_pokemon_abilities(name)
        answer = inquirer.prompt([inquirer.List("ability", "Pokemon Ability", abilities)])
        return answer["ability"]


class EditPokemonNatureCommand(Command):
    def __init__(self, slot):
        self._slot = slot

    def execute(self, trainer):
        pokemon = trainer.team[self._slot]
        self._randomize_nature(pokemon)

    def _randomize_nature(self, pokemon):
        answer = inquirer.prompt([inquirer.Confirm("confirm", message="Randomize nature?", default=False)])
        if answer["confirm"]:
            pokemon["nature"] = PokemonBuilder.select_random_nature()



class EditPokemonMovesetCommand(Command):
    def __init__(self, slot):
        self._slot = slot

    def execute(self, trainer):
        pokemon = trainer.team[self._slot]
        self._randomize_moveset(pokemon)

    def _randomize_moveset(self, pokemon):
        answer = inquirer.prompt([inquirer.Confirm("confirm", message="Randomize moveset?", default=False)])
        if answer["confirm"]:
            name = PokemonBuilder.get_pokemon_name(pokemon)
            moves = PokemonWikiApi().get_pokemon_moves(name)
            pokemon["moveset"] = PokemonBuilder.select_random_moveset(moves)

class PrintPokemonCommand(Command):
    def __init__(self, slot):
        self._slot = slot

    def execute(self, trainer):
        json_pretty = json.dumps(trainer.team[self._slot], indent=4)
        print(json_pretty)
