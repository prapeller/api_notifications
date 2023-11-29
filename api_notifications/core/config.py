import os
from pathlib import Path

import pydantic as pd
import pydantic_settings as ps
from celery.schedules import crontab

from core.enums import TaskPriorityEnum


class Settings(ps.BaseSettings):
    API_AUTH_HOST: str
    API_AUTH_PORT: int

    API_NOTIFICATIONS_HOST: str
    API_NOTIFICATIONS_PORT: int

    PROJECT_NAME: str
    DOCS_URL: str = 'docs'

    SMTP_HOST: str
    SMTP_PORT: int
    EMAILS_FROM_EMAIL: pd.EmailStr
    TG_BOT_ID: str

    REDIS_HOST: str
    REDIS_PORT: int

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_PASSWORD: str

    AUTH_POSTGRES_HOST: str
    AUTH_POSTGRES_PORT: int
    AUTH_POSTGRES_USER: str
    AUTH_POSTGRES_DB: str
    AUTH_POSTGRES_PASSWORD: str

    SERVICE_TO_SERVICE_SECRET: str

    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    CELERY_TIMEZONE: str

    class Config:
        extra = 'allow'

    def __init__(self, DOCKER, DEBUG, BASE_DIR):
        if DEBUG and DOCKER:
            super().__init__(_env_file=[BASE_DIR / '../.envs/.docker-compose-local/.api',
                                        BASE_DIR / '../.envs/.docker-compose-local/.postgres',
                                        BASE_DIR / '../.envs/.docker-compose-local/.redis'])
        elif DEBUG and not DOCKER:
            super().__init__(_env_file=[BASE_DIR / '../.envs/.local/.api',
                                        BASE_DIR / '../.envs/.local/.postgres',
                                        BASE_DIR / '../.envs/.local/.redis'])
        else:
            super().__init__(_env_file=[BASE_DIR / '../.envs/.prod/.api',
                                        BASE_DIR / '../.envs/.prod/.postgres',
                                        BASE_DIR / '../.envs/.prod/.redis'])


DEBUG = os.getenv('DEBUG', False) == 'True'
DOCKER = os.getenv('DOCKER', False) == 'True'
BASE_DIR = Path(__file__).resolve().parent.parent

settings = Settings(DOCKER, DEBUG, BASE_DIR)

USER_NOTIFICATION_AVAILABLE_HOURS = [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

CELERY_BEAT_SCHEDULE = {
    'deliver_pending_messages_task': {
        'task': 'deliver_pending_messages_task',
        'schedule': crontab(hour='*', day_of_week='*'),
        'options': {'priority': TaskPriorityEnum.check_pending_messages_task_priority,
                    'queue': 'default'}
    },
    'send_email_task': {
        'task': 'send_email_task',
        'schedule': crontab(minute='*', day_of_week='*'),
        'kwargs': {'email_to': 'prapeller@mail', 'msg_text': 'test'},
        'options': {'priority': TaskPriorityEnum.email_task_priority,
                    'queue': 'default'}
    },
}
