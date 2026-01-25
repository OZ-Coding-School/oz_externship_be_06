.PHONY: help format test run makemigrations migrate shell dbshell \
	up down restart logs ps build dtest dmypy-reset push-force fetch rebase-develop

COMPOSE_FILE := docker-compose.local.yml
ARGS = $(filter-out $@,$(MAKECMDGOALS))

help:
	@echo "Targets:"
	@echo "  run              Run Django dev server"
	@echo "  format           Run black + isort"
	@echo "  test             Run mypy + tests with coverage"
	@echo "  makemigrations   Create Django migrations"
	@echo "  migrate          Apply Django migrations"
	@echo "  shell            Django shell"
	@echo "  dbshell          Django db shell"
	@echo "  dtest            Run mypy + tests with coverage (Docker)"
	@echo "  dmakemigrations  Create Django migrations (Docker)"
	@echo "  dmigrate         Apply Django migrations (Docker)"
	@echo "  dshell           Django shell (Docker)"
	@echo "  ddbshell         Django db shell (Docker)"
	@echo "  build            Build Docker images"
	@echo "  up               Start Docker services"
	@echo "  down             Stop Docker services"
	@echo "  restart          Restart Docker services"
	@echo "  logs             Tail Docker logs"
	@echo "  ps               List Docker services"
	@echo "  dmypy-reset      Stop dmypy and clear cache"
	@echo "  push-force       Force push with lease"
	@echo "  fetch            Fetch from origin"
	@echo "  sync-develop     Fetch, checkout develop, and pull origin develop"
	@echo "  rebase-develop   Rebase onto origin/develop"

run:
	python manage.py runserver

format:
	bash resources/scripts/code_formatting.sh

test:
	bash resources/scripts/test.sh $(ARGS)

makemigrations:
	python manage.py makemigrations $(ARGS)

migrate:
	python manage.py migrate $(ARGS)

shell:
	python manage.py shell

dbshell:
	python manage.py dbshell

dtest:
	docker compose -f $(COMPOSE_FILE) exec django make test $(ARGS)

dmakemigrations:
	docker compose -f $(COMPOSE_FILE) exec django make makemigrations $(ARGS)

dmigrate:
	docker compose -f $(COMPOSE_FILE) exec django make migrate $(ARGS)

dshell:
	docker compose -f $(COMPOSE_FILE) exec django make shell

ddbshell:
	docker compose -f $(COMPOSE_FILE) exec django make dbshell

build:
	docker compose -f $(COMPOSE_FILE) build $(ARGS)

up:
	docker compose -f $(COMPOSE_FILE) up -d $(ARGS)

down:
	docker compose -f $(COMPOSE_FILE) down

restart:
	docker compose -f $(COMPOSE_FILE) restart

logs:
	docker compose -f $(COMPOSE_FILE) logs -f --tail=100 $(ARGS)

ps:
	docker compose -f $(COMPOSE_FILE) ps

dmypy-reset:
	poetry run dmypy stop || true
	rm -f .dmypy.json

push-force:
	@if [ -n "$(ARGS)" ]; then \
		git push origin $(ARGS) --force-with-lease; \
	else \
		git push --force-with-lease; \
	fi

fetch:
	git fetch origin

sync-develop:
	git fetch origin
	git checkout develop
	git pull origin develop

rebase-develop:
	git fetch origin
	git rebase origin/develop

%:
	@: