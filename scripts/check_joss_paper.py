"""Check the repository-local JOSS paper assets without requiring JOSS tooling."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "docs" / "paper.md"
BIBLIOGRAPHY = ROOT / "docs" / "paper.bib"
REQUIRED_HEADINGS = (
    "# Summary",
    "# Statement of need",
    "# Software design",
    "# State of the field",
    "# Research impact statement",
    "# Research applications and limitations",
    "# Availability",
    "# AI usage disclosure",
)


def paper_word_count(text: str) -> int:
    """Count prose-like tokens outside the YAML front matter."""
    body = text
    if body.startswith("---"):
        _, _, body = body.split("---", 2)
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'-]*", body))


def validate_paper() -> list[str]:
    errors: list[str] = []
    if not PAPER.exists():
        return ["Missing docs/paper.md."]
    if not BIBLIOGRAPHY.exists():
        return ["Missing docs/paper.bib."]

    paper = PAPER.read_text()
    bibliography = BIBLIOGRAPHY.read_text()
    for field in ("title:", "tags:", "authors:", "affiliations:", "bibliography:"):
        if field not in paper.split("---", 2)[1]:
            errors.append(f"Missing YAML metadata field: {field}")
    for heading in REQUIRED_HEADINGS:
        if heading not in paper:
            errors.append(f"Missing required section: {heading}")

    if "no independently documented external research user" not in paper:
        errors.append("Research impact statement must state the current external-use evidence.")
    if "tools/models and versions" not in paper:
        errors.append("AI usage disclosure must require tool/model/version confirmation before submission.")

    stale_phrases = (
        "domain-maturity matrix",
        "Runtime Studio",
        "12-paper runtime",
        "196 domain",
        "domain adapters",
    )
    for phrase in stale_phrases:
        if phrase.lower() in paper.lower():
            errors.append(f"docs/paper.md still advertises removed release surface: {phrase!r}")

    if "ARCHIVE_NOTICE_2026-08-25.md" not in paper:
        errors.append("Software design or availability must reference ARCHIVE_NOTICE_2026-08-25.md.")

    words = paper_word_count(paper)
    if not 750 <= words <= 1750:
        errors.append(f"docs/paper.md has {words} words; JOSS expects 750-1750.")

    cited = set(re.findall(r"\[@([A-Za-z0-9_-]+)\]", paper))
    available = set(re.findall(r"@\w+\{([^,]+),", bibliography))
    missing = sorted(cited - available)
    if missing:
        errors.append(f"docs/paper.bib is missing cited keys: {', '.join(missing)}")
    return errors


def main() -> int:
    errors = validate_paper()
    if errors:
        print("\n".join(errors))
        return 1
    print(f"JOSS paper assets valid ({paper_word_count(PAPER.read_text())} words).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
