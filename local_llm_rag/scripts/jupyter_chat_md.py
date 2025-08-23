from __future__ import annotations
import os, json, time, uuid, pathlib
from typing import List, Dict, Optional
import ollama

try:
    from IPython.display import display, Markdown
    _HAS_IPY = True
except Exception:
    _HAS_IPY = False

try:
    import weaviate
    _HAS_WV = True
except Exception:
    _HAS_WV = False

def _now_ms() -> int:
    return int(time.time() * 1000)

class ChatMD:
    def __init__(self,
                 model: str = "qwen3:14b",
                 system_prompt: Optional[str] = None,
                 temperature: float = 0.2,
                 top_p: float = 0.9,
                 num_ctx: int = 8192,
                 seed: Optional[int] = None):
        self.model = model
        self.system_prompt = system_prompt or "You are a helpful, concise assistant."
        self.temperature = float(temperature)
        self.top_p = float(top_p)
        self.num_ctx = int(num_ctx)
        self.seed = seed
        self.id = str(uuid.uuid4())
        self.messages: List[Dict[str, str]] = [{"role": "system", "content": self.system_prompt}]

    def save_json(self, path: str) -> str:
        data = {
            "id": self.id,
            "model": self.model,
            "params": {
                "temperature": self.temperature,
                "top_p": self.top_p,
                "num_ctx": self.num_ctx,
                "seed": self.seed
            },
            "messages": self.messages,
            "saved_at": _now_ms()
        }
        pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        return path

    @classmethod
    def load_json(cls, path: str) -> "ChatMD":
        data = json.load(open(path))
        sess = cls(
            model=data.get("model", "qwen3:14b"),
            system_prompt=data.get("messages", [{}])[0].get("content", "You are a helpful assistant."),
            temperature=data.get("params", {}).get("temperature", 0.2),
            top_p=data.get("params", {}).get("top_p", 0.9),
            num_ctx=data.get("params", {}).get("num_ctx", 8192),
            seed=data.get("params", {}).get("seed", None),
        )
        sess.id = data.get("id", str(uuid.uuid4()))
        sess.messages = data.get("messages", sess.messages)
        return sess

    def save_markdown(self, path: str) -> str:
        md = self.to_markdown()
        pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write(md)
        return path

    def to_markdown(self) -> str:
        lines = [f"# Chat — {self.model}\n"]
        for msg in self.messages:
            role = msg["role"]
            content = msg["content"].rstrip()
            if role == "system":
                lines.append(f"> **system**\n>\n> {content}\n")
            elif role == "user":
                lines.append(f"**You:**\n\n{content}\n")
            else:
                lines.append(f"**Assistant:**\n\n{content}\n")
        return "\n".join(lines).strip() + "\n"

    def _display_markdown(self, md_text: str, display_handle=None):
        if not _HAS_IPY:
            print(md_text)
            return display_handle
        if display_handle is None:
            return display(Markdown(md_text), display_id=True)
        else:
            display_handle.update(Markdown(md_text))
            return display_handle

    def _msgs_to_md(self, msgs: List[Dict[str, str]]) -> str:
        lines = [f"# Chat — {self.model}\n"]
        for m in msgs:
            r, c = m["role"], m["content"].rstrip()
            if r == "system": lines += [f"> **system**\n>\n> {c}\n"]
            elif r == "user": lines += [f"**You:**\n\n{c}\n"]
            else: lines += [f"**Assistant:**\n\n{c}\n"]
        return "\n".join(lines)

    def ask(self, prompt: str, stream: bool = True) -> str:
        self.messages.append({"role": "user", "content": prompt})

        opts = {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "num_ctx": self.num_ctx,
        }
        if self.seed is not None:
            opts["seed"] = self.seed

        reply = ""
        if _HAS_IPY:
            tmp_msgs = self.messages + [{"role": "assistant", "content": ""}]
            handle = self._display_markdown(self._msgs_to_md(tmp_msgs))
        else:
            handle = None

        if stream:
            for part in ollama.chat(model=self.model, messages=self.messages, stream=True, options=opts):
                delta = part.get("message", {}).get("content", "")
                reply += delta
                if _HAS_IPY:
                    tmp_msgs[-1]["content"] = reply
                    handle = self._display_markdown(self._msgs_to_md(tmp_msgs), display_handle=handle)
        else:
            res = ollama.chat(model=self.model, messages=self.messages, options=opts)
            reply = res["message"]["content"]

        self.messages.append({"role": "assistant", "content": reply})
        self._display_markdown(self.to_markdown(), display_handle=handle)
        return reply

    def log_to_weaviate(self,
                         collection: str = "Conversations",
                         weaviate_host: str = "http://localhost:8080") -> None:
        if not _HAS_WV:
            raise RuntimeError("weaviate-client not installed")
        client = weaviate.connect_to_local(grpc_port=50051, http_host="localhost", http_port=8080)
        try:
            try:
                coll = client.collections.get(collection)
            except:
                from weaviate.classes.config import Configure
                coll = client.collections.create(
                    name=collection,
                    vectorizer_config=Configure.Vectorizer.text2vec_ollama(
                        api_endpoint="http://localhost:11434", model="bge-m3"
                    ),
                )
            objs = []
            for i, m in enumerate(self.messages):
                if m["role"] == "system": 
                    continue
                objs.append({
                    "chat_id": self.id,
                    "turn": i,
                    "role": m["role"],
                    "content": m["content"],
                    "ts": _now_ms(),
                    "model": self.model,
                })
                if len(objs) >= 200:
                    coll.data.insert_many(objs); objs.clear()
            if objs: coll.data.insert_many(objs)
        finally:
            client.close()
