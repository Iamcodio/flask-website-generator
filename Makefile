# Makefile for Flask Website Generator Docker Operations

.PHONY: help build up down logs shell test clean dev prod

# Default environment
ENV ?= dev

help: ## Show this help message
	@echo 'Usage: make [target] [ENV=dev|prod]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build Docker images
	@echo "Building images for $(ENV) environment..."
	@if [ "$(ENV)" = "prod" ]; then \
		docker-compose -f docker-compose.yml -f docker-compose.prod.yml build; \
	else \
		docker-compose -f docker-compose.yml -f docker-compose.dev.yml build; \
	fi

up: ## Start all services
	@echo "Starting $(ENV) environment..."
	@if [ "$(ENV)" = "prod" ]; then \
		docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d; \
	else \
		docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d; \
	fi
	@echo "Services started! Access the app at http://localhost"

down: ## Stop all services
	@echo "Stopping $(ENV) environment..."
	@if [ "$(ENV)" = "prod" ]; then \
		docker-compose -f docker-compose.yml -f docker-compose.prod.yml down; \
	else \
		docker-compose -f docker-compose.yml -f docker-compose.dev.yml down; \
	fi

logs: ## View logs (use SERVICE=web/nginx/redis to filter)
	@if [ "$(ENV)" = "prod" ]; then \
		docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f $(SERVICE); \
	else \
		docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f $(SERVICE); \
	fi

shell: ## Open shell in web container
	@docker exec -it flask_app_$(ENV) /bin/bash

db-shell: ## Open PostgreSQL shell (dev only)
	@docker exec -it flask_db_dev psql -U postgres -d flask_website_generator_dev

redis-cli: ## Open Redis CLI
	@docker exec -it flask_redis redis-cli

test: ## Run tests in container
	@docker exec flask_app_$(ENV) pytest

migrate: ## Run database migrations
	@docker exec flask_app_$(ENV) flask db upgrade

clean: ## Clean up containers, volumes, and images
	@echo "Cleaning up Docker resources..."
	@docker-compose -f docker-compose.yml -f docker-compose.dev.yml down -v --remove-orphans
	@docker-compose -f docker-compose.yml -f docker-compose.prod.yml down -v --remove-orphans
	@docker system prune -f

dev: ## Quick start development environment
	@$(MAKE) ENV=dev build
	@$(MAKE) ENV=dev up
	@echo "Development environment is running!"
	@echo "- App: http://localhost"
	@echo "- Mailhog: http://localhost:8025"
	@echo "- Adminer: http://localhost:8080"

prod: ## Quick start production environment
	@$(MAKE) ENV=prod build
	@$(MAKE) ENV=prod up
	@echo "Production environment is running!"
	@echo "- App: http://localhost"
	@echo "- Monitoring: http://localhost:3000 (Grafana)"

restart: ## Restart a service (use SERVICE=web/nginx/redis)
	@if [ -z "$(SERVICE)" ]; then \
		echo "Please specify SERVICE=web/nginx/redis"; \
	else \
		docker-compose restart $(SERVICE); \
	fi

status: ## Show status of all services
	@docker-compose ps

exec: ## Execute command in container (use SERVICE and CMD)
	@if [ -z "$(SERVICE)" ] || [ -z "$(CMD)" ]; then \
		echo "Usage: make exec SERVICE=web CMD='flask routes'"; \
	else \
		docker-compose exec $(SERVICE) $(CMD); \
	fi