"""Runs the Lua-level core system checks through the installed Love2D runtime."""

from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[2]
LOVE = Path(r"C:\Program Files\LOVE\lovec.exe")


class CoreSystemRuntimeTests(unittest.TestCase):
    def test_lua_core_system_checks(self) -> None:
        result = subprocess.run(
            [str(LOVE), "qa/love_checks"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
