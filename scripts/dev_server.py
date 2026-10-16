"""Run the API and the Vite dev server in one window."""

import os
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")


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


def main() -> int:
    api = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.app:app", "--host", "127.0.0.1", "--port", "8000", "--reload"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    web = subprocess.Popen(
        "npm run dev -- --host 127.0.0.1 --port 5173",
        cwd=WEB,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    threading.Thread(target=_pump, args=(api, "api"), daemon=True).start()
    threading.Thread(target=_pump, args=(web, "web"), daemon=True).start()
    threading.Thread(target=_open_when_ready, args=(5173, "http://localhost:5173"), daemon=True).start()
    print("CardioTwin dev servers starting. API http://localhost:8000  UI http://localhost:5173")
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


if __name__ == "__main__":
    raise SystemExit(main())
