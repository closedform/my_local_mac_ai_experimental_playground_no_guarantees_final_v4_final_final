## 1) The helper

`scripts/jupyter_chat_md.py` implements `ChatMD`, a small class that manages messages, streaming, Markdown rendering, save/load, and optional Weaviate logging.

---

## 2) Use it in a notebook

```python
from scripts.jupyter_chat_md import ChatMD

# Choose a local model (ensure you've pulled it via `ollama pull`)
sess = ChatMD(model="qwen3:14b", temperature=0.2, top_p=0.9, num_ctx=16384)

# Ask something (streams + renders the entire transcript as Markdown)
sess.ask("Summarize the key projects in this repository and list action items.", stream=True)

# Subsequent turns
sess.ask("Drill down on the 'data-pipeline' folder and propose refactors.", stream=True)
```

---

## 3) Save / Load / Export

```python
# Save
sess.save_json("chats/session.json")
sess.save_markdown("chats/session.md")

# Load
from scripts.jupyter_chat_md import ChatMD
sess2 = ChatMD.load_json("chats/session.json")
sess2.ask("Continue from where we left off: produce a prioritized task list.", stream=True)
```
