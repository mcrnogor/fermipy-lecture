# Running the lecture environment

This folder has a Docker recipe and a conda recipe. Either one gets you a working environment with fermipy 1.4, gammapy 1.3, fermitools 2.2, JupyterLab, and the four lecture notebooks.

The lecture data itself (~700 MB of FT1/FT2 plus the precomputed source maps for PG 1553 and TXS 0506) lives separately on Dropbox and gets pulled at first run by [`setup_data.sh`](setup_data.sh). That keeps the image/env reasonable in size and means I can update the data without rebuilding the image.

## Docker (the easy path)

You'll need Docker Desktop on Mac/Windows or `docker` on Linux, plus about 4 GB of free disk for the image. On Apple Silicon, fermitools is x86_64-only, so Docker Desktop runs the image through Rosetta. It's slower than native, but it works.

I've pushed the image to Docker Hub:

```bash
docker volume create fermipy-data
docker run --rm -p 8888:8888 -v fermipy-data:/opt/lecture-data mcrnogor23/fermipy-lecture:latest
```

Open the URL it prints. The first launch downloads the lecture data into the named volume; subsequent launches reuse it.

If you have a tarball instead of a Docker Hub pull:

```bash
gunzip -c fermipy-lecture.tar.gz | docker load
docker volume create fermipy-data
docker run --rm -p 8888:8888 -v fermipy-data:/opt/lecture-data fermipy-lecture:latest
```

## Conda (if you'd rather skip Docker)

You'll need miniforge or any conda distribution. From this folder:

```bash
bash setup_conda.sh
```

That creates a `fermipy-lecture` env, downloads the lecture data into `~/fermipy-lecture-data/`, downloads the gammapy tutorial datasets into `~/gammapy-data/1.3/`, and wires both paths into the env's activate hook so the notebooks find them. Takes about 10 min on a decent connection.

Then:

```bash
conda activate fermipy-lecture
cd student-environment/notebooks
jupyter lab
```

## What's actually in the environment

```
python      3.9.22
fermipy     1.4.0      (pip)
fermitools  2.2.0      (fermi channel)
gammapy     1.3        (conda-forge)
astropy     6.0
numpy       1.26
matplotlib  3.9
```

In the container, the lecture data ends up at `/opt/lecture-data/{pg1553,txs0506}/` (the named Docker volume), the gammapy tutorial data is baked in at `/opt/gammapy-data/1.3/`, the Fermi diffuse models live where fermitools puts them under `$CONDA_PREFIX/share/fermitools/refdata/`, and the notebooks are at `/home/student/notebooks/`.

In the conda case the lecture data is in `~/fermipy-lecture-data/` and the gammapy data in `~/gammapy-data/1.3/`. The notebooks read whichever via `$LECTURE_DATA` / `$GAMMAPY_DATA` / `$CONDA_PREFIX`, so the same `.ipynb` files work in both layouts.

## Things that bit me — keep an eye on these

A few rough edges I hit while building this. They're documented inline in the notebooks too, but worth flagging up front:

**`gta.lightcurve` crashes on macOS.** macOS uses `spawn` for new processes, which trips a circular import inside fermipy (`fermipy.lightcurve` ↔ `fermipy.gtanalysis`). Notebook 02 sets `multithread=False` to avoid it. Sequential is slow (30–45 min for 24 monthly bins on a cold run), but reliable.

**TXS 0506+056 and the +0541 vs +0542 trap.** 3FGL has it at `+0541`; 4FGL renamed it to `+0542` because the centroid moved. Notebook 02 uses the 4FGL name. If you copy a config from somewhere older, watch out.

**Apple Silicon throughput.** Rosetta gives you maybe half native speed on the fermitools steps.

**Container can't reach `localhost:8888`.** Check that Docker Desktop is actually running and that you used `-p 8888:8888`. On Linux you may need `--network=host` instead.