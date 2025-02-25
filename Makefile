# Variables
DOCKER_COMPOSE = docker compose
API_SERVICE = api

# Default target
all: help

# Help: Display available commands
help:
	@echo "Available commands:"
	@echo "  make start       - Start the Docker containers in detached mode"
	@echo "  make stop     - Stop and remove the Docker containers"
	@echo "  make build    - Build the Docker images"
	@echo "  make logs     - View logs from the Flask app container"
	@echo "  make shell    - Open a shell in the Flask app container"
	@echo "  make clean    - Stop containers and remove all unused resources"

# Start the Docker containers in detached mode
start:
	$(DOCKER_COMPOSE) up -d

# Stop and remove the Docker containers
stop:
	$(DOCKER_COMPOSE) down

# Build/Rebuild the api Docker image
build:
	$(DOCKER_COMPOSE) build $(API_SERVICE)

# View logs from the api service
logs:
	$(DOCKER_COMPOSE) logs $(API_SERVICE)

# Open a shell in the api container
shell:
	$(DOCKER_COMPOSE) exec -it $(API_SERVICE) bash

# Stop containers and remove all unused resources
clean:
	$(DOCKER_COMPOSE) down --volumes --remove-orphans

.PHONY: all help start stop build logs shell clean test