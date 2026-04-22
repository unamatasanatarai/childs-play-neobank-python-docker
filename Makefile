# --- Configuration ---
DOCKER_COMPOSE = docker-compose
API_SERVICE = api
DB_SERVICE = db

# --- Main Commands ---

.PHONY: build
build: ## Build the docker containers (installs dependencies)
	$(DOCKER_COMPOSE) build

.PHONY: up
up: ## Start the containers in the background
	$(DOCKER_COMPOSE) up -d

.PHONY: stop
stop: ## Stop the containers
	$(DOCKER_COMPOSE) stop

.PHONY: down
down: ## Remove containers and networks
	$(DOCKER_COMPOSE) down

.PHONY: logs
logs: ## Tail the API logs
	$(DOCKER_COMPOSE) logs -f $(API_SERVICE)

# --- Database & Migrations ---

.PHONY: migrate-gen
migrate-gen: ## Generate a new migration script based on models
	$(DOCKER_COMPOSE) exec $(API_SERVICE) alembic revision --autogenerate -m "auto_migration"

.PHONY: migrate-up
migrate-up: ## Apply migrations to the database (Creates tables)
	$(DOCKER_COMPOSE) exec $(API_SERVICE) alembic upgrade head

.PHONY: seed
seed: ## Seed the database with demo users
	$(DOCKER_COMPOSE) exec $(API_SERVICE) python -m scripts.seed

.PHONY: db-shell
db-shell: ## Access the Postgres shell
	$(DOCKER_COMPOSE) exec $(DB_SERVICE) psql -U admin -d childspay_ledger

# --- Testing ---

test: ## Run the test suite on a temporary database
	$(DOCKER_COMPOSE) exec $(DB_SERVICE) psql -U admin -d postgres -c "DROP DATABASE IF EXISTS childspay_test;" || true
	$(DOCKER_COMPOSE) exec $(DB_SERVICE) psql -U admin -d postgres -c "CREATE DATABASE childspay_test;"
	$(DOCKER_COMPOSE) exec -e DATABASE_URL="postgresql+asyncpg://admin:development_password@db:5432/childspay_test" $(API_SERVICE) alembic upgrade head
	$(DOCKER_COMPOSE) exec -e DATABASE_URL="postgresql+asyncpg://admin:development_password@db:5432/childspay_test" $(API_SERVICE) python -m scripts.seed
	$(DOCKER_COMPOSE) exec -e DATABASE_URL="postgresql+asyncpg://admin:development_password@db:5432/childspay_test" $(API_SERVICE) pytest tests/

# --- Cleanup ---

.PHONY: clean
clean: ## Full Reset: Wipe DB volumes and pyc files
	$(DOCKER_COMPOSE) down -v
	find . -type d -name "__pycache__" -exec rm -rf {} +

.PHONY: destroy
destroy: ## Completely destroy the project (containers, volumes, images, orphans)
	$(DOCKER_COMPOSE) down -v --rmi all --remove-orphans
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -f migrations/versions/*.py

# --- Setup Routine ---

.PHONY: setup
setup: build up ## Full first-time setup
	@echo "⏳ Waiting for database to be ready..."
	@sleep 5
	$(MAKE) migrate-gen
	$(MAKE) migrate-up
	$(MAKE) seed
	@echo "🚀 Child'sPay is ready! Open index.html in your browser."

.PHONY: help
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'