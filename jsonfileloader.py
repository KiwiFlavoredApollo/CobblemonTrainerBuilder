import json
import logging

logger = logging.getLogger(__name__)


def load_json_file(filename):
    with open(filename) as file:
        return json.load(file)
