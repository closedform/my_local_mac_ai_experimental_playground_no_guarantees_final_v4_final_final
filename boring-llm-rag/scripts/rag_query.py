import os, sys, textwrap, weaviate, ollama

WEAVIATE_HOST = os.environ.get("WEAVIATE_HOST","http://localhost:8080")
COLLECTION = os.environ.get("WEAVIATE_COLLECTION","Docs")
GEN_MODEL = os.environ.get("GEN_MODEL","qwen3:14b")
TOPK = int(os.environ.get("TOPK","8"))

def main():
    q = sys.argv[1] if len(sys.argv)>1 else "Summarize this corpus and propose a clean folder/tags organization."

    client = weaviate.connect_to_local(grpc_port=50051, http_host="localhost", http_port=8080)
    try:
        docs = client.collections.get(COLLECTION)
        hits = docs.query.near_text(query=q, limit=TOPK).objects
        context = "\n\n---\n\n".join([h.properties["text"] for h in hits])

        prompt = f\"\"\"You are an assistant helping to organize a local drive.
Use the context to answer the user query. If asked, propose a folder tree, dedup/merge plan,
and tagging scheme. If asked to dedup, list exact dup groups and near-dup candidates.

# Query
{q}

# Context (top-{TOPK} chunks)
{context}
\"\"\"

        resp = ollama.chat(model=GEN_MODEL, messages=[{"role":"user","content":prompt}], options={"temperature":0.2})
        print(textwrap.fill(resp["message"]["content"], width=100))

    finally:
        client.close()

if __name__ == "__main__":
    main()
