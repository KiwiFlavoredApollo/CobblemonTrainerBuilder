import json
import logging

logger = logging.getLogger(__name__)


def load_json_file(filepath):
    with open(filepath, "r") as file:
        return json.load(file)


def is_valid_json_file(filepath):
    try:
        load_json_file(filepath)
        return True
    except (json.JSONDecodeError, FileNotFoundError):
        return False