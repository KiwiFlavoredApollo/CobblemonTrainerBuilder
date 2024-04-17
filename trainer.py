from common import load_json_file, resource_path
from pokemonfactory import get_pokemon_name

DEFAULT_TRAINER_FILENAME = 'defaults/trainer.json'


class Trainer:
    def __init__(self, name):
        self.name = name
        self.properties = load_json_file(resource_path(DEFAULT_TRAINER_FILENAME))


def get_pokemon_names(trainer):
    names = []
    for pokemon in trainer.properties["team"]:
        names.append(get_pokemon_name(pokemon))
    return names
