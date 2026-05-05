# Fermi-LAT analysis with fermipy & gammapy — lecture content

A 105-minute lecture: slide deck plus four runnable notebooks.

For the runnable container and environment setup, see [`../student-environment/`](../student-environment/) (top-level guide: [`../README.md`](../README.md)).

```
lecture/
├── README.md                       # this file
├── slides/
│   ├── lecture.md                  # Marp markdown (the deck)
│   ├── lecture.pdf / .html         # rendered output
│   ├── render.sh                   # render to PDF/HTML
│   └── img/
├── notebooks/                      # instructor master copies (use absolute paths)
│   ├── _build_notebooks.py
│   ├── 00_data_levels.ipynb        # FT1/FT2/CCUBE quick tour (~10 min)
│   ├── 01_fermipy_pg1553.ipynb     # PG 1553+113 end-to-end (~25 min)
│   ├── 02_fermipy_txs0506.ipynb    # TXS 0506+056, lightcurve + SED (~25 min)
│   ├── 03_gammapy_joint_crab.ipynb # gammapy 5-instrument joint Crab fit (~5 min)
│   ├── gtmktime.par
│   └── gtselect.par
└── data/                           # NOT in git — fetched at runtime; ~700 MB
```

The notebooks here are the instructor master copies and contain absolute paths
anchored to a local checkout. The portable copies that students get are at
[`../student-environment/notebooks/`](../student-environment/notebooks/) — those
read `$LECTURE_DATA` / `$GAMMAPY_DATA` / `$CONDA_PREFIX` set by the container or
the conda activate hook. If you regenerate the master copies (e.g. via
`_build_notebooks.py`), re-run the patching step in `student-environment/` to
keep the student copies in sync.

---

## Lecture timing (105 min)

| Block | Slides | Notebook | Time |
|------:|--------|----------|------|
| I  — Recap & data products       | 1–9    | `00_data_levels` (live skim)               | ~15 min |
| II — Fermipy: PG 1553+113, TXS   | 10–28  | `01_fermipy_pg1553`, `02_fermipy_txs0506`  | ~60 min |
| III — Gammapy + joint fits       | 23–28  | `03_gammapy_joint_crab`                    | ~20 min |
| IV — When-to-use-what / wrap-up  | 29–end | —                                          | ~10 min |

Heavy `gta.setup()` runs are **pre-computed** in the bundled data so live demos
load via `gta.load_roi('fit0')` / `gta.load_roi('fit_txs')` — no waiting for
`gtltcube` mid-lecture.

---

## Rendering the slides

```bash
cd slides
./render.sh                # produces lecture.html and lecture.pdf via marp
```
Or use VS Code "Marp for VS Code": open `slides/lecture.md`, click the preview
eye, `Export slide deck`.

---

## Credits

- **Manuel Meyer**, ISAPP 2021 fermipy hands-on — the PG 1553+113 worked example, likelihood-loop diagrams, and PSF-vs-energy panels in Block II adapt his deck and his fermipy-extra notebook.
- **Black Hole Group fermipy tutorial** (Cafardo, Nemmen, de Menezes; CC-BY) — the TXS 0506+056 notebook is adapted from `BlazarNeutrino.ipynb`.
- **Fermi Summer School materials** (Wood, Perkins, et al.; SLAC) — `Data_Exploration.ipynb` images (FSSC website, event-class table, recommended-cuts table) used in Block I.
- **Gammapy team** — the joint-Crab tutorial in notebook 03 builds on the gammapy 1.3 `joint-crab` dataset and the methodology of [Nigro et al. 2019, *A&A* 625, A10](https://www.aanda.org/articles/aa/abs/2019/05/aa34938-18/aa34938-18.html).

Lecture by **M. Crnogorčević** (Stockholm University) · <milena.crnogorcevic@fysik.su.se>
