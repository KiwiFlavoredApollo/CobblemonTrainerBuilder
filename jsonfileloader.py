import json
import logging

logger = logging.getLogger(__name__)


def load_json_file(filename):
    with open(filename) as file:
        return json.load(file)


def is_valid_json_file(filepath):
    try:
        with open(filepath, 'r') as file:
            json.load(file)
        return True
    except (json.JSONDecodeError, FileNotFoundError):
        return False