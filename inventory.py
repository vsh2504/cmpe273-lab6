"""Inventory service for CMPE 273 Lab 6.

A small HTTP service with no third party dependencies, so it runs on a
plain python:3.12-slim image. It serves these endpoints:

    GET  /items               current stock, plus the name of the Pod
                              that served the request
    GET  /ready               200 while the Pod is ready, 503 after
                              readiness has been failed on purpose
    POST /fail-readiness      make this Pod report not ready
    POST /restore-readiness   make this Pod report ready again
    GET  /health              simple liveness check, always 200

In Kubernetes, the Pod name is the container hostname, so the /items
response shows exactly which replica handled each request. The readiness
flag lives in memory, so failing readiness on one Pod affects only that
Pod, which is what the Lab 6 readiness demo needs.
"""

import json
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

POD_NAME = socket.gethostname()
PORT = 5000

ITEMS = {
    "laptop": 10,
    "phone": 5,
    "keyboard": 25,
    "headphones": 0,
}

ready = True


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, payload):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f"[inventory:{POD_NAME}] {self.command} {self.path}", flush=True)

    def do_GET(self):
        if self.path == "/items":
            self._send(200, {"pod": POD_NAME, "items": ITEMS})
        elif self.path == "/ready":
            if ready:
                self._send(200, {"pod": POD_NAME, "ready": True})
            else:
                self._send(503, {"pod": POD_NAME, "ready": False})
        elif self.path == "/health":
            self._send(200, {"pod": POD_NAME, "status": "ok"})
        elif self.path == "/":
            self._send(200, {"service": "inventory", "pod": POD_NAME})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        global ready
        if self.path == "/fail-readiness":
            ready = False
            self._send(200, {"pod": POD_NAME, "ready": False})
        elif self.path == "/restore-readiness":
            ready = True
            self._send(200, {"pod": POD_NAME, "ready": True})
        else:
            self._send(404, {"error": "not found"})


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[inventory:{POD_NAME}] Listening on port {PORT}", flush=True)
    server.serve_forever()
