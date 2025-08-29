# Local LLM Reasoning & RAG on Mac Studio (Aug 2025, **uv**)

**Start here.** This repo contains:
- `01_infrastructure_setup.md` — base stack (Ollama, Weaviate, Makefile, uv project)
- `02_rag_indexing_service.md` — ingestion, summaries/metadata, RAG queries, dedup
- `03_jupyter_markdown_chat.md` — notebook-native markdown chat (save/load, streaming)

**Quick start (uv)**

```bash
# Terminal A
ollama serve

# Terminal B
cd local-llm-rag
uv venv .venv && uv sync
make start
make pull-models
make ingest INGEST_DIR="/path/to/folder"
make ask QUERY="Summarize notebooks and propose folder structure"
make jlab
```
