class TrainerBuilderCloseException(Exception):
    pass


class PokemonGenderlessException(Exception):
    pass


class PokemonCreationFailedException(Exception):
    def __init__(self, message):
        self.message = message


class EditTeamCommandCloseException(Exception):
    pass


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


class PokemonNotExistSlotException(Exception):
    pass


class EditSlotCommandCloseException(Exception):
    pass