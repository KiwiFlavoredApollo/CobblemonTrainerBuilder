import json

import inquirer

from commands.interface import Command
from common import create_double_logger
from exceptions import PokemonCreationFailedException, EditTeamCommandCloseException, \
    EditSlotCommandCloseException, PokemonLevelInvalidException, EmptyPokemonSlotException
from pokemonfactory import RandomizedPokemonFactory, assert_valid_pokemon_level, \
    get_pokemon_name, select_random_nature, select_random_moveset
from pokemonwikiapi import PokeApi as PokemonWikiApi


class EditTeamCommand(Command):
    def execute(self, trainer):
        try:
            self._edit_team(trainer)
        except EditTeamCommandCloseException:
            pass

    def _edit_team(self, trainer):
        while True:
            team = trainer.properties["team"]
            buttons = [
                ("Return", CloseEditTeamCommand()),
                (self._get_button_name(team, 0), self._get_button_command(team, 0)),
                (self._get_button_name(team, 1), self._get_button_command(team, 1)),
                (self._get_button_name(team, 2), self._get_button_command(team, 2)),
                (self._get_button_name(team, 3), self._get_button_command(team, 3)),
                (self._get_button_name(team, 4), self._get_button_command(team, 4)),
                (self._get_button_name(team, 5), self._get_button_command(team, 5)),
                ("Team Level", EditTeamLevelCommand()),
                ("Random Team", ConfirmGenerateRandomTeamCommand()),
            ]
            answer = inquirer.prompt([inquirer.List("button", "Select Pokemon", buttons)])
            answer["button"].execute(trainer)

    def _get_button_name(self, team, slot):
        try:
            self._assert_exist_pokemon(team, slot)
            cap_name = self._get_capitalized_pokemon_name(team, slot)
            return self._prepend_slot_number(cap_name, slot)
        except EmptyPokemonSlotException:
            return self._prepend_slot_number("Empty", slot)

    def _assert_exist_pokemon(self, team, slot):
        try:
            team[slot]
        except IndexError:
            raise EmptyPokemonSlotException

    def _prepend_slot_number(self, string, slot):
        delimiter = " "
        return delimiter.join(["[{}]".format(slot + 1), string])

    def _get_capitalized_pokemon_name(self, team, slot):
        name = get_pokemon_name(team[slot])
        return name.capitalize()

    def _get_button_command(self, team, slot):
        try:
            self._assert_exist_pokemon(team, slot)
            return EditSlotCommand(slot)
        except EmptyPokemonSlotException:
            return AddPokemonCommand()


class ConfirmAddPokemonCommand(Command):
    def execute(self, trainer):
        answer = inquirer.prompt([inquirer.Confirm("add", message="Add Pokemon?", default=False)])
        if answer["add"]:
            AddPokemonCommand().execute(trainer)


class AddPokemonCommand(Command):
    def __init__(self):
        self._logger = create_double_logger(__name__)

    def execute(self, trainer):
        try:
            name = self._get_pokemon_name()
            pokemon = RandomizedPokemonFactory(PokemonWikiApi()).create(name)
            trainer.properties["team"].append(pokemon)
            cap_name = get_pokemon_name(pokemon).capitalize()
            self._logger.info("Added {pokemon} to {trainer}".format(pokemon=cap_name, trainer=trainer.name))
        except PokemonCreationFailedException as e:
            self._logger.info(e.message)

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
                ("Remove", ConfirmRemovePokemonCommand(self._slot))
            ]
            answer = inquirer.prompt([inquirer.List("command", "Select action", COMMANDS)])
            answer["command"].execute(trainer)


class CloseEditSlotCommand(Command):
    def execute(self, trainer):
        raise EditSlotCommandCloseException


class RemovePokemonCommand(Command):
    def __init__(self, slot):
        self._logger = create_double_logger(__name__)
        self._slot = slot

    def execute(self, trainer):
        team = trainer.properties["team"]
        pokemon = team[self._slot]
        team.pop(self._slot)

        cap_name = get_pokemon_name(pokemon).capitalize()
        self._logger.info("Removed {pokemon} from {trainer}".format(pokemon=cap_name, trainer=trainer.name))

        CloseEditSlotCommand().execute(trainer)

    def _confirm_remove_pokemon(self):
        answer = inquirer.prompt([inquirer.Confirm("remove", message="Remove this pokemon?", default=False)])
        return answer["remove"]


class ConfirmRemovePokemonCommand(Command):
    def __init__(self, slot):
        self._logger = create_double_logger(__name__)
        self._slot = slot

    def execute(self, trainer):
        if not self._confirm_remove_pokemon():
            return

        RemovePokemonCommand(self._slot).execute(trainer)

    def _confirm_remove_pokemon(self):
        answer = inquirer.prompt([inquirer.Confirm("remove", message="Remove this pokemon?", default=False)])
        return answer["remove"]


class CloseEditTeamCommand(Command):
    def execute(self, trainer):
        raise EditTeamCommandCloseException


