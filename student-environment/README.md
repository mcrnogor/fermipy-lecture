# Fermi-LAT + gammapy lecture environment

Self-contained setup for the four lecture notebooks:

- `00_data_levels.ipynb` — what FT1/FT2/CCUBE/etc. actually are
- `01_fermipy_pg1553.ipynb` — fermipy on PG 1553+113
- `02_fermipy_txs0506.ipynb` — fermipy on TXS 0506+056 (the IceCube blazar)
- `03_gammapy_joint_crab.ipynb` — gammapy 5-instrument joint Crab fit

The image / env is **slim** (~3 GB) — environment + notebooks + gammapy tutorial datasets only. The lecture data (~700 MB FT1/FT2/configs/ancillaries for PG 1553 and TXS 0506) is downloaded on first run from a URL (Dropbox).

Pick **one** path:

| | when to use | size | first-run time |
|---|---|---|---|
| **Docker** | you don't have conda or want zero-friction reproducibility | image ~3 GB + 700 MB data | a few minutes |
| **Conda** | you already use conda, want native performance, or want to edit dependencies | env ~3 GB + 700 MB data | ~10 min |

---

## Option A — Docker

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Mac/Windows) or `docker` (Linux), running.
- ~4 GB free disk.
- Apple Silicon: Docker uses Rosetta automatically — fermitools is x86_64-only.

### Pull (if your instructor pushed to Docker Hub)
```bash
docker pull <instructor-username>/fermipy-lecture:latest
docker volume create fermipy-data    # persist the lecture data across runs
docker run --rm -p 8888:8888 \
    -v fermipy-data:/opt/lecture-data \
    <instructor-username>/fermipy-lecture:latest
```

### …or load a tarball
```bash
gunzip -c fermipy-lecture.tar.gz | docker load
docker volume create fermipy-data
docker run --rm -p 8888:8888 -v fermipy-data:/opt/lecture-data fermipy-lecture:latest
```

Open the URL the container prints (`http://localhost:8888/...`) in your browser.

The first `docker run` downloads ~700 MB of data into the named volume. Subsequent runs reuse it.

---

## Option B — Conda

### Prerequisites
- [Miniforge](https://github.com/conda-forge/miniforge) or any conda distribution.
- ~4 GB free disk + internet for ~1 GB of downloads.

### Setup
From this folder:
```bash
bash setup_conda.sh
```
That script:
1. Creates the `fermipy-lecture` env from `environment.yml`.
2. Downloads the lecture data via `setup_data.sh` (default: from the instructor's Dropbox) into `~/fermipy-lecture-data/`.
3. Downloads the gammapy tutorial datasets into `~/gammapy-data/1.3/`.
4. Wires `LECTURE_DATA` and `GAMMAPY_DATA` env vars into the conda activate hook.

### Run
```bash
conda activate fermipy-lecture
cd student-environment/notebooks
jupyter lab
```

---

## Instructor: how to prepare and distribute

### 1. Build the data tarball
```bash
cd /path/to/fermipy            # the directory above lecture/
tar czf lecture-data.tar.gz -C lecture data/pg1553 data/txs0506
# or, if you want the tarball to expand into "lecture-data/pg1553" etc.
# (matches the --strip-components=1 in setup_data.sh):
mkdir -p _staging/lecture-data
cp -r lecture/data/pg1553 lecture/data/txs0506 _staging/lecture-data/
tar czf lecture-data.tar.gz -C _staging lecture-data
rm -rf _staging
```

### 2. Upload to Dropbox and get a direct-download link
- Right-click `lecture-data.tar.gz` → Share → Copy link
- Paste into a text editor, change the trailing `?dl=0` → `?dl=1`
- Paste that URL into `DEFAULT_URL` at the top of `setup_data.sh`

### 3. Build the Docker image
```bash
bash student-environment/build.sh
```

### 4. Distribute
- **Docker Hub** (best UX for students):
  ```bash
  docker tag  fermipy-lecture:latest <your-username>/fermipy-lecture:latest
  docker push <your-username>/fermipy-lecture:latest
  ```
  (Needs `docker login`. Free for public images.)
- **Tarball**:
  ```bash
  docker save fermipy-lecture:latest | gzip > fermipy-lecture.tar.gz
  ```
  Upload the tarball anywhere students can download it.

### 5. Test it from a clean state
```bash
docker volume rm fermipy-data || true
docker volume create fermipy-data
docker run --rm -p 8888:8888 -v fermipy-data:/opt/lecture-data fermipy-lecture:latest
# Open http://localhost:8888 and click through one notebook.
```

---

## Bundled versions

```
python      3.9.22
fermipy     1.4.0      (pip)
fermitools  2.2.0      (fermi channel)
gammapy     1.3        (conda-forge)
astropy     6.0
numpy       1.26
matplotlib  3.9
```

---

## Where things live

| | Docker path | Conda path |
|---|---|---|
| Lecture data | `/opt/lecture-data/{pg1553,txs0506}/` (volume) | `~/fermipy-lecture-data/{pg1553,txs0506}/` |
| gammapy datasets | `/opt/gammapy-data/1.3/` (in image) | `~/gammapy-data/1.3/` |
| Fermi diffuse models | `$CONDA_PREFIX/share/fermitools/refdata/...` | same |
| Notebooks | `/home/student/notebooks/` | `<repo>/student-environment/notebooks/` |

The notebooks read `$LECTURE_DATA` / `$GAMMAPY_DATA` / `$CONDA_PREFIX` so the same notebook works in both layouts.

---

## Troubleshooting

**Apple Silicon Docker is slow.** Expected — fermitools is x86_64 and runs through Rosetta. Lecture notebooks still complete in well under the cited times.

**`setup_data.sh: DATA_URL not configured`.** The instructor hasn't published the data URL yet. Override at run time:
```bash
DATA_URL="https://..." bash setup_data.sh
# or for Docker:
docker run -e DATA_URL="https://..." ... fermipy-lecture
```

**`gta.lightcurve` crashes with `circular import` in spawn workers.** Already handled in notebook 02 (`multithread=False`). Sequential, ~30–45 min on first run, fast on re-run.

**`gta.sed` raises `Brentq failed` / NaN.** Reload the saved ROI before the SED call: `gta.load_roi('fit_txs')`. Notebook 02 does this.

**`No source matching name: 4FGL J0509.4+0541`.** TXS is at `+0542` in 4FGL (the 3FGL name was `+0541`). Notebook 02 uses the correct name.

**Container can't reach `localhost:8888`.** Make sure Docker Desktop is running and you used `-p 8888:8888`. On Linux you may need `--network=host` instead.
