import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from qa.bridge_server import BridgeHTTPServer
from qa.game_driver.session import append_jsonl, new_run_dir, write_json


class BridgeServerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.run_dir = new_run_dir(self.root, "run-1")
        write_json(self.run_dir / "session.json", {"run_id": "run-1", "status": "running"})
        append_jsonl(self.run_dir / "events.jsonl", {"event_id": 1, "type": "qa_started"})
        self.server = BridgeHTTPServer(("127.0.0.1", 0), self.run_dir)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_address[1]}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temp.cleanup()

    def request(self, path, method="GET", value=None, token=None):
        data = json.dumps(value).encode("utf-8") if value is not None else None
        request = Request(self.base + path, data=data, method=method)
        request.add_header("Authorization", f"Bearer {token or self.server.token}")
        if data:
            request.add_header("Content-Type", "application/json")
        return urlopen(request, timeout=2)

    def test_status_and_incremental_events(self):
        status = json.load(self.request("/v1/status"))
        self.assertEqual(status["run_id"], "run-1")
        first = json.load(self.request("/v1/events"))
        self.assertEqual(len(first["records"]), 1)
        second = json.load(self.request(f"/v1/events?after={first['next']}"))
        self.assertEqual(second["records"], [])
        self.assertEqual(second["errors"], [])

    def test_malformed_log_line_is_reported(self):
        append_jsonl(self.run_dir / "events.jsonl", {"event_id": 2, "type": "valid"})
        with (self.run_dir / "events.jsonl").open("a", encoding="utf-8") as handle:
            handle.write("not-json\n")
        payload = json.load(self.request("/v1/events"))
        self.assertEqual(len(payload["records"]), 2)
        self.assertEqual(len(payload["errors"]), 1)

    def test_missing_screenshot_is_explicit(self):
        with self.assertRaises(HTTPError) as error:
            self.request("/v1/screenshots/latest")
        self.assertEqual(error.exception.code, 404)

    def test_command_post_adds_agent_source(self):
        response = json.load(self.request("/v1/commands", "POST", {"id": "a1", "command": "press", "key": "right"}))
        self.assertEqual(response["accepted"], ["a1"])
        line = (self.run_dir / "commands.jsonl").read_text(encoding="utf-8")
        self.assertIn('"source":"agent"', line)

    def test_invalid_token_is_rejected(self):
        with self.assertRaises(HTTPError) as error:
            self.request("/v1/status", token="wrong")
        self.assertEqual(error.exception.code, 401)

    def test_duplicate_command_is_rejected(self):
        append_jsonl(self.run_dir / "commands.jsonl", {"id": "old", "command": "press", "key": "left"})
        with self.assertRaises(HTTPError) as error:
            self.request("/v1/commands", "POST", {"id": "old", "command": "release", "key": "left"})
        self.assertEqual(error.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
