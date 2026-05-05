#!/bin/bash
# Container entrypoint.
#   1. If the lecture data isn't present, fetch it via setup_data.sh.
#   2. Activate the conda env and launch JupyterLab on 0.0.0.0:8888 (no auth — local use only).
# Note: no `set -u`.  fermitools' activate hook references $CALDB
# (set inside the hook itself), which would trip an unset-variable error.
set -eo pipefail

# Step 1 — activate the env first so `curl` (from conda) is on PATH
source /opt/conda/etc/profile.d/conda.sh
conda activate fermipy-lecture

# Step 2 — data
if [ ! -d "${LECTURE_DATA}/pg1553" ] || [ ! -d "${LECTURE_DATA}/txs0506" ]; then
    echo "[start] Lecture data not found in ${LECTURE_DATA} — running setup_data.sh"
    /usr/local/bin/setup_data.sh "${LECTURE_DATA}"
else
    echo "[start] Lecture data found in ${LECTURE_DATA}"
fi

exec jupyter lab \
    --ip=0.0.0.0 \
    --port=8888 \
    --no-browser \
    --ServerApp.token='' \
    --ServerApp.password='' \
    --ServerApp.allow_origin='*' \
    --notebook-dir=/home/student/notebooks
