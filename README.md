# Fermi-LAT analysis with fermipy & gammapy — lecture materials

A self-contained, runnable lecture on γ-ray analysis with **fermipy** and **gammapy**, built around four notebooks:

| # | notebook | what it does | runtime |
|---|---|---|---|
| 00 | [`00_data_levels.ipynb`](lecture/notebooks/00_data_levels.ipynb) | FT1/FT2/CCUBE quick tour — what the files actually are | ~10 min |
| 01 | [`01_fermipy_pg1553.ipynb`](lecture/notebooks/01_fermipy_pg1553.ipynb) | PG 1553+113 end-to-end fermipy analysis (clean high-latitude HBL) | ~25 min |
| 02 | [`02_fermipy_txs0506.ipynb`](lecture/notebooks/02_fermipy_txs0506.ipynb) | TXS 0506+056 (the IceCube blazar): SED + lightcurve around IC-170922A | ~25 min |
| 03 | [`03_gammapy_joint_crab.ipynb`](lecture/notebooks/03_gammapy_joint_crab.ipynb) | gammapy 5-instrument joint Crab fit — Fermi-LAT + MAGIC + VERITAS + FACT + H.E.S.S. | ~5 min |

The lecture is paired with a **Docker container** ([`student-environment/`](student-environment/)) that bundles fermipy, fermitools, gammapy, the gammapy tutorial datasets, and the patched notebooks. The lecture data (FT1/FT2 + pre-computed source maps for PG 1553 and TXS 0506, ~700 MB) is **fetched on first run** from Dropbox by [`setup_data.sh`](student-environment/setup_data.sh) — that's why the image is only ~4 GB instead of ~5 GB.

---

## Run it (students)

> Replace `YOUR_DH_USER` below with the Docker Hub user the lecturer pushed the image under (announced in class).

```bash
docker volume create fermipy-data
docker run --rm -p 8888:8888 -v fermipy-data:/opt/lecture-data \
    YOUR_DH_USER/fermipy-lecture:latest
```

Open `http://localhost:8888` in your browser. First run downloads the lecture data; subsequent runs reuse it.

If you'd rather not use Docker, [`student-environment/`](student-environment/) also contains a conda recipe ([`setup_conda.sh`](student-environment/setup_conda.sh) + [`environment.yml`](student-environment/environment.yml)).

Full instructions, prerequisites, and troubleshooting: [`student-environment/README.md`](student-environment/README.md).

---

## Repository layout

```
.
├── README.md                       # this file
├── LICENSE                         # MIT
├── lecture/
│   ├── README.md                   # lecture-specific notes
│   ├── slides/                     # Marp slide deck
│   └── notebooks/                  # the four working notebooks (instructor master copies)
└── student-environment/            # the runnable container + conda env
    ├── README.md                   # full setup & distribution guide
    ├── Dockerfile                  # fermipy 1.4.0 + fermitools 2.2.0 + gammapy 1.3
    ├── environment.yml             # conda spec (alternative to Docker)
    ├── setup_data.sh               # fetches the lecture data tarball from Dropbox
    ├── setup_conda.sh              # one-shot conda installer
    ├── start.sh                    # container entrypoint (jupyter lab)
    ├── build.sh                    # instructor: builds the Docker image
    └── notebooks/                  # patched copies of the 4 (paths driven by env vars)
```

The lecture data and the data tarball are **not in this repo** (~700 MB and 554 MB respectively). They're hosted on Dropbox and fetched at runtime — see `setup_data.sh`.

---

## Rebuild / redistribute (instructor)

If you change the notebooks or environment, rebuild and republish:

```bash
# 1. (only if data changed) rebuild the data tarball and re-upload to Dropbox
mkdir -p _staging/lecture-data
cp -R lecture/data/pg1553 lecture/data/txs0506 _staging/lecture-data/
COPYFILE_DISABLE=1 tar czf lecture-data.tar.gz \
    --exclude='._*' --exclude='*conflicted copy*' \
    -C _staging lecture-data
rm -rf _staging
# replace lecture-data.tar.gz in Dropbox; the share URL stays the same.

# 2. rebuild the Docker image
bash student-environment/build.sh

# 3. push to Docker Hub
docker tag  fermipy-lecture:latest YOUR_DH_USER/fermipy-lecture:latest
docker push YOUR_DH_USER/fermipy-lecture:latest
```

Full instructor walk-through (Dropbox URL formatting, Docker Hub vs tarball distribution, troubleshooting): [`student-environment/README.md`](student-environment/README.md).

---

## Acknowledgements

The notebooks adapt the following published tutorials:

- **PG 1553+113** — M. Meyer's hands-on (ISAPP 2021), based on the LAT-team study in [Abdo et al. 2010, *ApJ* 708, 1310](https://ui.adsabs.harvard.edu/abs/2010ApJ...708.1310A) and the FSSC [Likelihood Analysis with Python](https://fermi.gsfc.nasa.gov/ssc/data/analysis/scitools/python_tutorial.html) thread.
- **TXS 0506+056** — adapted from the Black-Hole-Group fermipy tutorial (Cafardo, Nemmen, de Menezes), reproducing a qualitative version of [IceCube et al. 2018, *Science* 361, eaat1378](https://www.science.org/doi/10.1126/science.aat1378).
- **Joint Crab** — gammapy `joint-crab` dataset and methodology of [Nigro et al. 2019, *A&A* 625, A10](https://www.aanda.org/articles/aa/abs/2019/05/aa34938-18/aa34938-18.html).

fermipy: <https://fermipy.readthedocs.io>  ·  gammapy: <https://docs.gammapy.org>  ·  Fermi Science Tools: <https://fermi.gsfc.nasa.gov/ssc/data/analysis/software/>

Fermi-LAT data is in the public domain.

## License

MIT — see [`LICENSE`](LICENSE).
