"""Checks for the first promoted runtime asset set."""

from pathlib import Path
import unittest

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
LAB_DUCK = ROOT / "asset_lab" / "lab_assets" / "characters" / "barbarian_duck_wizard"
RUNTIME_DUCK = ROOT / "media_assets" / "characters" / "barbarian_duck_wizard"
RUNTIME_SLIME = ROOT / "media_assets" / "characters" / "funky_blue_slime"
RUNTIME_EFFECT = ROOT / "media_assets" / "effects" / "magic_explosion"
MANIFEST_LUA = ROOT / "game_data" / "asset_manifest.lua"


class PromotedDuckTests(unittest.TestCase):
    def test_runtime_files_exist_and_match_lab_sources(self) -> None:
        relative_files = (
            "original_images/barbarian_duck_wizard__pixellab__image__v001.png",
            "sprite_sheets/barbarian_duck_wizard__pixellab__jump_from_image_v001__v001.png",
        )
        for relative_file in relative_files:
            lab_file = LAB_DUCK / relative_file
            runtime_file = RUNTIME_DUCK / relative_file
            self.assertTrue(lab_file.is_file(), lab_file)
            self.assertTrue(runtime_file.is_file(), runtime_file)
            self.assertEqual(lab_file.read_bytes(), runtime_file.read_bytes())

    def test_runtime_dimensions_match_game_data(self) -> None:
        image_path = RUNTIME_DUCK / "original_images" / "barbarian_duck_wizard__pixellab__image__v001.png"
        sheet_path = RUNTIME_DUCK / "sprite_sheets" / "barbarian_duck_wizard__pixellab__jump_from_image_v001__v001.png"
        with Image.open(image_path) as image:
            self.assertEqual(image.size, (64, 64))
        with Image.open(sheet_path) as sheet:
            self.assertEqual(sheet.size, (320, 64))


class PromotedPlaygroundExamplesTests(unittest.TestCase):
    def test_slime_and_effect_runtime_files_exist(self) -> None:
        expected = (
            RUNTIME_SLIME / "original_images/funky_blue_slime__pixellab__image__v001.png",
            RUNTIME_SLIME / "sprite_sheets/funky_blue_slime__pixellab__idle_bounce_from_image_v001__v001.png",
            RUNTIME_EFFECT / "original_images/magic_explosion__self__image__v001.png",
            RUNTIME_EFFECT / "sprite_sheets/magic_explosion__self__burst_from_image_v001__v001.png",
        )
        for path in expected:
            self.assertTrue(path.is_file(), path)

        self.assertFalse(any(RUNTIME_EFFECT.rglob("*.gif")))

    def test_generated_manifest_contains_effect_dimensions_and_entries(self) -> None:
        text = MANIFEST_LUA.read_text(encoding="utf-8")
        self.assertIn("funky_blue_slime", text)
        self.assertIn("magic_explosion", text)
        self.assertIn("frame_width = 64", text)
        self.assertIn("frame_height = 64", text)

    def test_controller_and_effect_runtime_modules_exist(self) -> None:
        required = (
            "game/controllers/controller_factory.lua",
            "game/controllers/player_controller.lua",
            "game/controllers/basic_enemy_controller.lua",
            "game/systems/movement_manager.lua",
            "game/entities/characters/character.lua",
            "game/entities/effects/effect.lua",
        )
        for relative in required:
            self.assertTrue((ROOT / relative).is_file(), relative)


if __name__ == "__main__":
    unittest.main()
