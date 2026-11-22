from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from support import REPO, run_script, write


class EnglishCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_reports_korean_prose_with_location(self) -> None:
        write(self.root / "docs/guide.md", "# Guide\n\n설명이 남았다.\n")
        result = run_script("english-check.py", str(self.root))
        self.assertEqual(result.returncode, 1)
        self.assertIn("docs/guide.md:3:", result.stdout)
        self.assertIn("1 Korean line(s) in 1 file(s)", result.stdout)

    def test_translations_test_data_and_translation_links_are_allowed(self) -> None:
        write(self.root / "README.md", "# Title\n\n한국어 문서: [README.ko.md](README.ko.md)\n")
        write(self.root / "README.ko.md", "# 제목\n")
        write(self.root / "infra/tests/test_titles.py", "TITLE = '한글 제목'\n")
        write(self.root / "image.bin", "")
        (self.root / "image.bin").write_bytes(b"\xff\xfe\x00binary")
        result = run_script("english-check.py", str(self.root))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("0 Korean line(s)", result.stdout)

    def test_dashes_and_arrows_are_not_korean(self) -> None:
        write(self.root / "notes.md", "inbox → spec — done\n")
        self.assertEqual(run_script("english-check.py", str(self.root)).returncode, 0)

    def test_git_tracked_tree_is_english(self) -> None:
        result = run_script("english-check.py", str(REPO))
        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
