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
"$PYTHON" scripts/generate_domain_matrix.py --check > "$OUT/logs/domain-matrix-check.txt"

"$PYTHON" cdfd.py doctor --json --out "$OUT/evidence/doctor.json" > "$OUT/logs/doctor.stdout.json"
"$PYTHON" cdfd.py gallery --json --out "$OUT/evidence/gallery.json" > "$OUT/logs/gallery.stdout.json"
"$PYTHON" cdfd.py compare origins_of_life \
  --scenarios mixed_source_surface_trap meteoritic_seed_retained terrestrial_synthesis \
  --json --out "$OUT/evidence/origins_compare.json" > "$OUT/logs/origins-compare.stdout.json"
"$PYTHON" cdfd.py report "$OUT/evidence/gallery.json" --format markdown --out "$OUT/evidence/gallery_report.md" > "$OUT/logs/report.stdout.txt"
"$PYTHON" cdfd.py explain "$OUT/evidence/gallery.json" --format markdown --out "$OUT/evidence/gallery_explain.md" > "$OUT/logs/explain.stdout.txt"

"$PYTHON" -m pytest -q tests/test_cli_runtime.py tests/test_new_engine_upgrades.py tests/test_release_surfaces.py \
  > "$OUT/evidence/test-report.txt"

"$PYTHON" -m build --sdist --wheel --outdir "$OUT/package" > "$OUT/logs/python-build.txt"

tar \
  --exclude='./.git' \
  --exclude='./.venv' \
  --exclude='./__pycache__' \
  --exclude='./build' \
  --exclude='./dist' \
  -czf "$OUT/package/CDFD-Runtime-checkout-$STAMP.tar.gz" .

if command -v latexmk >/dev/null 2>&1; then
  papers/build_pdfs.sh > "$OUT/evidence/paper-pdf-build.log" 2>&1
else
  test "$(find papers/PDFs -maxdepth 1 -name '*.pdf' | wc -l)" -eq 12
  echo "latexmk not installed; verified 12 committed runtime PDFs" > "$OUT/evidence/paper-pdf-build.log"
fi

(
  cd "$OUT"
  find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum
) > "$OUT/SHA256SUMS"

echo "bundle complete: $OUT"
