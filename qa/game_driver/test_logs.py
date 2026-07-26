import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from qa.game_driver.logs import inspect_run
from qa.game_driver.session import finalize_run, new_run_dir, read_latest, write_json


class StableLogTests(unittest.TestCase):
    def test_run_ids_do_not_collide(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = new_run_dir(root)
            second = new_run_dir(root)
            self.assertNotEqual(first.name, second.name)

    def test_run_id_cannot_escape_log_root(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                new_run_dir(Path(directory), "..\\outside")

    def test_finalize_writes_report_and_latest_pointer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_dir = new_run_dir(root, "run-1")
            write_json(run_dir / "session.json", {"run_id": "run-1", "status": "running"})
            report = finalize_run(run_dir, {"status": "passed", "error_count": 0})
            self.assertEqual(report["schema_version"], 1)
            self.assertEqual(read_latest(root)["run_id"], "run-1")
            with patch("qa.game_driver.logs.LOG_ROOT", root):
                self.assertEqual(inspect_run("run-1")["run_id"], "run-1")

    def test_inspect_counts_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_dir = new_run_dir(root, "run-2")
            (run_dir / "events.jsonl").write_text('{"type":"qa_started"}\n', encoding="utf-8")
            (run_dir / "results.jsonl").write_text('{"ok":true}\n', encoding="utf-8")
            (run_dir / "snapshots" / "one.json").write_text("{}", encoding="utf-8")
            (run_dir / "screenshots" / "one.png").write_bytes(b"png")
            with patch("qa.game_driver.logs.LOG_ROOT", root):
                result = inspect_run("run-2")
            self.assertEqual(result["event_count"], 1)
            self.assertEqual(result["result_count"], 1)
            self.assertEqual(result["snapshots"], 1)
            self.assertEqual(result["screenshots"], 1)
