"""One command for the website and the API. Windows, Mac, and Linux.

    python run.py          open http://localhost:8000
    python run.py setup    install packages and build the website
    python run.py dev      API plus hot reload while editing the website
"""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")


def venv_python() -> Path:
    if os.name == "nt":
        return ROOT / ".venv" / "Scripts" / "python.exe"
    return ROOT / ".venv" / "bin" / "python"


def npm() -> str:
    return "npm.cmd" if os.name == "nt" else "npm"


def require_node() -> None:
    if shutil.which("node") is None or shutil.which(npm()) is None:
        raise SystemExit("Node.js is required. Install it from https://nodejs.org and run this again.")


def ensure_env_file() -> None:
    env_file = ROOT / ".env"
    example = ROOT / ".env.example"
    if env_file.exists() or not example.exists():
        return
    env_file.write_text(example.read_text(encoding="utf-8"), encoding="utf-8")
    print("Created .env from .env.example. Add your OPENAI_API_KEY.")


def setup() -> None:
    require_node()
    py = venv_python()
    if not py.exists():
        print("Creating .venv ...")
        subprocess.check_call([sys.executable, "-m", "venv", str(ROOT / ".venv")])
    subprocess.check_call([str(py), "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.check_call([str(py), "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")])
    subprocess.check_call([npm(), "install"], cwd=WEB)
    subprocess.check_call([npm(), "run", "build"], cwd=WEB)
    ensure_env_file()
    print("Setup complete. Next: python run.py")


def _open_when_ready(port: int, url: str) -> None:
    for _ in range(80):
        with socket.socket() as sock:
            sock.settimeout(0.4)
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                webbrowser.open(url)
                return
        time.sleep(0.5)


def _pump(proc: subprocess.Popen, name: str) -> None:
    if proc.stdout is None:
        return
    for line in proc.stdout:
        print(f"[{name}] {line}", end="")


def _stop(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    if os.name == "nt":
        subprocess.call(["taskkill", "/F", "/T", "/PID", str(proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        proc.terminate()


def start() -> int:
    if not venv_python().exists() or not (WEB / "dist" / "index.html").exists():
        setup()
    print("Opening http://localhost:8000")
    threading.Thread(target=_open_when_ready, args=(8000, "http://localhost:8000"), daemon=True).start()
    return subprocess.call(
        [str(venv_python()), "-m", "uvicorn", "backend.app:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=ROOT,
    )


def dev() -> int:
    if not venv_python().exists() or not (WEB / "node_modules").exists():
        setup()
    api = subprocess.Popen(
        [str(venv_python()), "-m", "uvicorn", "backend.app:app", "--host", "127.0.0.1", "--port", "8000", "--reload"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    web = subprocess.Popen(
        [npm(), "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173"],
        cwd=WEB,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    threading.Thread(target=_pump, args=(api, "api"), daemon=True).start()
    threading.Thread(target=_pump, args=(web, "web"), daemon=True).start()
    threading.Thread(target=_open_when_ready, args=(5173, "http://localhost:5173"), daemon=True).start()
    print("API http://localhost:8000    website http://localhost:5173")
    print("Press Ctrl+C to stop both.")
    try:
        while api.poll() is None and web.poll() is None:
            time.sleep(0.4)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        _stop(web)
        _stop(api)
    return 0


def main() -> int:
    command = sys.argv[1] if len(sys.argv) > 1 else "start"
    if command == "setup":
        setup()
        return 0
    if command == "dev":
        return dev()
    if command in {"start", "run"}:
        return start()
    print(__doc__)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
