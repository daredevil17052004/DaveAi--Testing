"""
Lightweight Mock Server implementing the Reqres API contract.
Used as an offline fallback or deterministic CI mock when live Reqres hits daily rate limits.
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading


class MockReqresHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress standard logging to keep test output clean
        pass

    def _send_json(self, status_code: int, data: dict):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path
        if "/api/users?page=2" in path or path == "/api/users":
            self._send_json(200, {
                "page": 2,
                "per_page": 6,
                "total": 12,
                "total_pages": 2,
                "data": [
                    {
                        "id": 7,
                        "email": "michael.lawson@reqres.in",
                        "first_name": "Michael",
                        "last_name": "Lawson",
                        "avatar": "https://reqres.in/img/faces/7-image.jpg"
                    },
                    {
                        "id": 8,
                        "email": "lindsay.ferguson@reqres.in",
                        "first_name": "Lindsay",
                        "last_name": "Ferguson",
                        "avatar": "https://reqres.in/img/faces/8-image.jpg"
                    }
                ],
                "support": {
                    "url": "https://contentcaddy.io?utm_source=reqres&utm_medium=json&utm_campaign=referral",
                    "text": "Tired of writing mock data?"
                }
            })
        elif path == "/api/users/2":
            self._send_json(200, {
                "data": {
                    "id": 2,
                    "email": "janet.weaver@reqres.in",
                    "first_name": "Janet",
                    "last_name": "Weaver",
                    "avatar": "https://reqres.in/img/faces/2-image.jpg"
                },
                "support": {
                    "url": "https://contentcaddy.io?utm_source=reqres&utm_medium=json&utm_campaign=referral",
                    "text": "Tired of writing mock data?"
                }
            })
        elif path == "/api/users/999":
            self._send_json(404, {})
        else:
            self._send_json(404, {"error": "Not Found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        payload_bytes = self.rfile.read(length) if length > 0 else b"{}"
        try:
            body = json.loads(payload_bytes.decode("utf-8"))
        except Exception:
            body = {}

        if self.path == "/api/users":
            self._send_json(201, {
                "name": body.get("name", "morpheus"),
                "job": body.get("job", "leader"),
                "id": "789",
                "createdAt": "2026-11-20T16:00:00.000Z"
            })
        elif self.path == "/api/register":
            if "password" not in body or not body["password"]:
                self._send_json(400, {"error": "Missing password"})
            else:
                self._send_json(200, {"id": 4, "token": "QpwL5tke4Pnpja7X4"})
        else:
            self._send_json(404, {"error": "Not Found"})


def start_mock_server(host="127.0.0.1", port=8000):
    server = HTTPServer((host, port), MockReqresHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server
