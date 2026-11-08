"""A local door in front of Ollama.

Listens on 127.0.0.1 only. Forwards /api/chat after the bearer token matches.
Ollama itself stays on 127.0.0.1:11434.
"""

import os
import sys

import httpx
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TOKEN = os.environ.get("OLLAMA_GATE_TOKEN", "").strip()
UPSTREAM = os.environ.get("OLLAMA_UPSTREAM", "http://127.0.0.1:11434").rstrip("/")
PORT = int(os.environ.get("OLLAMA_GATE_PORT", "11435"))


class Gate(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self):
        self._forward()

    def do_POST(self):
        self._forward()

    def _forward(self):
        if not TOKEN or self.headers.get("Authorization") != f"Bearer {TOKEN}":
            body = b"unauthorized"
            self.send_response(401)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        length = int(self.headers.get("Content-Length") or 0)
        payload = self.rfile.read(length) if length else None
        headers = {}
        if self.headers.get("Content-Type"):
            headers["Content-Type"] = self.headers["Content-Type"]
        try:
            with httpx.stream(
                self.command,
                f"{UPSTREAM}{self.path}",
                content=payload,
                headers=headers,
                timeout=httpx.Timeout(300.0, connect=10.0),
            ) as response:
                self.send_response(response.status_code)
                content_type = response.headers.get("content-type")
                if content_type:
                    self.send_header("Content-Type", content_type)
                self.send_header("Transfer-Encoding", "chunked")
                self.end_headers()
                for chunk in response.iter_bytes():
                    if not chunk:
                        continue
                    self.wfile.write(f"{len(chunk):X}\r\n".encode("ascii") + chunk + b"\r\n")
                self.wfile.write(b"0\r\n\r\n")
        except Exception:
            try:
                self.send_error(502, "model server unavailable")
            except Exception:
                return

    def log_message(self, fmt, *args):
        sys.stderr.write("ollama-gate " + (fmt % args) + "\n")


def main() -> None:
    if not TOKEN:
        raise SystemExit("Set OLLAMA_GATE_TOKEN before starting the gate.")
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Gate)
    print(f"Ollama gate on http://127.0.0.1:{PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
