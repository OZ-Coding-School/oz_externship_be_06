.PHONY: help format test run makemigrations migrate shell dbshell \
	up down restart logs ps build dtest dmypy-reset push-force fetch rebase-develop

COMPOSE_FILE := docker-compose.local.yml

help:
	@echo "Targets:"
	@echo "  format           Run black + isort"
	@echo "  test             Run mypy + tests with coverage"
	@echo "  run              Run Django dev server"
	@echo "  makemigrations   Create Django migrations"
	@echo "  migrate          Apply Django migrations"
	@echo "  shell            Django shell"
	@echo "  dbshell          Django db shell"
	@echo "  build            Build Docker images"
	@echo "  up               Start Docker services"
	@echo "  down             Stop Docker services"
	@echo "  restart          Restart Docker services"
	@echo "  logs             Tail Docker logs"
	@echo "  ps               List Docker services"
	@echo "  dtest            Run tests in Docker (exec django)"
	@echo "  dmypy-reset      Stop dmypy and clear cache"
	@echo "  push-force       Force push with lease"
	@echo "  fetch            Fetch from origin"
	@echo "  rebase-develop   Rebase onto origin/develop"

format:
	bash resources/scripts/code_formatting.sh

test:
	bash resources/scripts/test.sh

run:
	python manage.py runserver

makemigrations:
	python manage.py makemigrations $(APP)

migrate:
	python manage.py migrate $(APP)

shell:
	python manage.py shell

dbshell:
	python manage.py dbshell

build:
	docker compose -f $(COMPOSE_FILE) build

up:
	docker compose -f $(COMPOSE_FILE) up -d

down:
	docker compose -f $(COMPOSE_FILE) down

restart:
	docker compose -f $(COMPOSE_FILE) restart

logs:
	docker compose -f $(COMPOSE_FILE) logs -f --tail=100

ps:
	docker compose -f $(COMPOSE_FILE) ps

dtest:
	docker compose -f $(COMPOSE_FILE) exec django make test

dmypy-reset:
	poetry run dmypy stop || true
	rm -f .dmypy.json

push-force:
	git push --force-with-lease

fetch:
	git fetch origin

rebase-develop:
	git fetch origin
	git rebase origin/develop
