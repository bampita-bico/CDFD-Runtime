#!/usr/bin/env bash
# Build a reproducible local release evidence bundle for CDFD Runtime.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAMP="$(date -u +%Y%m%d-%H%M%S)"
OUT="${1:-"$ROOT/dist/release-bundle-$STAMP"}"
PYTHON="${PYTHON:-python}"

mkdir -p "$OUT"/{package,evidence,logs}
cd "$ROOT"

echo "CDFD Runtime release bundle: $OUT"

git diff --check > "$OUT/logs/git-diff-check.txt"
"$PYTHON" scripts/check_joss_paper.py > "$OUT/logs/joss-paper-check.txt"

"$PYTHON" cdfd.py doctor --json --out "$OUT/evidence/doctor.json" > "$OUT/logs/doctor.stdout.json"
"$PYTHON" cdfd.py gallery --json --out "$OUT/evidence/gallery.json" > "$OUT/logs/gallery.stdout.json"
"$PYTHON" experiments/run_cdfl_smoke.py --out "$OUT/evidence/cdfl_smoke.json" > "$OUT/logs/cdfl-smoke.stdout.txt"
"$PYTHON" cdfd.py report "$OUT/evidence/gallery.json" --format markdown --out "$OUT/evidence/gallery_report.md" > "$OUT/logs/report.stdout.txt"
"$PYTHON" cdfd.py explain "$OUT/evidence/gallery.json" --format markdown --out "$OUT/evidence/gallery_explain.md" > "$OUT/logs/explain.stdout.txt"

"$PYTHON" -m pytest -q tests/test_joss_submission_assets.py tests/test_cli_runtime.py tests/test_release_surfaces.py \
  > "$OUT/evidence/test-report.txt"

"$PYTHON" -m build --sdist --wheel --outdir "$OUT/package" > "$OUT/logs/python-build.txt"

tar \
  --exclude='./.git' \
  --exclude='./.venv' \
  --exclude='./__pycache__' \
  --exclude='./build' \
  --exclude='./dist' \
  -czf "$OUT/package/CDFD-Runtime-checkout-$STAMP.tar.gz" .

(
  cd "$OUT"
  find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum
) > "$OUT/SHA256SUMS"

echo "bundle complete: $OUT"
