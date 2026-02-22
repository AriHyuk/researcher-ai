# ai-researcher // Makefile for Portfolio Excellence

.PHONY: up down restart build logs ps clean help

# Variabel
COMPOSE = docker-compose

help: ## Tampilkan list perintah yang tersedia
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## Jalankan semua container (api & web)
	$(COMPOSE) up -d

deploy: ## Deploy backend ke Google Cloud Run
	bash scripts/deploy.sh

deploy-fe: ## Deploy frontend ke Firebase Hosting
	cd frontend && pnpm build
	pnpm dlx firebase-tools deploy --only hosting --project portofolio-487515 --only hosting:ai-researcher-app

down: ## Hentikan semua container
	$(COMPOSE) down

restart: down up ## Restart semua layanan

build: ## Build ulang image docker
	$(COMPOSE) build

logs: ## Lihat log real-time dari semua container
	$(COMPOSE) logs -f

ps: ## Cek status container yang sedang berjalan
	$(COMPOSE) ps

clean: ## Hentikan container dan hapus volume serta image yatim
	$(COMPOSE) down -v --rmi all --remove-orphans

backend-dev: ## Jalankan backend secara manual (local venv)
	cd backend && python -m uvicorn app.main:app --reload --port 8080

frontend-dev: ## Jalankan frontend secara manual (local pnpm)
	cd frontend && pnpm dev
