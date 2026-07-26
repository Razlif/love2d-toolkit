import json
import tempfile
import unittest
from pathlib import Path

from dev_tools.love_docs import love_docs


class LoveDocsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = love_docs.load_reference()

    def test_reference_is_valid_and_pinned(self):
        self.assertEqual(love_docs.validate_reference(self.reference), [])
        self.assertEqual(self.reference["love_version"], "11.5")

    def test_exact_lookup(self):
        entry = love_docs.lookup(self.reference, "love.graphics.captureScreenshot")
        self.assertIsNotNone(entry)
        self.assertEqual(entry["fullname"], "love.graphics.captureScreenshot")

    def test_lookup_is_case_insensitive(self):
        entry = love_docs.lookup(self.reference, "LOVE.GRAPHICS.CAPTURESCREENSHOT")
        self.assertIsNotNone(entry)

    def test_case_insensitive_search_and_limit(self):
        results = love_docs.search(self.reference, "CAMERA", 3)
        self.assertLessEqual(len(results), 3)
        self.assertTrue(results)

    def test_missing_lookup_returns_none(self):
        self.assertIsNone(love_docs.lookup(self.reference, "love.notARealFunction"))

    def test_malformed_reference_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text("{bad", encoding="utf-8")
            with self.assertRaises(love_docs.ReferenceError):
                love_docs._load_json(path)

    def test_stable_index_is_json_serializable(self):
        encoded = json.dumps(self.reference, ensure_ascii=False, sort_keys=True)
        self.assertIn("love.graphics.captureScreenshot", encoded)

    def test_version_mismatch_is_reported(self):
        mismatched = dict(self.reference)
        mismatched["love_version"] = "11.4"
        errors = love_docs.validate_reference(mismatched)
        self.assertTrue(any("expected Love2D 11.5" in error for error in errors))
