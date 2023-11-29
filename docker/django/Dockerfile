ARG PYTHON_VERSION=3.10-slim-bullseye
FROM python:${PYTHON_VERSION} as my_python

FROM my_python as python-build-stage
ARG BUILD_ENV
ENV BUILD_ENV $BUILD_ENV

RUN apt-get update && apt-get install --no-install-recommends -y libpq-dev build-essential
COPY ./django_notifications/requirements .
COPY ./.envs .
RUN pip wheel --wheel-dir /usr/src/app/wheels -r ${BUILD_ENV}.txt

FROM my_python as python-run-stage

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install --no-install-recommends -y libpq-dev gettext curl netcat \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

COPY --from=python-build-stage /usr/src/app/wheels /wheels/
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
    && rm -rf /wheels/

COPY ./docker/django/entrypoint /entrypoint
COPY ./docker/django/start_django /start_django
RUN chmod +x /entrypoint
RUN chmod +x /start_django

ARG APP_HOME=/app/django_notifications
WORKDIR ${APP_HOME}
COPY ./django_notifications ${APP_HOME}

ENTRYPOINT ["/entrypoint"]