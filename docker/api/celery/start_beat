#!/bin/bash

set -o errexit
set -o nounset

celery -A celery_app beat -S celery_sqlalchemy_scheduler.schedulers:DatabaseScheduler --loglevel=INFO