import os

from celery import Celery
from kombu import Exchange, Queue

from core.config import settings
from db import DATABASE_NOTIFICATIONS_URL_SYNC

celery_app = Celery(__name__, broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)
celery_app.conf.timezone = settings.CELERY_TIMEZONE
celery_app.conf.task_queues = (
    Queue('default', Exchange('default'), routing_key='default', queue_arguments={'x-max-priority': 10}),
)

celery_app.conf.update({'beat_dburi': DATABASE_NOTIFICATIONS_URL_SYNC})


def import_celery_tasks_from_services():
    root, subdirs, files = next(os.walk(f'{os.getcwd()}/services/'))
    for dir in subdirs:
        try:
            exec(f'from services.{dir} import celery_tasks')
        except ImportError:
            continue


import_celery_tasks_from_services()
