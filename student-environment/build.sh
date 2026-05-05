#!/bin/bash
# Instructor convenience: build the slim Docker image (no lecture data baked in).
# Run me from anywhere; I cd to the repo root so docker build can see the
# Dockerfile under student-environment/.
set -euo pipefail

ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$ROOT"

for p in student-environment/Dockerfile \
         student-environment/environment.yml \
         student-environment/setup_data.sh \
         student-environment/start.sh \
         student-environment/notebooks; do
    [ -e "$p" ] || { echo "MISSING: $p"; exit 1; }
done

echo "Building from $ROOT"
docker build \
    --platform=linux/amd64 \
    -t fermipy-lecture:latest \
    -f student-environment/Dockerfile \
    .

cat <<EOF

Image built: fermipy-lecture:latest

Run it (data will be fetched into a named volume on first start):

    docker volume create fermipy-data
    docker run --rm -p 8888:8888 -v fermipy-data:/opt/lecture-data fermipy-lecture:latest

…then open http://localhost:8888

Distribution options:

  1. Docker Hub  (recommended)
       docker tag  fermipy-lecture:latest <your-username>/fermipy-lecture:latest
       docker push <your-username>/fermipy-lecture:latest

  2. Tarball  (no registry)
       docker save fermipy-lecture:latest | gzip > fermipy-lecture.tar.gz
       students:  gunzip -c fermipy-lecture.tar.gz | docker load
EOF
