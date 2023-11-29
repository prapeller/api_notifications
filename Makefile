API_NOTIFICATIONS_LOCAL := -p api_notifications -f ./docker/api/docker-compose-local.yml
POSTGRES_NOTIFICATIONS_LOCAL := -p postgres_notifications -f ./docker/postgres/docker-compose-local.yml
DJANGO_NOTIFICATIONS_LOCAL := -p django_notifications -f ./docker/django/docker-compose-local.yml

API_NOTIFICATIONS_PROD := -p api_notifications -f ./docker/api/prod.yml
POSTGRES_NOTIFICATIONS_PROD := -p postgres_notifications -f ./docker/postgres/prod.yml
DJANGO_NOTIFICATIONS_PROD := -p django_notifications -f ./docker/django/prod.yml

build-loc:
	@docker network create shared_network || true
	docker-compose $(POSTGRES_NOTIFICATIONS_LOCAL) up --build -d --remove-orphans
	docker-compose $(API_NOTIFICATIONS_LOCAL) up --build -d --remove-orphans
	docker-compose $(DJANGO_NOTIFICATIONS_LOCAL) up --build -d --remove-orphans


build:
	@docker network create shared_network || true
	docker-compose $(POSTGRES_NOTIFICATIONS_PROD) up --build -d --remove-orphans
	docker-compose $(API_NOTIFICATIONS_PROD) up --build -d --remove-orphans
	docker-compose $(DJANGO_NOTIFICATIONS_PROD) up --build -d --remove-orphans

down-loc:
	docker-compose $(POSTGRES_NOTIFICATIONS_LOCAL) down
	docker-compose $(API_NOTIFICATIONS_LOCAL) down
	docker-compose $(DJANGO_NOTIFICATIONS_LOCAL) down

down:
	docker-compose $(POSTGRES_NOTIFICATIONS_PROD) down
	docker-compose $(API_NOTIFICATIONS_PROD) down
	docker-compose $(DJANGO_NOTIFICATIONS_PROD) down

down-v-loc:
	docker-compose $(POSTGRES_NOTIFICATIONS_LOCAL) down -v
	docker-compose $(API_NOTIFICATIONS_LOCAL) down -v
	docker-compose $(DJANGO_NOTIFICATIONS_LOCAL) down -v

down-v:
	docker-compose $(POSTGRES_NOTIFICATIONS_PROD) down -v
	docker-compose $(API_NOTIFICATIONS_PROD) down -v
	docker-compose $(DJANGO_NOTIFICATIONS_PROD) down -v


api-build-loc:
	docker-compose $(API_NOTIFICATIONS_LOCAL) up --build -d  --remove-orphans --no-deps api_notifications

api-build:
	docker-compose $(API_NOTIFICATIONS_PROD) up --build -d  --remove-orphans --no-deps api_notifications

api-pipinstall-loc:
	docker-compose $(API_NOTIFICATIONS_LOCAL)  run --rm api_notifications pip install -r requirements/local.txt

api-pipinstall:
	docker-compose $(API_NOTIFICATIONS_PROD)  run --rm api_notifications pip install -r requirements/prod.txt

api-check-ip:
	docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' api_notifications

api-redis-build-loc:
	docker-compose $(API_NOTIFICATIONS_LOCAL) up --build -d --remove-orphans --no-deps redis_notifications

api-rabbit-build-loc:
	docker-compose $(API_NOTIFICATIONS_LOCAL) up --build -d --remove-orphans --no-deps rabbitmq_notifications

api-celery-build-loc:
	docker-compose $(API_NOTIFICATIONS_LOCAL) up --build -d --remove-orphans --no-deps celery_worker_notifications celery_flower_notifications celery_beat_notifications

api-nginx-build-loc:
	docker-compose $(API_NOTIFICATIONS_LOCAL) up --build -d --remove-orphans --no-deps nginx_notifications

api-tests-build-loc:
	docker-compose $(API_NOTIFICATIONS_LOCAL) up --build -d --remove-orphans --no-deps tests_notifications

api-make-migration-loc:
	docker-compose $(API_NOTIFICATIONS_LOCAL) run --rm api_notifications python3 -m scripts.make_migration

api-make-migration:
	docker-compose $(API_NOTIFICATIONS_PROD) run --rm api_notifications python3 -m scripts.make_migration

api-migrate-loc:
	docker-compose $(API_NOTIFICATIONS_LOCAL) run --rm api_notifications python3 -m scripts.migrate

api-migrate:
	docker-compose $(API_NOTIFICATIONS_PROD) run --rm api_notifications python3 -m scripts.migrate



django-build-loc:
	docker-compose $(DJANGO_NOTIFICATIONS_LOCAL) up --build -d  --remove-orphans --no-deps

django-build:
	docker-compose $(DJANGO_NOTIFICATIONS_PROD) up --build -d  --remove-orphans --no-deps

django-down-loc:
	docker-compose $(DJANGO_NOTIFICATIONS_LOCAL) down

django-down:
	docker-compose $(DJANGO_NOTIFICATIONS_PROD) down

django-down-v-loc:
	docker-compose $(DJANGO_NOTIFICATIONS_LOCAL) down -v

django-down-v:
	docker-compose $(DJANGO_NOTIFICATIONS_PROD) down -v

django-superuser-loc:
	docker-compose $(DJANGO_NOTIFICATIONS_LOCAL) run --rm django_notifications python3 manage.py createsuperuser

