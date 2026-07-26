"""Runs the Lua-level core system checks through the installed Love2D runtime."""

import subprocess
import unittest

from .love_runtime import find_love_executable

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class CoreSystemRuntimeTests(unittest.TestCase):
    def test_lua_core_system_checks(self) -> None:
        result = subprocess.run(
            [find_love_executable(), "qa/love_checks"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
