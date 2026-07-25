"""Static checks for the disposable cutscene engine example."""
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
PYTHON = sys.executable
VALIDATOR = ROOT / "cutscene_engine" / "tools" / "validate_scene.py"


class CutsceneEngineTests(unittest.TestCase):
    def test_start_state_is_registered(self) -> None:
        source = (ROOT / "game" / "states_manager.lua").read_text(encoding="utf-8")
        self.assertIn('start = require("game.game_states.start")', source)
        self.assertIn('StatesManager.change("start", ...)', source)

    def test_example_scene_validates(self) -> None:
        result = subprocess.run(
            [PYTHON, str(VALIDATOR), "duck_slime_intro"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_date_scene_validates(self) -> None:
        result = subprocess.run(
            [PYTHON, str(VALIDATOR), "duck_slime_date"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unknown_scene_fails_validation(self) -> None:
        result = subprocess.run(
            [PYTHON, str(VALIDATOR), "missing_scene"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)

    def test_root_preview_stays_running(self) -> None:
        love = Path(r"C:\Program Files\LOVE\lovec.exe")
        process = subprocess.Popen(
            [str(love), ".", "--cutscene", "duck_slime_intro"],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            self.assertIsNone(process.poll(), "cutscene preview exited during startup")
        finally:
            process.terminate()
            process.wait(timeout=10)


if __name__ == "__main__":
    unittest.main()
