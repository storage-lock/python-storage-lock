import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
import unittest

from admin_client import AdminClient


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps([{"lock_id": "orders", "owner_id": "reader", "held": True}]).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


class AdminClientTest(unittest.TestCase):
    def test_list_locks(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.shutdown)
        self.addCleanup(server.server_close)
        client = AdminClient(f"http://127.0.0.1:{server.server_port}")
        self.assertIn("orders", client.list_locks())


if __name__ == "__main__":
    unittest.main()
