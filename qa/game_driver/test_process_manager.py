import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from qa.game_driver.process_manager import build_launch, start_session, status


class FakeProcess:
    pid = 4242

    def __init__(self, *args, **kwargs):
        pass


class ProcessManagerTests(unittest.TestCase):
    def test_build_launch(self):
        command = build_launch("love", Path("C:/project"), Path("C:/run"), "duck_slime_date")
        self.assertEqual(command, ["love", ".", "--qa", "--qa-run-dir", str(Path("C:/run")), "--cutscene", "duck_slime_date"])

    def test_start_writes_process_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            logs = root / "logs"
            with patch("qa.game_driver.process_manager.find_love_executable", return_value="love"), \
                 patch("qa.game_driver.process_manager._love_version", return_value="LOVE 11.5"), \
                 patch("qa.game_driver.process_manager._git_commit", return_value="abc123"), \
                 patch("qa.game_driver.process_manager.is_process_alive", return_value=False):
                result = start_session(root=root, log_root=logs, run_id="run-1", popen=FakeProcess)
            self.assertEqual(result["pid"], 4242)
            self.assertEqual((logs / "run-1" / "process.json").exists(), True)
            self.assertEqual(status(log_root=logs)["status"], "stale")
