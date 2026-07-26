import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from .love_runtime import LoveRuntimeError, find_love_executable


class LoveRuntimeTests(unittest.TestCase):
    def test_environment_override_accepts_path_with_spaces(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / "Love Runtime" / "love"
            executable.parent.mkdir()
            executable.touch()
            with patch.dict(os.environ, {"LOVE_EXECUTABLE": str(executable)}, clear=False):
                self.assertEqual(find_love_executable(), str(executable))

    @patch.dict(os.environ, {}, clear=True)
    @patch("qa.game_checks.love_runtime.shutil.which")
    def test_lovec_is_preferred_on_path(self, which) -> None:
        which.side_effect = lambda name: "/usr/bin/lovec" if name == "lovec" else None
        self.assertEqual(find_love_executable(), "/usr/bin/lovec")

    @patch.dict(os.environ, {}, clear=True)
    @patch("qa.game_checks.love_runtime.shutil.which")
    def test_love_is_fallback_when_lovec_is_missing(self, which) -> None:
        which.side_effect = lambda name: "/usr/bin/love" if name == "love" else None
        self.assertEqual(find_love_executable(), "/usr/bin/love")

    @patch.dict(os.environ, {}, clear=True)
    @patch("qa.game_checks.love_runtime.shutil.which", return_value=None)
    @patch("qa.game_checks.love_runtime.WINDOWS_CANDIDATES", ())
    def test_missing_runtime_has_actionable_error(self, _which) -> None:
        with self.assertRaisesRegex(LoveRuntimeError, "LOVE_EXECUTABLE"):
            find_love_executable()
