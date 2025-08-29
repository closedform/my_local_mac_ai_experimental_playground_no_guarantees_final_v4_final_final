# Local LLM Reasoning & RAG

**Start here.** This repo contains:
- `01_infrastructure_setup.md` — Base stack (Ollama, Docker, Makefile, Python project).
- `02_rag_indexing_service.md` — RAG pipeline for ingesting knowledge into `TheBrain`.
- `03_jupyter_hivemind.md` — A multi-agent Markdown chat interface for AI Drones.
- `04_llm_sandbox_execution.md` — Sandboxed code execution within the HiveMind.

**Quick Start**

1.  **Clone the Repository**
    ```bash
    git clone <your-repo-url>
    cd local-llm-rag
    ```

2.  **Run Ollama**
    ```bash
    ollama serve
    ```

3.  **Set up the Environment & Tools**
    ```bash
    uv venv .venv && uv sync
    make awaken_hive
    make pull-models
    ```

4.  **Ingest Knowledge & Start Jupyter**
    ```bash
    make ingest INGEST_DIR="./"
    make jlab
    ```
