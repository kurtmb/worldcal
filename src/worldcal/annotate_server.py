from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from worldcal.packet import ROOT
from worldcal.queue import append_annotation, build_queue

STATIC_DIR = Path(__file__).resolve().parent / "annotate_static"


class AnnotateHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        print(f"[annotate] {self.address_string()} {fmt % args}")

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            html = (STATIC_DIR / "index.html").read_bytes()
            self._send(200, html, "text/html; charset=utf-8")
            return
        if path == "/api/queue":
            queue = build_queue()
            payload = {
                "count": len(queue),
                "unlabeled": sum(1 for item in queue if not item["public"]["labeled"]),
                "items": [item["public"] for item in queue],
            }
            self._send(200, json.dumps(payload).encode("utf-8"), "application/json")
            return
        self._send(404, b"not found", "text/plain")

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/api/label":
            self._send(404, b"not found", "text/plain")
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
            row = append_annotation(payload)
        except Exception as exc:
            self._send(400, json.dumps({"error": str(exc)}).encode("utf-8"), "application/json")
            return
        self._send(200, json.dumps({"ok": True, "saved": row}).encode("utf-8"), "application/json")


def serve(host: str = "127.0.0.1", port: int = 8765) -> None:
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((host, port), AnnotateHandler)
    print(f"WorldCal annotator: http://{host}:{port}")
    print(f"Labels append to {ROOT / 'data' / 'annotations' / 'human.jsonl'}")
    print("Model names are hidden. Stories stay on this machine.")
    server.serve_forever()


def main() -> None:
    serve()


if __name__ == "__main__":
    main()
