#!/usr/bin/env python3
"""Reproducible CDFL smoke experiment for the slim CDFD Runtime release."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime.diagnostics import clean_json, write_json
from runtime.runner import gallery, validate_cdfl, run_cdfl


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = ROOT / "examples" / "heat_flow.cdfl"
DEFAULT_OUT = Path(__file__).resolve().parent / "outputs" / "cdfl_smoke.json"


def build_payload(*, nx: int, ny: int) -> dict:
    validation = validate_cdfl(DEFAULT_MODEL)
    execution = run_cdfl(DEFAULT_MODEL, nx=nx, ny=ny)
    smoke = gallery(nx=nx, ny=ny, include_cdfl=True)
    return {
        "experiment": "cdfl_smoke",
        "model": str(DEFAULT_MODEL),
        "claim_boundary": "Software smoke only; not empirical validation.",
        "validation": validation,
        "execution": execution,
        "gallery": smoke,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the public CDFL smoke experiment.")
    parser.add_argument("--nx", type=int, default=4)
    parser.add_argument("--ny", type=int, default=4)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--print-json", action="store_true")
    args = parser.parse_args(argv)

    payload = build_payload(nx=args.nx, ny=args.ny)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    write_json(args.out, payload)

    ok = all(
        block.get("status") == "ok" and block.get("finite_audit", {}).get("all_finite")
        for block in (payload["validation"], payload["execution"], payload["gallery"])
    )
    if args.print_json:
        print(json.dumps(clean_json(payload), indent=2, sort_keys=True, allow_nan=False))
    print(f"written: {args.out}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
