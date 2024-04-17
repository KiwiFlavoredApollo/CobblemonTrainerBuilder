from common import load_json_file, resource_path

DEFAULT_TRAINER_FILENAME = 'defaults/trainer.json'


class Trainer:
    def __init__(self, name):
        self.name = name
        self.properties = load_json_file(resource_path(DEFAULT_TRAINER_FILENAME))
