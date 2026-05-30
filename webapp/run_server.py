#!/usr/bin/env python3
"""Launch the CDFD Runtime Streamlit dashboard."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    dashboard = Path(__file__).resolve().parent / "dashboard.py"
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(dashboard),
        "--server.headless",
        "true",
    ]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
