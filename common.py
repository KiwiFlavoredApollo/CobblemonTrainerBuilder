import json
import logging
import os
import sys

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


def resource_path(relative_path):
    return os.path.join(_base_path(), relative_path)


def _base_path():
    try:
        return sys._MEIPASS
    except AttributeError:
        return os.path.abspath(".")