class EditPokemonLevelCommand(Command):
    def __init__(self, slot):
        self._logger = create_double_logger(__name__)
        self._slot = slot

    def execute(self, trainer):
        try:
            team = trainer.properties["team"]
            pokemon = team[self._slot]
            level = self._ask_pokemon_level(pokemon)
            assert_valid_pokemon_level(level)
            pokemon["level"] = level
            cap_name = get_pokemon_name(pokemon).capitalize()
            self._logger.info("Set level of {pokemon} to {level}".format(pokemon=cap_name, level=level))
        except PokemonLevelInvalidException:
            self._logger.info("Invalid value was given for Pokemon level")

    def _ask_pokemon_level(self, pokemon):
        answer = inquirer.prompt([inquirer.Text("level", "Pokemon Level", default=pokemon["level"])])
        return int(answer["level"])


class EditPokemonAbilityCommand(Command):
    def __init__(self, slot):
        self._logger = create_double_logger(__name__)
        self._slot = slot

    def execute(self, trainer):
        team = trainer.properties["team"]
        pokemon = team[self._slot]
        name = get_pokemon_name(pokemon)
        ability = self._ask_pokemon_ability(name)
        pokemon["ability"] = ability
        cap_name = name.capitalize()
        self._logger.info("Set ability of {pokemon} to {ability}".format(pokemon=cap_name, ability=ability))

    def _ask_pokemon_ability(self, name):
        abilities = PokemonWikiApi().get_pokemon_abilities(name)
        answer = inquirer.prompt([inquirer.List("ability", "Pokemon Ability", abilities)])
        return answer["ability"]


class EditPokemonNatureCommand(Command):
    def __init__(self, slot):
        self._logger = create_double_logger(__name__)
        self._slot = slot

    def execute(self, trainer):
        if not self._confirm_randomize_nature():
            return

        team = trainer.properties["team"]
        pokemon = team[self._slot]
        nature = select_random_nature()
        pokemon["nature"] = nature

        cap_name = get_pokemon_name(pokemon).capitalize()
        self._logger.info("Set nature of {pokemon} to {nature}".format(pokemon=cap_name, nature=nature))

    def _confirm_randomize_nature(self):
        answer = inquirer.prompt([inquirer.Confirm("confirm", message="Randomize nature?", default=False)])
        return answer["confirm"]


class EditPokemonMovesetCommand(Command):
    def __init__(self, slot):
        self._logger = create_double_logger(__name__)
        self._slot = slot

    def execute(self, trainer):
        if not self._confirm_randomize_moveset():
            return

        team = trainer.properties["team"]
        pokemon = team[self._slot]
        name = get_pokemon_name(pokemon)
        moves = PokemonWikiApi().get_pokemon_moves(name)
        moveset = select_random_moveset(moves)
        pokemon["moveset"] = moveset

        cap_name = get_pokemon_name(pokemon).capitalize()
        self._logger.info("Set moveset of {pokemon} to {moveset}".format(pokemon=cap_name, moveset=moveset))

    def _confirm_randomize_moveset(self):
        answer = inquirer.prompt([inquirer.Confirm("confirm", message="Randomize moveset?", default=False)])
        return answer["confirm"]


class PrintPokemonCommand(Command):
    def __init__(self, slot):
        self._slot = slot

    def execute(self, trainer):
        team = trainer.properties["team"]
        json_pretty = json.dumps(team[self._slot], indent=2)
        print(json_pretty)


class EditTeamLevelCommand(Command):
    def __init__(self):
        self._logger = create_double_logger(__name__)

    def execute(self, trainer):
        try:
            level = self._ask_team_level()
            team = trainer.properties["team"]
            assert_valid_pokemon_level(level)
            for pokemon in team:
                pokemon["level"] = level
            self._logger.info("Set team level of {trainer} to {level}".format(trainer=trainer.name, level=level))
        except PokemonLevelInvalidException:
            self._logger.info("Invalid value was given for Pokemon level")

    def _ask_team_level(self):
        answer = inquirer.prompt([inquirer.Text("level", "Team Level")])
        return int(answer["level"])


class GenerateRandomTeamCommand(Command):
    def __init__(self):
        self._logger = create_double_logger(__name__)

    def execute(self, trainer):
        api = PokemonWikiApi()
        trainer.properties["team"] = [
            RandomizedPokemonFactory(api).create(api.get_random_pokemon_name()),
            RandomizedPokemonFactory(api).create(api.get_random_pokemon_name()),
            RandomizedPokemonFactory(api).create(api.get_random_pokemon_name()),
            RandomizedPokemonFactory(api).create(api.get_random_pokemon_name()),
            RandomizedPokemonFactory(api).create(api.get_random_pokemon_name()),
            RandomizedPokemonFactory(api).create(api.get_random_pokemon_name()),
        ]
        self._logger.info("Successfully generated a new team")


class ConfirmGenerateRandomTeamCommand(Command):
    def execute(self, trainer):
        if not self._confirm_generate_random_team():
            return

        GenerateRandomTeamCommand().execute(trainer)

    def _confirm_generate_random_team(self):
        message = "Generate random team? (All Pokemons will be overridden and this task takes about a minute)"
        answer = inquirer.prompt([inquirer.Confirm("confirm", message=message, default=False)])
        return answer["confirm"]
