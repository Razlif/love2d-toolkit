"""Static checks for optional systems that need a real Love user sandbox for full I/O tests."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class OptionalSystemContractTests(unittest.TestCase):
    def test_camera_parallax_audio_ui_and_save_modules_exist(self) -> None:
        required = (
            "game/systems/camera_manager.lua",
            "game/systems/parallax.lua",
            "game/systems/audio_manager.lua",
            "game/systems/json.lua",
            "game/systems/save_manager.lua",
            "game/ui/theme.lua",
            "game/ui/ui_elements/default_button.lua",
            "game/ui/ui_elements/default_menu.lua",
            "game/ui/ui_elements/default_dialogue_box.lua",
        )
        for relative in required:
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_save_manager_exposes_versioned_json_contract(self) -> None:
        text = (ROOT / "game/systems/save_manager.lua").read_text(encoding="utf-8")
        for symbol in ("save", "load", "exists", "delete", "list_slots", "SCHEMA_VERSION"):
            self.assertIn(symbol, text)
        self.assertIn("save_slots", text)
