# Conversation Interface — Markdown Chat in Jupyter

A notebook-native chat UI that:
- renders the whole conversation as **Markdown** in Jupyter,
- supports **streaming** responses,
- lets you **tune parameters** (model, temperature, top_p, context),
- **saves/loads** chats (JSON + Markdown),
- optionally **logs** conversations into Weaviate for “conversational RAG.”

> Requires: `ollama`, `ipywidgets`, `jupyterlab` (already in requirements).

---

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

---

## 4) Quick parameter tuning

```python
sess.model = "llama3.1:8b-instruct"  # switch to a faster model
sess.temperature = 0.1
sess.top_p = 0.8
sess.num_ctx = 8192
sess.ask("Rewrite the summary into a crisp executive brief.", stream=False)
```

---

## 5) Optional: simple widget chat box

```python
import ipywidgets as w
from IPython.display import display
from scripts.jupyter_chat_md import ChatMD

models = ["qwen3:14b", "phi4:reasoning-14b", "llama3.1:8b-instruct"]
dd_model = w.Dropdown(options=models, value=models[0], description="Model")
sl_temp  = w.FloatSlider(value=0.2, min=0.0, max=1.0, step=0.05, description="Temp")
sl_top_p = w.FloatSlider(value=0.9, min=0.1, max=1.0, step=0.05, description="top_p")
ta       = w.Textarea(placeholder="Type your message…", rows=4, layout=w.Layout(width="100%"))
btn      = w.Button(description="Send", button_style="primary")
box      = w.VBox([dd_model, w.HBox([sl_temp, sl_top_p]), ta, btn])

sess = ChatMD(model=dd_model.value, temperature=sl_temp.value, top_p=sl_top_p.value)

def on_send(_):
    sess.model = dd_model.value
    sess.temperature = sl_temp.value
    sess.top_p = sl_top_p.value
    if ta.value.strip():
        sess.ask(ta.value.strip(), stream=True)
        ta.value = ""

btn.on_click(on_send)
display(box)
```

---

## 6) Optional: log chats to Weaviate

```python
# Writes (non-system) turns into "Conversations" collection
sess.log_to_weaviate(collection="Conversations", weaviate_host="http://localhost:8080")
```
