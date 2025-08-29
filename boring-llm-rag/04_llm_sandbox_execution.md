# LLM Sandbox Execution (Docker, Jupyter)

This build adds a **sandboxed execution environment** for the LLM, allowing it to safely run Python scripts and shell commands inside a Docker container.

- **Docker Container Sandbox**: Isolates code execution from the host OS.
- **Mounted Workspace**: A shared `/workspace` folder allows the LLM to read and write files.
- **Jupyter Integration**: The `ChatMD` class is extended to recognize `python` and `sh` code blocks, execute them, and stream the output back.

> Prereqs: Infrastructure from `01_infrastructure_setup.md` is up and running.

---

## 1) Sandbox Service

The sandbox is a Docker container defined in `compose/docker-compose.yml` and built from `compose/sandbox/Dockerfile`.

- **Image**: A Python image whose packages are defined in `compose/sandbox/requirements.txt`.
- **Volume**: The local `./workspace` directory is mounted to `/workspace` inside the container.

Start it with the other services:
```bash
make start
```

---

## 2) Customizing the Sandbox Environment

You can add Python packages to the sandbox by editing the `compose/sandbox/requirements.txt` file.

After adding a new package (e.g., `matplotlib`), you must rebuild the sandbox image for the changes to take effect. Run the following command:

```bash
make rebuild-sandbox
```

The new package will then be available for import in Python code blocks executed by the LLM.

---

## 3) Jupyter Usage

The `ChatMD` helper can be instantiated with an `execute=True` flag. When its `ask()` method is called, it inspects the prompt for fenced code blocks.

- ```python ... ``` blocks are saved to a temp file in `./workspace` and run with `python` inside the container.
- ```sh ... ``` blocks are executed directly as shell commands within the container's `/workspace` directory.

The `stdout` and `stderr` are captured and rendered back into the Markdown chat.

---

## 4) Example Notebook Workflow

```python
from scripts.jupyter_chat_md import ChatMD

# The `execute=True` flag enables the sandbox feature.
sess = ChatMD(model="qwen3:14b", execute=True)

# Example 1: Create and query a database
sess.ask("""
Create a sqlite database named 'inventory.db' with a 'products' table,
insert some data, and then query it to show products with a quantity less than 20.

```sh
sqlite-utils insert workspace/inventory.db products --csv - <<EOF
id,name,quantity
1,gadget,15
2,widget,25
3,sprocket,10
EOF

sqlite-utils workspace/inventory.db "select * from products where quantity < 20"
```
""")

# Example 2: Python script using pandas
sess.ask("""
Now use Python and Pandas to read the 'products' table from 'inventory.db'
and calculate the total quantity of all items.

```python
import sqlite3
import pandas as pd

con = sqlite3.connect("workspace/inventory.db")
df = pd.read_sql_query("SELECT * from products", con)
con.close()

total_quantity = df['quantity'].sum()
print(f"DataFrame:\n{df}")
print(f"\nTotal quantity: {total_quantity}")
```
""")
```