django-superuser:
	docker-compose $(DJANGO_NOTIFICATIONS_PROD) run --rm django_notifications python3 manage.py createsuperuser

django-migrate-loc:
	docker-compose $(DJANGO_NOTIFICATIONS_LOCAL) run --rm django_notifications python3 manage.py migrate

django-migrate:
	docker-compose $(DJANGO_NOTIFICATIONS_PROD) run --rm django_notifications python3 manage.py migrate

django-make-migration-loc:
	docker-compose $(DJANGO_NOTIFICATIONS_LOCAL) run --rm django_notifications python3 manage.py makemigrations

django-make-migration:
	docker-compose $(DJANGO_NOTIFICATIONS_PROD) run --rm django_notifications python3 manage.py makemigrations

django-collectstatic-loc:
	docker-compose $(DJANGO_NOTIFICATIONS_LOCAL) run --rm django_notifications python3 manage.py collectstatic --no-input --clear

django-collectstatic:
	docker-compose $(DJANGO_NOTIFICATIONS_PROD) run --rm django_notifications python3 manage.py collectstatic --no-input --clear

django-shell-loc:
	docker-compose $(DJANGO_NOTIFICATIONS_LOCAL) run --rm django_notifications python3 manage.py shell

django-shell:
	docker-compose $(DJANGO_NOTIFICATIONS_PROD) run --rm django_notifications python3 manage.py shell

django-shell-plus-loc:
	docker-compose $(DJANGO_NOTIFICATIONS_LOCAL) run --rm django_notifications python3 manage.py shell_plus --plain

django-shell-plus:
	docker-compose $(DJANGO_NOTIFICATIONS_PROD) run --rm django_notifications python3 manage.py shell_plus --plain

django-shell-plus-sql-loc:
	docker-compose $(DJANGO_NOTIFICATIONS_LOCAL) run --rm django_notifications python3 manage.py shell_plus --print-sql

django-shell-plus-sql:
	docker-compose $(DJANGO_NOTIFICATIONS_PROD) run --rm django_notifications python3 manage.py shell_plus --print-sql

django-rebuild-index-loc:
	docker-compose $(DJANGO_NOTIFICATIONS_LOCAL) run --rm django_notifications python3 manage.py rebuild_index

django-rebuild-index:
	docker-compose $(DJANGO_NOTIFICATIONS_PROD) run --rm django_notifications python3 manage.py rebuild_index



postgres-build:
	docker-compose $(POSTGRES_NOTIFICATIONS_PROD) up --build -d  --remove-orphans --no-deps postgres_notifications

postgres-build-loc:
	docker-compose $(POSTGRES_NOTIFICATIONS_LOCAL) up --build -d  --remove-orphans --no-deps postgres_notifications

postgres-down-loc:
	docker-compose $(POSTGRES_NOTIFICATIONS_LOCAL) down

postgres-down:
	docker-compose $(POSTGRES_NOTIFICATIONS_PROD) down

postgres-down-v-loc:
	docker-compose $(POSTGRES_NOTIFICATIONS_LOCAL) down -v

postgres-down-v:
	docker-compose $(POSTGRES_NOTIFICATIONS_PROD) down -v

postgres-dump-loc:
	docker-compose $(POSTGRES_NOTIFICATIONS_LOCAL) exec postgres_notifications dump.sh

postgres-dump:
	docker-compose $(POSTGRES_NOTIFICATIONS_PROD) exec postgres_notifications dump.sh



check-config:
	docker-compose $(API_NOTIFICATIONS_PROD) config
	docker-compose $(POSTGRES_NOTIFICATIONS_PROD) config
	docker-compose $(DJANGO_NOTIFICATIONS_PROD) config

check-config-loc:
	docker-compose $(API_NOTIFICATIONS_LOCAL) config
	docker-compose $(POSTGRES_NOTIFICATIONS_LOCAL) config
	docker-compose $(DJANGO_NOTIFICATIONS_LOCAL) config



check-logs:
	docker-compose $(API_NOTIFICATIONS_PROD) logs
	docker-compose $(POSTGRES_NOTIFICATIONS_PROD) logs
	docker-compose $(DJANGO_NOTIFICATIONS_PROD) logs

check-logs-loc:
	docker-compose $(API_NOTIFICATIONS_LOCAL) logs
	docker-compose $(POSTGRES_NOTIFICATIONS_LOCAL) logs
	docker-compose $(DJANGO_NOTIFICATIONS_LOCAL) logs



flake8:
	docker-compose $(API_NOTIFICATIONS_LOCAL) exec api_notifications flake8 .

black-check:
	docker-compose $(API_NOTIFICATIONS_LOCAL) exec api_notifications black --check --exclude=venv .

black-diff:
	docker-compose $(API_NOTIFICATIONS_LOCAL) exec api_notifications black --diff --exclude=venv .

black:
	docker-compose $(API_NOTIFICATIONS_LOCAL) exec api_notifications black --exclude=venv .

isort-check:
	docker-compose $(API_NOTIFICATIONS_LOCAL) exec api_notifications isort . --check-only --skip venv

isort-diff:
	docker-compose $(API_NOTIFICATIONS_LOCAL) exec api_notifications isort . --diff --skip venv

isort:
	docker-compose $(API_NOTIFICATIONS_LOCAL) exec api_notifications isort . --skip venv
