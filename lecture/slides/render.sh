#!/usr/bin/env bash
# Render lecture.md to HTML and PDF using Marp CLI.
#
# Install Marp CLI once:
#   npm install -g @marp-team/marp-cli
# or (no install, recommended):
#   alias marp='npx -y @marp-team/marp-cli@latest'
set -euo pipefail
cd "$(dirname "$0")"

MARP="${MARP:-npx -y @marp-team/marp-cli@latest}"

echo "[render] HTML  -> lecture.html"
$MARP --html lecture.md -o lecture.html

echo "[render] PDF   -> lecture.pdf"
$MARP --pdf  --allow-local-files lecture.md -o lecture.pdf

echo "[render] PPTX  -> lecture.pptx (editable in Keynote/PowerPoint)"
$MARP --pptx --allow-local-files lecture.md -o lecture.pptx

echo "[render] done."
