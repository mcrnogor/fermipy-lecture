# Fermi-LAT analysis with fermipy and gammapy

Notebook materials for a lecture on γ-ray analysis with fermipy and gammapy in FK8045: Astroparticle Physics . Four notebooks and a Docker image so students don't have to fight a conda install before they've learned anything.

## Notebooks

[`00_data_levels.ipynb`](lecture/notebooks/00_data_levels.ipynb) — what an FT1 file actually contains, and what `gtselect` / `gtmktime` do to it 

[`01_fermipy_pg1553.ipynb`](lecture/notebooks/01_fermipy_pg1553.ipynb) — PG 1553+113 end to end with fermipy: setup, fit, SED. The clean high-latitude case 

[`02_fermipy_txs0506.ipynb`](lecture/notebooks/02_fermipy_txs0506.ipynb) — TXS 0506+056, the IceCube blazar. Same workflow on a harder source: lower Galactic latitude, source crowding, bright variability, plus a monthly lightcurve around IC-170922A 

[`03_gammapy_joint_crab.ipynb`](lecture/notebooks/03_gammapy_joint_crab.ipynb) — switching to gammapy and fitting the Crab simultaneously across LAT + MAGIC + VERITAS + FACT + H.E.S.S. 

## Running the notebooks

The easiest way is the Docker image from Docker Hub:

```bash
docker volume create fermipy-data
docker run --rm -p 8888:8888 -v fermipy-data:/opt/lecture-data mcrnogor23/fermipy-lecture:latest
```

Open http://localhost:8888 in your browser. The first launch downloads the lecture data (~700 MB) into the named volume; later launches skip that step.

If you'd rather build from this repo, or use a conda env, see [`student-environment/`](student-environment/) — the setup scripts and Dockerfile live there.

## What's in this repo

`lecture/` holds the notebooks. The notebooks here have absolute paths anchored to my laptop, so they don't run as-is on someone else's machine.

`student-environment/` holds the Docker recipe, the conda recipe, and portable copies of the four notebooks (paths driven by environment variables). That's the version I recommend students get.

The lecture data itself — the FT1/FT2 files plus the precomputed source maps for PG 1553 and TXS 0506 — is not in this repo. It lives in Dropbox and is fetched at runtime by [`student-environment/setup_data.sh`](student-environment/setup_data.sh).

## Credits

The notebooks adapt many, many Fermipy/gammapy lecture materials, but primarily:

- The PG 1553+113 worked example follows Manuel Meyer's ISAPP 2021 fermipy hands-on, which itself rebuilds the LAT-team analysis in [Abdo et al. 2010, *ApJ* 708, 1310](https://ui.adsabs.harvard.edu/abs/2010ApJ...708.1310A) and the FSSC [Likelihood Analysis with Python](https://fermi.gsfc.nasa.gov/ssc/data/analysis/scitools/python_tutorial.html) thread.
- The TXS 0506+056 notebook is adapted from the Black Hole Group fermipy tutorial (Cafardo, Nemmen, de Menezes), reproducing the qualitative result from [IceCube et al. 2018, *Science* 361, eaat1378](https://www.science.org/doi/10.1126/science.aat1378).
- The joint-Crab fit uses gammapy's `joint-crab` dataset and the methodology of [Nigro et al. 2019, *A&A* 625, A10](https://www.aanda.org/articles/aa/abs/2019/05/aa34938-18/aa34938-18.html).

fermipy: <https://fermipy.readthedocs.io>  ·  gammapy: <https://docs.gammapy.org>  ·  Fermi Science Tools: <https://fermi.gsfc.nasa.gov/ssc/data/analysis/software/>

Fermi-LAT data is in the public domain.
