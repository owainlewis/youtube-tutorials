from __future__ import annotations

import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer

from server import DemoHandler


class ServerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), DemoHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.assertFalse(self.thread.is_alive())

    def test_home_returns_plain_text(self) -> None:
        host, port = self.server.server_address

        with urllib.request.urlopen(f"http://{host}:{port}/", timeout=2) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers.get_content_type(), "text/plain")
            self.assertEqual(response.read(), b"Docker sandbox demo\n")


if __name__ == "__main__":
    unittest.main()
