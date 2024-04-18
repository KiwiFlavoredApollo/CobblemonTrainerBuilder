class CommandPromptCloseException(Exception):
    pass


class PokemonGenderlessException(Exception):
    pass


class PokemonCreationFailedException(Exception):
    def __init__(self, message):
        self.message = message


class EditTeamCommandCloseException(Exception):
    pass


class InvalidPokemonNameException(Exception):
    def __init__(self, message):
        self.message = message


class ApiRequestFailedException(Exception):
    def __init__(self, message):
        self.message = message


class PokemonSpeciesNotExistException(Exception):
    pass


class MovesNotEnoughExistException(Exception):
    def __init__(self, moves):
        self.moves = moves


class EditTrainerCommandCloseException(Exception):
    pass


class EmptyPokemonSlotException(Exception):
    pass


class EditPokemonCommandCloseException(Exception):
    pass


class InvalidPokemonLevelException(Exception):
    pass


class CachedResponseNotExistException(Exception):
    pass


class GenerationIxPokemonException(Exception):
    pass
