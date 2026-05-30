#!/usr/bin/env bash
# Rebuild all runtime paper PDFs into papers/PDFs/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD="${TMPDIR:-/tmp}/cdfd_runtime_papers_build"
PDF_DIR="$ROOT/papers/PDFs"

mkdir -p "$BUILD" "$PDF_DIR"
cd "$ROOT"

for tex in papers/[0-9][0-9]_*.tex; do
  base="$(basename "$tex" .tex)"
  echo "==> $base"
  latexmk -pdf -interaction=nonstopmode -halt-on-error \
    -output-directory="$BUILD" "$tex"
  cp -f "$BUILD/${base}.pdf" "$PDF_DIR/${base}.pdf"
done

echo "PDFs updated in $PDF_DIR"
