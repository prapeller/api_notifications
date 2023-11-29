ARG PYTHON_VERSION=3.11-slim-bullseye
FROM python:${PYTHON_VERSION} as my_python

FROM my_python as python-build-stage
ARG BUILD_ENV
ENV BUILD_ENV $BUILD_ENV

RUN apt-get update && apt-get install --no-install-recommends -y libpq-dev build-essential
COPY ./api_notifications/requirements .
COPY ./.envs .
RUN pip wheel --wheel-dir /usr/src/app/wheels -r ${BUILD_ENV}.txt

FROM my_python as python-run-stage

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install --no-install-recommends -y libpq-dev gettext curl netcat postgresql \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

COPY --from=python-build-stage /usr/src/app/wheels /wheels/
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
    && rm -rf /wheels/

COPY ./docker/api/entrypoint /entrypoint
COPY ./docker/api/start_prod /start_prod
COPY ./docker/api/start_local /start_local
COPY ./docker/api/start_tests /start_tests
RUN chmod +x /entrypoint
RUN chmod +x /start_prod
RUN chmod +x /start_local
RUN chmod +x /start_tests

COPY ./docker/api/celery/start_celeryworker /start_celeryworker
RUN chmod +x /start_celeryworker

COPY ./docker/api/celery/start_flower /start_flower
RUN chmod +x /start_flower

COPY ./docker/api/celery/start_beat /start_beat
RUN chmod +x /start_beat

ARG APP_HOME=/app/api_notifications
COPY ./api_notifications ${APP_HOME}
WORKDIR ${APP_HOME}
ENTRYPOINT ["/entrypoint"]