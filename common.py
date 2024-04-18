import json
import logging
import os
import sys
import time

LOG_DIR = "logs"
EXPORT_DIR = "export"
IMPORT_DIR = "import"

CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setLevel(logging.INFO)


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


def create_double_logger(name):
    logger = logging.getLogger(name)

    if CONSOLE_HANDLER not in logger.handlers:
        logger.addHandler(CONSOLE_HANDLER)

    return logger


class CooldownTimer:
    def __init__(self, cooldown):
        self._cooldown = cooldown
        self._timestamp = time.time()
        self._logger = create_double_logger(__name__)

    def is_elapsed_cooldown(self):
        elapsed_time = time.time() - self._timestamp
        return elapsed_time > self._cooldown

    def reset(self):
        self._timestamp = time.time()
        self._logger.debug("Reset cooldown timer")
