from pathlib import Path

from scripts.check_joss_paper import paper_word_count, validate_paper


ROOT = Path(__file__).resolve().parents[1]


def test_joss_paper_assets_are_present_and_consistent():
    assert validate_paper() == []
    words = paper_word_count((ROOT / "docs" / "paper.md").read_text())
    assert 750 <= words <= 1750

