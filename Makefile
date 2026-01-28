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
	@echo "  sync-develop     Fetch, switch to develop, and pull origin develop"
	@echo "  rebase-develop   Rebase onto origin/develop"

run:
	python manage.py runserver

format:
	bash resources/scripts/code_formatting.sh

test:
	@if [ -z "$(ARGS)" ]; then \
		bash resources/scripts/test.sh; \
	else \
		TARGET="$(ARGS)"; \
		case "$$TARGET" in \
			apps/*) ;; \
			*) TARGET="apps/$$TARGET" ;; \
		esac; \
		SOURCE=$$(echo $$TARGET | cut -d'/' -f1,2); \
		echo "Starting Mypy for $$TARGET..."; \
		poetry run mypy $$TARGET || true; \
		echo "Starting Django Test with coverage (Target: $$TARGET)"; \
		echo "- Coverage Source: $$SOURCE"; \
		echo "- Test Target: $$TARGET"; \
		poetry run coverage run --source="$$SOURCE" manage.py test "$$TARGET"; \
		poetry run coverage report -m; \
		poetry run coverage html; \
	fi

makemigrations:
	python manage.py makemigrations $(ARGS)

migrate:
	python manage.py migrate $(ARGS)

shell:
	python manage.py shell

dbshell:
	python manage.py dbshell

dtest:
	docker compose -f $(COMPOSE_FILE) exec django make test ARGS="$(ARGS)"

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

push-f:
	@if [ -n "$(ARGS)" ]; then \
		git push origin $(ARGS) --force; \
	else \
		git push --force; \
	fi

fetch:
	git fetch origin

sync-develop:
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "⚠️  경고: 커밋되지 않은 변경 사항이 있습니다."; \
		echo "⚠️  브랜치를 이동하면 작업 내용이 꼬일 수 있습니다."; \
		read -p "⚠️  계속 진행하시겠습니까? [y/N]: " CONFIRM < /dev/tty; \
		if [ "$$CONFIRM" != "y" ] && [ "$$CONFIRM" != "Y" ]; then \
			echo "❌ 작업을 중단합니다. 기존 작업한 내역을 commit 또는 stash한 후에 다시 시도하세요."; \
			exit 1; \
		fi; \
	fi
	@echo ""
	@echo "---sync-develop 실행"
	git fetch origin
	@echo ""
	@echo "---develop 브랜치로 이동합니다."
	git switch develop
	@echo ""
	@echo "---🔄 develop 브랜치 최신화 중..."
	git pull origin develop
	@echo ""
	@echo "---develop 브랜치가 최신화 되었습니다."
	@echo "---현재 브랜치는 develop 입니다"
	@echo "🚨 🚨 🚨 🚨 🚨 작업할 브랜치로 이동하세요🚨 🚨 🚨 🚨 🚨"

rebase:
	git fetch origin
	git rebase develop

%:
	@: