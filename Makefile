.PHONY: help format test run makemigrations migrate shell dbshell \
	up down restart logs ps build

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

format:
	bash resources/scripts/code_formatting.sh

test:
	bash resources/scripts/test.sh

run:
	python manage.py runserver

makemigrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

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
