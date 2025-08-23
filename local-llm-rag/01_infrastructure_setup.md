# Local LLM Reasoning & RAG — Infrastructure Setup (Mac Studio M2 Max, Aug 2025, **uv**)

Sets up a **local-only** stack with:
- **Ollama** (Metal-accelerated local LLM runtime)
- **Weaviate** (local vector DB with Ollama integrations)
- **Python project managed by `uv`** (fast lock-free installer/runner)
- Base **folder layout** and **Makefile** (using `uv run`)

Everything runs locally on macOS — no cloud required.

---

## 0) Prerequisites

- macOS (Apple Silicon)
- Homebrew
- Docker Desktop (running)
- `uv` (installer below)

```bash
# Install uv (recommended):
curl -LsSf https://astral.sh/uv/install.sh | sh
# (or) brew install uv
```

```bash
# Essentials
brew install git jq coreutils wget
```

---

## 1) Project layout

```bash
mkdir -p local-llm-rag/{compose,scripts,chats}
cd local-llm-rag
```

```
local-llm-rag/
├─ compose/
│  └─ docker-compose.weaviate.yml
├─ scripts/            # code (ingest, RAG query, chat UI, helpers)
├─ chats/              # saved chat logs (.json/.md)
├─ Makefile
├─ pyproject.toml      # <- uv project file (deps live here)
└─ README.md
```

---

## 2) Python environment via uv

```bash
# Create and use an in-project venv (optional; uv can run without activation)
uv venv .venv
# Install dependencies from pyproject.toml
uv sync
```

You can run everything with `uv run` (no manual activation required).

---

## 3) Ollama (LLM runtime)

```bash
brew install ollama
ollama serve   # leave running in a terminal (or run the app)
```

Pull recommended models (reasoning + embeddings):

```bash
# Reasoning
ollama pull qwen3:14b
ollama pull phi4:reasoning-14b || true
ollama pull deepseek-r1:14b || true

# Generalist fallback
ollama pull llama3.1:8b-instruct

# Embeddings for RAG
ollama pull bge-m3 || ollama pull nomic-embed-text
```

Tip: `ollama list` shows installed models.

---

## 4) Weaviate (local vector DB with Ollama modules)

The compose file is at `compose/docker-compose.weaviate.yml`.

Start it:

```bash
docker compose -f compose/docker-compose.weaviate.yml up -d
```

> Collections will point to your **host** Ollama endpoint from Python (`http://host.docker.internal:11434`).

---

## 5) Makefile (uses uv)

- `start` / `stop` — bring up/down Weaviate
- `pull-models` — pull suggested models
- `ingest` — index a folder (recursive)
- `ask` — run a RAG query against the index
- `jlab` — launch JupyterLab

```bash
# Terminal A
ollama serve

# Terminal B
make start
uv sync
make pull-models
make ingest INGEST_DIR="/path/to/folder"
make ask QUERY="Summarize notebooks and propose folder structure"
make jlab
make stop
```
