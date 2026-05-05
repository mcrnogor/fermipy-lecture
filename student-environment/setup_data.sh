#!/bin/bash
# Download the lecture data tarball (PG 1553 + TXS 0506 FT1/FT2/configs/ancillaries)
# and extract it into a target directory.
#
# Usage:
#   bash setup_data.sh [target_dir]
#
# The URL is hard-coded below — If needed: edit DATA_URL after you've uploaded
# the tarball to Dropbox. 
#
# It can also be overridden at run time:
#   DATA_URL=https://example.com/data.tar.gz bash setup_data.sh
set -euo pipefail

DEFAULT_URL="https://www.dropbox.com/scl/fi/mahe5ydxpj6647x3ppywe/lecture-data.tar.gz?rlkey=it8vqyn0swrh2v8o83n1a7imt&st=0cs08nyq&dl=1"

DATA_URL="${DATA_URL:-$DEFAULT_URL}"
TARGET="${1:-${LECTURE_DATA:-$HOME/fermipy-lecture-data}}"

if [[ "$DATA_URL" == *REPLACE_ME* ]]; then
    cat >&2 <<EOF
ERROR: DATA_URL not configured.

If you are an instructor preparing this for distribution, edit DEFAULT_URL
at the top of this script.  If you are a student, ask your instructor for
the data URL and run:

    DATA_URL=<the-url> bash setup_data.sh

EOF
    exit 1
fi

if [ -d "$TARGET/pg1553" ] && [ -d "$TARGET/txs0506" ]; then
    echo "[setup_data] Data already present in $TARGET — nothing to do."
    exit 0
fi

mkdir -p "$TARGET"
TMP="$(mktemp -t fermipy-lecture.XXXXXX.tar.gz)"
trap 'rm -f "$TMP"' EXIT

echo "[setup_data] Downloading lecture data (~550 MB compressed, ~700 MB extracted) ..."
echo "             from: $DATA_URL"
echo "             to:   $TMP"
curl -L --fail --progress-bar -o "$TMP" "$DATA_URL"

echo "[setup_data] Extracting into $TARGET ..."
# --strip-components 1 collapses an outer "lecture-data/" wrapper if present.
tar xzf "$TMP" -C "$TARGET" --strip-components=1 2>/dev/null \
    || tar xzf "$TMP" -C "$TARGET"

if [ ! -d "$TARGET/pg1553" ] || [ ! -d "$TARGET/txs0506" ]; then
    echo "ERROR: archive extracted but $TARGET/pg1553 or $TARGET/txs0506 still missing." >&2
    echo "Check the tarball layout — it should contain pg1553/ and txs0506/ at the top." >&2
    exit 1
fi

echo "[setup_data] Done. Data is in $TARGET"
