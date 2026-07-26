import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from qa.game_driver.compare_runs import compare_runs
from qa.game_driver.session import finalize_run, new_run_dir, write_json


class CompareRunTests(unittest.TestCase):
    def test_identical_runs_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = new_run_dir(root, "one")
            second = new_run_dir(root, "two")
            for run in (first, second):
                snapshot = run / "snapshots" / "final.json"
                write_json(snapshot, {"state": "playground", "visible_entities": [], "camera": {}})
                finalize_run(run, {"status": "passed", "error_count": 0, "snapshot": str(snapshot)})
            with patch("qa.game_driver.compare_runs.LOG_ROOT", root), patch("qa.game_driver.logs.LOG_ROOT", root):
                self.assertEqual(compare_runs("one", "two")["status"], "pass")

    def test_position_difference_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for run_id, x in (("one", 10), ("two", 20)):
                run = new_run_dir(root, run_id)
                snapshot = run / "snapshots" / "final.json"
                write_json(snapshot, {"state": "playground", "visible_entities": [{"id": "duck", "world": {"x": x}}], "camera": {}})
                finalize_run(run, {"status": "passed", "error_count": 0, "snapshot": str(snapshot)})
            with patch("qa.game_driver.compare_runs.LOG_ROOT", root), patch("qa.game_driver.logs.LOG_ROOT", root):
                result = compare_runs("one", "two")
            self.assertEqual(result["status"], "fail")
            self.assertEqual(result["differences"][0]["field"], "visible_entities")
