#!/bin/bash
# Conda-based setup (alternative to Docker).  Creates the `fermipy-lecture`
# env, downloads the lecture data (via setup_data.sh) and the gammapy tutorial
# datasets, and wires the env vars the notebooks expect into the conda
# activate hook.
set -euo pipefail

HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 1. conda env
echo "[1/4] Creating conda env 'fermipy-lecture' ..."
if conda env list | awk '{print $1}' | grep -qx fermipy-lecture; then
    echo "      env exists; updating"
    conda env update -n fermipy-lecture -f "$HERE/environment.yml"
else
    conda env create -f "$HERE/environment.yml"
fi

# 2. lecture data (downloaded from Dropbox via setup_data.sh)
LECTURE_DATA_DIR="$HOME/fermipy-lecture-data"
echo "[2/4] Fetching lecture data into $LECTURE_DATA_DIR ..."
bash "$HERE/setup_data.sh" "$LECTURE_DATA_DIR"

# 3. gammapy tutorial datasets (~260 MB)
GAMMAPY_DATA_DIR="$HOME/gammapy-data/1.3"
echo "[3/4] Downloading gammapy datasets into $GAMMAPY_DATA_DIR ..."
mkdir -p "$(dirname "$GAMMAPY_DATA_DIR")"
conda run -n fermipy-lecture gammapy download datasets --out "$GAMMAPY_DATA_DIR"

# 4. wire env vars into the activate hook
echo "[4/4] Wiring env vars into 'conda activate fermipy-lecture' ..."
ACT_DIR="$(conda info --base)/envs/fermipy-lecture/etc/conda/activate.d"
mkdir -p "$ACT_DIR"
cat > "$ACT_DIR/lecture_data.sh" <<EOF
export LECTURE_DATA="$LECTURE_DATA_DIR"
export GAMMAPY_DATA="$GAMMAPY_DATA_DIR"
EOF

cat <<EOF

Done.

    conda activate fermipy-lecture
    cd $HERE/notebooks
    jupyter lab
EOF
