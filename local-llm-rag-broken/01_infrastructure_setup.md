# Local LLM Reasoning & RAG — Infrastructure Setup

Sets up a local stack with:
- Ollama (local LLM runtime)
- Weaviate (local vector DB for RAG)
- Docker Sandbox (for safe code execution)
- Python project managed by `uv`

---

## 0) Prerequisites

- macOS, Linux, or Windows with WSL2
- Git
- Docker Desktop (for RAG and the execution sandbox)
- `uv`

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## 1) Project Layout

```
local-llm-rag/
├─ compose/
│  └─ ... (Docker configuration)
├─ hivemind/
│  ├─ __init__.py
│  ├─ session.py
│  └─ resources/
│     ├─ __init__.py
│     ├─ lab.py
│     └─ codex.py
├─ tools/
│  ├─ ingest.py
│  └─ brainscan.py
├─ chats/
├─ the_wormhole/
├─ Makefile
├─ pyproject.toml
└─ README.md
```

---

## 2) Python environment via uv

```bash
uv venv .venv
uv sync
```

---

## 3) Ollama

```bash
ollama serve
make pull-models
```

---

## 4) Optional Services: Weaviate & Sandbox

```bash
make awaken_hive
```
