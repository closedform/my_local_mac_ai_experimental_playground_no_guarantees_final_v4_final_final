    from __future__ import annotations
    import os, json, uuid, pathlib, re
    from typing import List, Dict
    from dataclasses import dataclass, field
    import ollama
    import weaviate
    from weaviate.classes.config import Configure
    from hivemind.resources import lab

    try:
        from IPython.display import display, Markdown
        _HAS_IPY = True
    except Exception:
        _HAS_IPY = False

    @dataclass
    class Drone:
        name: str
        model: str
        persona: str = "You are a helpful assistant."
        options: Dict = field(default_factory=dict)

    class HiveMind:
        def __init__(self, execute: bool = False, mode: str = "moderated"):
            self.id = str(uuid.uuid4())
            self.drones: Dict[str, Drone] = {}
            self.history: List[Dict[str, str]] = []
            self.execute = execute
            self.mode = mode
            self.workspace_dir = "the_wormhole"
            self.weaviate_collection = "TheBrain"
            pathlib.Path(self.workspace_dir).mkdir(exist_ok=True)
            self._weaviate_client = None

        def _get_weaviate_client(self):
            if self._weaviate_client is None:
                try:
                    self._weaviate_client = weaviate.connect_to_local(grpc_port=50051, http_host="localhost", http_port=8080)
                except Exception as e:
                    raise ConnectionError("Failed to connect to Weaviate. Is it running? (`make awaken_hive`)") from e
            return self._weaviate_client

        def add_drone(self, name: str, model: str, persona: str, options: Dict = {}):
            if name in self.drones:
                raise ValueError(f"Drone with name '{name}' already exists in the swarm.")
            if "Host" in name or "Brain" in name:
                raise ValueError("Drone name 'Host' or 'Brain' is reserved.")
            self.drones[name] = Drone(name=name, model=model, persona=persona, options=options)

        def list_drones(self):
            if not self.drones:
                print("No Drones in this swarm.")
                return
            print("Drones in the Swarm:")
            for name, d in self.drones.items():
                print(f"- {name} (Model: {d.model})")

        def _execute_code_blocks(self, prompt: str) -> str:
            fenced_block_pattern = re.compile(r"```(python|sh)\n(.*?)```", re.DOTALL)
            matches = list(fenced_block_pattern.finditer(prompt))
            if not matches:
                return ""
            results = []
            for match in matches:
                lang, code = match.groups()
                header = f"--- EXECUTING {lang.upper()} ---"
                try:
                    if lang == "python":
                        fname = f"script_{uuid.uuid4().hex[:8]}.py"
                        fpath = os.path.join(self.workspace_dir, fname)
                        with open(fpath, "w") as f:
                            f.write(code.strip())
                        exit_code, out = lab.run_python_script_in_sandbox(fpath)
                        os.remove(fpath)
                    else:
                        exit_code, out = lab.run_in_sandbox(code.strip())
                    body = f"EXIT CODE: {exit_code}\n\nOUTPUT:\n{out}"
                except Exception as e:
                    body = f"EXECUTION FAILED:\n{e}"
                results.append(f"{header}\n{body}\n--- END ---")
            return "\n\n" + "\n".join(results)

        def to_markdown(self) -> str:
            lines = [f"# HiveMind Session\n"]
            for msg in self.history:
                name, content = msg["name"], msg["content"].rstrip()
                if name == "Host":
                    lines.append(f"**Host:**\n\n{content}\n")
                else:
                    lines.append(f"**{name}:**\n\n{content}\n")
            return "\n".join(lines).strip() + "\n"

        def _display_markdown(self, md_text: str, display_handle=None):
            if not _HAS_IPY:
                print(md_text)
                return None
            if display_handle is None:
                return display(Markdown(md_text), display_id=True)
            display_handle.update(Markdown(md_text))
            return display_handle

        def save_json(self, path: str):
            data = {
                "id": self.id,
                "drones": {name: d.__dict__ for name, d in self.drones.items()},
                "history": self.history,
                "mode": self.mode,
                "execute": self.execute
            }
            pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as f:
                json.dump(data, f, indent=2)

        @classmethod
        def load_json(cls, path: str) -> "HiveMind":
            data = json.load(open(path))
            hive = cls(execute=data.get("execute", False), mode=data.get("mode", "moderated"))
            hive.id = data.get("id", str(uuid.uuid4()))
            hive.history = data.get("history", [])
            drones_data = data.get("drones", {})
            for name, d_data in drones_data.items():
                hive.drones[name] = Drone(**d_data)
            return hive

        def ask(self, prompt: str, stream: bool = True):
            target_match = re.search(r"@(\w+)", prompt)
            if not target_match:
                print("Host, please direct your message to a Drone using '@name'.")
                return
            target_name = target_match.group(1)
            if target_name not in self.drones:
                print(f"Drone '{target_name}' not found in the swarm.")
                return
            target_drone = self.drones[target_name]
            exec_out = self._execute_code_blocks(prompt) if self.execute else ""
            full_prompt = prompt + exec_out if exec_out else prompt
            self.history.append({"name": "Host", "content": full_prompt})
            messages = [{"role": "system", "content": target_drone.persona}]
            for msg in self.history:
                content_with_speaker = f"[{msg['name']}]: {msg['content']}"
                if msg['name'] == 'Host' or msg['name'] != target_name:
                    messages.append({"role": "user", "content": content_with_speaker})
                else:
                    messages.append({"role": "assistant", "content": msg['content']})
            self._stream_and_display(target_name, target_drone.model, messages, stream, target_drone.options)

        def brainscan(self, drone_name: str, query: str, top_k: int = 5, stream: bool = True):
            if drone_name not in self.drones:
                print(f"Drone '{drone_name}' not found in the swarm.")
                return
            target_drone = self.drones[drone_name]
            client = self._get_weaviate_client()
            try:
                docs = client.collections.get(self.weaviate_collection)
                hits = docs.query.near_text(query=query, limit=top_k).objects
                context = "\n\n---\n\n".join([h.properties.get("text", "") for h in hits])
            except Exception as e:
                print(f"Error querying TheBrain: {e}. Did you run `make ingest`?")
                return

            host_prompt = f"Host: Using the following knowledge from TheBrain, answer this query: "{query}""
            self.history.append({"name": "Host", "content": host_prompt})
            self.history.append({"name": "TheBrain", "content": f"CONTEXT:\n{context}"})

            messages = [
                {"role": "system", "content": target_drone.persona},
                {"role": "user", "content": f"Using the following knowledge from TheBrain, answer this query: "{query}"

CONTEXT:
{context}"}
            ]
            self._stream_and_display(drone_name, target_drone.model, messages, stream, target_drone.options)

        def _stream_and_display(self, name: str, model: str, messages: List, stream: bool, options: Dict):
            handle = self._display_markdown(self.to_markdown())
            full_reply = ""
            if stream:
                stream_buffer = ollama.chat(model=model, messages=messages, stream=True, options=options)
                for part in stream_buffer:
                    delta = part.get("message", {}).get("content", "")
                    full_reply += delta
                    if _HAS_IPY:
                        temp_md = self.to_markdown() + f"**{name}:**\n\n{full_reply + ' ▌'}\n"
                        self._display_markdown(temp_md, display_handle=handle)
            else:
                res = ollama.chat(model=model, messages=messages, options=options)
                full_reply = res["message"]["content"]
            self.history.append({"name": name, "content": full_reply})
            self._display_markdown(self.to_markdown(), display_handle=handle)
