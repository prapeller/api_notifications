import os
import subprocess
from pathlib import Path

from celery_app import celery_app
from core.enums import EnvEnum
from core.logger_config import setup_logger

SERVICE_DIR = Path(__file__).resolve().parent
SERVICE_NAME = SERVICE_DIR.stem

logger = setup_logger(SERVICE_NAME, SERVICE_DIR)


@celery_app.task(name='postgres_backup')
def postgres_backup():
    script_path = f"{os.getcwd()}/scripts/postgres/dump.sh"
    subprocess.run(script_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={'ENV': EnvEnum.prod})
    logger.info('postgres_backup task')
