#!/usr/bin/env python3
"""Export Part II diagnostics via the CLI backend (prefer `python cdfd.py diagnostics`)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.diagnostics import write_json
from runtime.runner import part_ii_diagnostics


def main() -> int:
    out = ROOT / "experiments" / "outputs" / "part_ii_runtime_diagnostics.json"
    result = part_ii_diagnostics()
    write_json(out, result)
    print(f"wrote {out}")
    return 0 if result.get("status") == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
