import logging
import os
from datetime import datetime

from common import LOG_DIR, EXPORT_DIR, IMPORT_DIR
from trainergenerator import TrainerGenerator


def create_log_dir_if_not_exist():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)


def create_export_dir_if_not_exist():
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)


def create_import_dir_if_not_exist():
    if not os.path.exists(IMPORT_DIR):
        os.makedirs(IMPORT_DIR)


def get_log_filepath():
    extension = ".log"
    current_date_time = datetime.now()
    filename = current_date_time.strftime('%Y-%m-%d') + extension
    return os.path.join(LOG_DIR, filename)


create_log_dir_if_not_exist()
create_export_dir_if_not_exist()
create_import_dir_if_not_exist()

logging.basicConfig(filename=get_log_filepath(),
                    level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    TrainerGenerator().open_trainer_builder_prompt()
