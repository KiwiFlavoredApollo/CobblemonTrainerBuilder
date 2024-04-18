class CommandPromptCloseException(Exception):
    pass


class PokemonGenderlessException(Exception):
    pass


class PokemonCreationFailedException(Exception):
    def __init__(self, message):
        self.message = message


class EditTeamCommandCloseException(Exception):
    pass


class PokemonNameEmptyException(Exception):
    def __init__(self, message):
        self.message = message


class PokemonWikiConnectionNotExistException(Exception):
    def __init__(self, message):
        self.message = message


class PokemonNotExistException(Exception):
    def __init__(self, message):
        self.message = message


class MovesNotEnoughExistException(Exception):
    def __init__(self, moves):
        self.moves = moves


class EditTrainerCommandCloseException(Exception):
    pass


class EmptyPokemonSlotException(Exception):
    pass


class EditSlotCommandCloseException(Exception):
    pass


class PokemonLevelInvalidException(Exception):
    pass


class CachedResponseNotExistException(Exception):
    pass


class GenerationIxPokemonException(Exception):
    pass


class TrainerTeamFullException(Exception):
    pass
