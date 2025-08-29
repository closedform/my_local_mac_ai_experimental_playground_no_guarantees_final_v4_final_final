import docker
import os
from typing import Tuple

SANDBOX_CONTAINER_NAME = "llm-sandbox"
WORKSPACE_DIR = "/workspace"

def get_sandbox_container():
    try:
        client = docker.from_env()
        containers = client.containers.list(filters={"name": SANDBOX_CONTAINER_NAME})
        if not containers:
            raise RuntimeError(f"Sandbox container '{SANDBOX_CONTAINER_NAME}' not found. Is it running?")
        return containers[0]
    except docker.errors.DockerException as e:
        raise RuntimeError("Docker daemon not running or accessible. Please start Docker.") from e

def run_in_sandbox(command: str, workdir: str = WORKSPACE_DIR) -> Tuple[int, str]:
    container = get_sandbox_container()
    exit_code, output = container.exec_run(command, workdir=workdir, demux=True)
    if isinstance(output, tuple):
        stdout, stderr = output
        out = (stdout or b'').decode('utf-8', errors='ignore')
        err = (stderr or b'').decode('utf-8', errors='ignore')
        combined = (out + err).strip()
    else:
        combined = (output or b'').decode('utf-8', errors='ignore').strip()
    return exit_code, combined

def run_python_script_in_sandbox(script_path: str) -> Tuple[int, str]:
    if not os.path.exists(script_path):
        return 1, f"Error: Script file not found at '{script_path}'"
    script_filename = os.path.basename(script_path)
    command = f"python {script_filename}"
    return run_in_sandbox(command)
