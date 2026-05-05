# Lecture content

The slide deck and the four notebooks I actually teach from. The runnable container and conda env live in [`../student-environment/`](../student-environment/).

I wrote this lecture for a 105-minute slot. The rough block structure I aim for:

- *Recap of LAT data products and the Science Tools.* Slides 1–9, paired with notebook 00 as a live skim. ~15 min.
- *Fermipy worked examples.* Slides 10–28, notebooks 01 and 02. The two notebooks together fill ~60 min if you don't try to compute lightcurves live (use the precomputed pickled state).
- *Gammapy and joint multi-instrument fits.* Slides 23–28, notebook 03. ~20 min.
- *Wrap-up.* ~10 min.

The big computations (`gta.setup()`, the TXS lightcurve) are precomputed in the bundled data, so live demos load via `gta.load_roi()` rather than waiting for `gtltcube` mid-lecture.

## Layout

```
lecture/
├── README.md                       # this
├── slides/                         # Marp deck (.md, rendered .pdf and .html, render.sh, img/)
└── notebooks/                      # the master copies (with absolute paths to my laptop)
    ├── _build_notebooks.py
    ├── 00_data_levels.ipynb
    ├── 01_fermipy_pg1553.ipynb
    ├── 02_fermipy_txs0506.ipynb
    ├── 03_gammapy_joint_crab.ipynb
    ├── gtmktime.par
    └── gtselect.par
```

The notebooks here are the ones I keep editing during prep. The portable copies that students actually run are at [`../student-environment/notebooks/`](../student-environment/notebooks/) and read paths from `$LECTURE_DATA` / `$GAMMAPY_DATA` / `$CONDA_PREFIX`. If I regenerate these masters via `_build_notebooks.py`, I have to re-run the patching step in `student-environment/` to keep the student copies in sync.

## Slides

```bash
cd slides
./render.sh                # marp -> lecture.html and lecture.pdf
```

The "Marp for VS Code" extension also works well: open `slides/lecture.md`, hit the preview eye, export.

## Credits

- Manuel Meyer's ISAPP 2021 fermipy hands-on for the PG 1553+113 worked example, the likelihood-loop diagrams, and the PSF-vs-energy panels in Block II.
- The Black Hole Group fermipy tutorial (Cafardo, Nemmen, de Menezes; CC-BY) for the TXS 0506+056 notebook structure.
- SLAC Fermi Summer School notes (Wood, Perkins, et al.) for several of the Block I figures (FSSC website screenshots, event-class table, recommended-cuts table).
- The gammapy team for `joint-crab` and the methodology in [Nigro et al. 2019, *A&A* 625, A10](https://www.aanda.org/articles/aa/abs/2019/05/aa34938-18/aa34938-18.html).

Lecture by Milena Crnogorčević · Stockholm University · <milena.crnogorcevic@fysik.su.se>
