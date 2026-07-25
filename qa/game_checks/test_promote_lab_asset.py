"""Tests for deterministic Asset Lab promotion operations."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

HELPERS = Path(__file__).resolve().parents[2] / "asset_lab" / "helpers"
sys.path.insert(0, str(HELPERS))

import promote_lab_asset


class PromotionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.lab_root = self.root / "asset_lab" / "lab_assets" / "characters" / "test_hero"
        self.lab_images = self.lab_root / "original_images"
        self.lab_sheets = self.lab_root / "sprite_sheets"
        self.lab_images.mkdir(parents=True)
        self.lab_sheets.mkdir(parents=True)
        self.write_png(self.lab_images / "test_hero__mock__image__v001.png", (8, 8))
        self.write_png(self.lab_sheets / "test_hero__mock__jump__v001.png", (16, 8))
        self.write_manifest(image_version=1, animation_version=1)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    @staticmethod
    def write_png(path: Path, size: tuple[int, int]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGBA", size, (255, 0, 0, 255)).save(path)

    def write_manifest(self, *, image_version: int, animation_version: int) -> None:
        image_name = f"test_hero__mock__image__v{image_version:03d}.png"
        sheet_name = f"test_hero__mock__jump__v{animation_version:03d}.png"
        data = {
            "version": 1,
            "assets": [{
                "id": "test_hero",
                "type": "character",
                "folder": "lab_assets/characters/test_hero",
                "images": [{
                    "version": image_version,
                    "path": f"lab_assets/characters/test_hero/original_images/{image_name}",
                    "provider": "mock",
                    "width": 8,
                    "height": 8,
                    "prompt": "test hero",
                }],
                "animations": [{
                    "name": "jump",
                    "version": animation_version,
                    "sheet_path": f"lab_assets/characters/test_hero/sprite_sheets/{sheet_name}",
                    "gif_path": "lab_assets/characters/test_hero/animation_gifs/not-promoted.gif",
                    "source_image_version": image_version,
                    "frame_width": 8,
                    "frame_height": 8,
                    "frame_count": 2,
                    "fps": 8,
                    "provider": "mock",
                    "prompt": "jump",
                }],
            }],
        }
        manifest_path = self.root / "asset_lab" / "manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(data), encoding="utf-8")

    def run_promotion(self, *args: str) -> int:
        return promote_lab_asset.main(["--project-root", str(self.root), *args])

    def test_promote_new_copies_pngs_and_writes_runtime_registry(self) -> None:
        result = self.run_promotion(
            "--operation", "promote-new",
            "--type", "character",
            "--asset-id", "test_hero",
            "--image-version", "1",
            "--animation", "jump=1",
        )
        self.assertEqual(result, 0)
        runtime_root = self.root / "media_assets" / "characters" / "test_hero"
        self.assertTrue((runtime_root / "original_images/test_hero__mock__image__v001.png").is_file())
        self.assertTrue((runtime_root / "sprite_sheets/test_hero__mock__jump__v001.png").is_file())
        self.assertFalse((runtime_root / "animation_gifs").exists())
        state = json.loads((self.root / "game_data/promoted_assets.json").read_text(encoding="utf-8"))
        self.assertEqual(state["assets"]["test_hero"]["image"]["version"], 1)
        self.assertIn("test_hero", (self.root / "game_data/asset_manifest.lua").read_text(encoding="utf-8"))

    def test_update_replaces_same_slot_and_keeps_registry_valid(self) -> None:
        self.test_promote_new_copies_pngs_and_writes_runtime_registry()
        self.write_png(self.lab_images / "test_hero__mock__image__v002.png", (8, 8))
        self.write_manifest(image_version=2, animation_version=1)
        result = self.run_promotion(
            "--operation", "promote-update",
            "--type", "character",
            "--asset-id", "test_hero",
            "--image-version", "2",
        )
        self.assertEqual(result, 0)
        runtime_root = self.root / "media_assets/characters/test_hero/original_images"
        self.assertFalse((runtime_root / "test_hero__mock__image__v001.png").exists())
        self.assertTrue((runtime_root / "test_hero__mock__image__v002.png").exists())
        state = json.loads((self.root / "game_data/promoted_assets.json").read_text(encoding="utf-8"))
        self.assertEqual(state["assets"]["test_hero"]["animations"]["jump"]["version"], 1)

    def test_dry_run_does_not_create_runtime_files(self) -> None:
        result = self.run_promotion(
            "--operation", "promote-new",
            "--type", "character",
            "--asset-id", "test_hero",
            "--image-version", "1",
            "--animation", "jump=1",
            "--dry-run",
        )
        self.assertEqual(result, 0)
        self.assertFalse((self.root / "media_assets").exists())
        self.assertFalse((self.root / "game_data/promoted_assets.json").exists())

    def test_new_duplicate_and_missing_source_are_rejected(self) -> None:
        self.assertEqual(self.run_promotion("--operation", "promote-new", "--type", "character", "--asset-id", "test_hero", "--image-version", "1"), 0)
        self.assertEqual(self.run_promotion("--operation", "promote-new", "--type", "character", "--asset-id", "test_hero", "--image-version", "1"), 1)
        self.write_manifest(image_version=2, animation_version=1)
        self.assertEqual(self.run_promotion("--operation", "promote-update", "--type", "character", "--asset-id", "test_hero", "--image-version", "2"), 1)


if __name__ == "__main__":
    unittest.main()
