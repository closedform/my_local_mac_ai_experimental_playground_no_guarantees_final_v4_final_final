# RAG Indexing Service (Recursive Discovery, Smart Chunking, Summaries, Metadata, Dedup)

This build adds:
- **Recursive** folder discovery
- **Smart parsing & chunking** (PDFs, code, docs)
- **Notebook ingestion** (`.ipynb`) and **Mathematica** (`.nb`) export
- **Per-file summaries & metadata** (local model)
- **Exact dedup** by SHA-256; near-dup ready
- **Weaviate** storage with **local embeddings** via Ollama

> Prereqs: infra from `01_infrastructure_setup.md` is up (Ollama + Weaviate + venv).

---

## 1) Helpers for notebooks / Mathematica

`scripts/utils_ipynb_nb.py` handles:
- extracting Markdown + code from `.ipynb`
- exporting Mathematica `.nb` to Markdown via `wolframscript` (if available), else metadata-only

---

## 2) Ingest script

`scripts/ingest.py`:
- Recursively discovers files under `INGEST_DIR`
- Parses & **chunk_by_title** chunks (Unstructured) for PDFs/Office/code
- Handles `.ipynb` (via `nbformat`) and `.nb` (via `wolframscript` export)
- Writes **summaries/metadata** with your local model (Ollama)
- Stores objects in Weaviate with **Ollama embeddings**
- Skips **exact duplicates** by SHA-256 (adds a pointer entry)

Run:

```bash
export INGEST_DIR="/path/to/folder"
export WEAVIATE_HOST="http://localhost:8080"
export OLLAMA_ENDPOINT="http://localhost:11434"
export WEAVIATE_COLLECTION="Docs"
export EMBED_MODEL="bge-m3"
export SUMMARY_MODEL="qwen3:14b"

python scripts/ingest.py
```

---

## 3) RAG querying

`scripts/rag_query.py` performs a semantic search in Weaviate and composes an answer with your chosen local model.

Examples:

```bash
python scripts/rag_query.py "List near-duplicate README sections and propose a merge"
python scripts/rag_query.py "Create an index of notebooks and summarize each"
```

You can set:
- `WEAVIATE_HOST` (default `http://localhost:8080`)
- `WEAVIATE_COLLECTION` (default `Docs`)
- `GEN_MODEL` (default `qwen3:14b`)
- `TOPK` (default `8`)

---

## 4) Near-duplicate flow (optional)

- For each chunk, query top-N neighbors and group by cosine similarity threshold (e.g., ≥ 0.92).
- Feed cluster exemplars to the LLM (via `rag_query.py`) to propose a **merge plan** (keep newest, collapse duplicates, apply tags).

---

## 5) Notes

- Unsupported/binary files get **metadata stubs** so they remain discoverable and can be included in folder overviews.
- Adjust Unstructured `chunk_by_title` parameters for larger or smaller chunks.
