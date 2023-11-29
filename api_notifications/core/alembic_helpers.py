import argparse
import configparser
import os
import tempfile

import sqlalchemy as sa
from alembic.config import Config

from core.config import BASE_DIR, settings

ALEMBIC_PATH = BASE_DIR / 'alembic'
ALEMBIC_INI_PATH = BASE_DIR / 'alembic.ini'
VERSIONS_PATH = ALEMBIC_PATH / 'versions'


def get_current_version():
    updated_config = get_updated_alembic_config()
    engine = sa.create_engine(next(updated_config).get_main_option('sqlalchemy.url'))
    connection = engine.connect()
    try:
        result = connection.execute(sa.text('select version_num from alembic_version'))
        row = result.fetchone()
        if row:
            current_version = row[0]
            return current_version
        return None
    finally:
        connection.close()
        engine.dispose()


def get_updated_alembic_config():
    # Read the alembic.ini file
    config = configparser.ConfigParser()
    config.read(ALEMBIC_INI_PATH)

    # Set the sqlalchemy.url adn script_location values
    config.set('alembic', 'sqlalchemy.url',
               f'postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@'
               f'{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}')
    config.set('alembic', 'script_location', str(ALEMBIC_PATH))

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_config_file:
        config.write(temp_config_file)
        temp_config_file_path = temp_config_file.name
    updated_config = Config(temp_config_file_path)
    try:
        yield updated_config
    finally:
        temp_config_file.close()


def get_next_version_index() -> int:
    return sum(1 for _ in VERSIONS_PATH.iterdir() if _.is_file())


def get_current_version_index():
    current_version_str = get_current_version()
    versions_files = os.listdir(VERSIONS_PATH)
    for filename in versions_files:
        if filename.startswith(f'{current_version_str}_'):
            index = int(filename.split('_')[1])
            return index


def get_args_message() -> str | None:
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--message', type=str, help='The message string')

    args = parser.parse_args()
    message = args.message
    return message
