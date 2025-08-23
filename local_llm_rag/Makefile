SHELL := /bin/bash

start:
	docker compose -f compose/docker-compose.weaviate.yml up -d
	@echo "Weaviate up at http://localhost:8080"

stop:
	docker compose -f compose/docker-compose.weaviate.yml down

pull-models:
	ollama pull qwen3:14b && \
	ollama pull phi4:reasoning-14b || true && \
	ollama pull deepseek-r1:14b || true && \
	ollama pull llama3.1:8b-instruct && \
	ollama pull bge-m3 || ollama pull nomic-embed-text

ingest:
	INGEST_DIR?=.
	WEAVIATE_HOST=http://localhost:8080 \
	OLLAMA_ENDPOINT=http://localhost:11434 \
	WEAVIATE_COLLECTION=Docs \
	EMBED_MODEL=bge-m3 \
	SUMMARY_MODEL=qwen3:14b \
	uv run scripts/ingest.py

ask:
	QUERY?="Summarize this corpus and propose a folder/tags organization."
	WEAVIATE_HOST=http://localhost:8080 \
	WEAVIATE_COLLECTION=Docs \
	GEN_MODEL=qwen3:14b \
	uv run scripts/rag_query.py $(QUERY)

jlab:
	uv run jupyter lab
