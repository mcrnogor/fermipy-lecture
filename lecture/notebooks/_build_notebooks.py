"""Generate the four lecture notebooks from inline Python source.

Run once:
    python _build_notebooks.py

Each notebook is a list of (kind, body) pairs:
    kind = "md" | "py"
"""
from __future__ import annotations
import json
import pathlib

HERE = pathlib.Path(__file__).parent

KERNEL = {
    "kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
    "language_info": {"name": "python"},
}


def cell(kind: str, body: str) -> dict:
    src = body.rstrip("\n").splitlines(keepends=True)
    if kind == "md":
        return {"cell_type": "markdown", "metadata": {}, "source": src}
    return {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": src,
    }


def write(name: str, cells: list[tuple[str, str]]) -> None:
    nb = {
        "metadata": KERNEL,
        "nbformat": 4,
        "nbformat_minor": 5,
        "cells": [cell(k, b) for k, b in cells],
    }
    out = HERE / name
    out.write_text(json.dumps(nb, indent=1))
    print(f"wrote {out}")


# ---------------------------------------------------------------------------
# 00 — data products
# ---------------------------------------------------------------------------
nb00 = [
    ("md", """\
# 00 — Fermi-LAT data products: a quick tour

**Goal of this notebook (~10 min).** Before we run any tool, look at the *raw* data product you start from: the FT1 photon list and the FT2 spacecraft history. We will:

1. Read the FT1 files with `astropy.io.fits`.
2. Plot the energy spectrum and the ROI sky distribution.
3. Decode the `EVENT_CLASS` / `EVENT_TYPE` bitfields the LAT processing pipeline writes.
4. Look at one row of FT2 to understand pointing / livetime.
5. Run `gtselect` and `gtmktime` by hand to produce a clean event list.

This is the **Level-2** product (cf. [FSSC, *Cicerone — LAT Data Products*](https://fermi.gsfc.nasa.gov/ssc/data/analysis/documentation/Cicerone/Cicerone_Data/LAT_DP.html)). Everything `fermipy` and `gammapy` do downstream is bookkeeping on top of these two files plus the IRFs and diffuse templates.

> **Local-run note.** This is the *local* (non-Docker) version of the notebook. Make sure VS Code's Jupyter extension is using the `fermipy` conda env: open the kernel picker (top-right) and pick the interpreter at `/Users/mcrnogor/miniconda3/envs/fermipy/bin/python`. The `gt_apps` import in the last section requires the Fermi Science Tools, which only ship in that env.
"""),
    ("py", """\
%matplotlib inline
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.coordinates import SkyCoord
import astropy.units as u
from glob import glob
from pathlib import Path

# Local data directory (already populated by hand from the LAT Data Server,
# Meyer ISAPP 2021 query: PG 1553+113, 20 deg, MET 239557417 -> 271093418).
ANADIR = Path("/Users/mcrnogor/Library/CloudStorage/Dropbox/"
              "lectures/fermipy/lecture/data/pg1553")

FT1_GLOB = str(ANADIR / "L*_PH0?.fits")
FT2_GLOB = str(ANADIR / "L*_SC00.fits")

print("ANADIR    :", ANADIR)
print("FT1 chunks:", sorted(p.name for p in ANADIR.glob("L*_PH0?.fits")))
print("FT2 file  :", sorted(p.name for p in ANADIR.glob("L*_SC00.fits")))
"""),
    ("md", """\
## 1. The FT1 photon list

Each row is *one* gamma-ray candidate. The LAT Data Server returns multiple FT1 chunks per query (the server splits long time ranges to keep individual files manageable), so we have three `*_PH00.fits`, `*_PH01.fits`, `*_PH02.fits` chunks covering the full 1-yr Meyer window MET 239 557 417 → 271 093 418 (2008-08-04 → 2009-08-04 UTC).

The columns are documented in [FSSC, *Cicerone — LAT Data Columns*](https://fermi.gsfc.nasa.gov/ssc/data/analysis/documentation/Cicerone/Cicerone_Data/LAT_Data_Columns.html). The most-used ones, with the FSSC definitions verbatim:

| column | unit | FSSC definition |
|---|---|---|
| `TIME`         | s    | "Mission elapsed time when the event was detected" — MET = total seconds since 00:00:00 UTC on 2001-01-01 |
| `ENERGY`       | MeV  | "Reconstructed energy of the event" |
| `RA`           | deg  | "Reconstructed direction of the event in Right Ascension" |
| `DEC`          | deg  | "Reconstructed direction of the event in Declination" |
| `L`, `B`       | deg  | reconstructed direction in galactic coordinates |
| `THETA`        | deg  | "Reconstructed angle of incidence of the event with respect to the LAT boresight (+Z axis of the spacecraft)" |
| `ZENITH_ANGLE` | deg  | "Angle between the reconstructed event direction and the zenith line (originates at the centre of the Earth and passes through the centre of mass of the spacecraft)" |
| `EVENT_CLASS`  | bits | "A bitfield indicating which event-class selections a given event has passed" |
| `EVENT_TYPE`   | bits | "A bitfield indicating which event-type selections a given event has passed" |

The MET reference epoch is encoded in the FT1 header as `MJDREFI = 51910` (= 2001-01-01) and `MJDREFF ≈ 7.43e-4` d (a small offset that pins the reference to the chosen TIMESYS, here `TT`).
"""),
    ("py", """\
ft1_files = sorted(glob(FT1_GLOB))
assert ft1_files, f"no FT1 files matched {FT1_GLOB}"

# Inspect the first chunk in detail.
hdul = fits.open(ft1_files[0])
hdul.info()

events_chunk0 = hdul["EVENTS"].data
hdr           = hdul["EVENTS"].header

print("\\nEVENTS columns + units:")
for c in events_chunk0.columns:
    print(f"  {c.name:22s} fmt={c.format:6s} unit={c.unit or '-'}")

print(f"\\nrows in this chunk: {len(events_chunk0):,}")
print(f"TSTART = {hdr['TSTART']:.0f} MET s")
print(f"TSTOP  = {hdr['TSTOP']:.0f} MET s   "
      f"(chunk spans {(hdr['TSTOP']-hdr['TSTART'])/86400:.1f} d)")
print(f"TIMESYS = {hdr['TIMESYS']}, MJDREFI = {hdr['MJDREFI']}, "
      f"MJDREFF = {hdr['MJDREFF']:.6e}")
"""),
    ("md", """\
The first chunk alone has ~232 k events — *a lot* of photons for one tutorial source — because the FT1 file contains *every* event reconstructed inside the 20°-radius search cone, *across all event classes*. The spatial / class / energy / zenith cuts that select a SOURCE-class point-source dataset are applied later by `gtselect`.

For the energy and sky plots below we concatenate all three chunks so we see the whole 1-yr window at once.
"""),
    ("py", """\
all_events = np.concatenate([fits.open(f)["EVENTS"].data for f in ft1_files])
print(f"total events across {len(ft1_files)} chunks: {len(all_events):,}")
"""),
    ("py", """\
fig, ax = plt.subplots(1, 2, figsize=(12, 4))

# energy spectrum (counts per log-E bin)
e = all_events["ENERGY"]
ax[0].hist(np.log10(e), bins=60)
ax[0].set_xlabel(r"$\\log_{10}(E\\,/\\,\\mathrm{MeV})$")
ax[0].set_ylabel("counts per bin")
ax[0].set_title("FT1 reconstructed energy (all events, no cuts)")

# sky distribution in galactic coords
c = SkyCoord(all_events["RA"]*u.deg, all_events["DEC"]*u.deg).galactic
ax[1].hexbin(c.l.wrap_at(180*u.deg).deg, c.b.deg,
             gridsize=80, cmap="magma", bins="log")
ax[1].invert_xaxis()                         # convention: l increases to the left
ax[1].set_xlabel("galactic l (deg)")
ax[1].set_ylabel("galactic b (deg)")
ax[1].set_title("FT1 sky distribution (20° cone around PG 1553+113)")

# mark PG 1553+113 itself
pg = SkyCoord(238.929*u.deg, 11.190*u.deg).galactic
ax[1].plot(pg.l.wrap_at(180*u.deg).deg, pg.b.deg,
           marker='+', color='cyan', mew=2, ms=14, label='PG 1553+113')
ax[1].legend(loc='lower right')
fig.tight_layout()
"""),
    ("md", """\
**Things to notice.**

- The energy histogram falls steeply: most photons sit at a few hundred MeV, very few above 100 GeV. The LAT effective area also varies with energy, but the dominant effect is the *source-population* spectrum (∝ E^−2.x for typical extragalactic sources, plus diffuse).
- PG 1553+113 sits at $(l,b)\\approx(21.9^\\circ,\\ +43.9^\\circ)$, well off the galactic plane — no bright diffuse background, no nearby pulsar, no SNR. That is why this source is a textbook target.
- The 20° search cone is much larger than the 10°-side ROI we will fit later. The padding lets the LAT PSF and the diffuse templates "leak" properly into the ROI from outside its boundary, which keeps the fit unbiased near the edges.
"""),
    ("md", """\
## 2. Event class / event type bitfields

The LAT processing pipeline runs *every* photon through a chain of background-rejection cuts and stores the per-event result in two FITS columns of TFORM `32X` — i.e. a 32-bit field, one bit per cut. We **never re-run the cuts**; we *select* events whose mask has a given bit set ([FSSC, *Cicerone — LAT IRFs*](https://fermi.gsfc.nasa.gov/ssc/data/analysis/documentation/Cicerone/Cicerone_LAT_IRFs/IRF_overview.html)).

For Pass 8 P8R3 (the current reprocessing), the standard event-class hierarchy is:

| EVENT_CLASS bit | name | `evclass` value (= `2**bit`) |
|----:|---|----:|
|  4  | P8R3_TRANSIENT020      |    16 |
|  6  | P8R3_TRANSIENT010      |    64 |
|  7  | **P8R3_SOURCE**        |   **128** |
|  8  | P8R3_CLEAN             |   256 |
|  9  | P8R3_ULTRACLEAN        |   512 |
| 10  | P8R3_ULTRACLEANVETO    |  1024 |
| 11  | P8R3_SOURCEVETO        |  2048 |
| 16  | P8R3_TRANSIENT015S     | 65536 |

The classes are **nested**: a photon that passes `ULTRACLEANVETO` automatically passes `ULTRACLEAN`, `CLEAN`, `SOURCE`, `TRANSIENT010`, `TRANSIENT020`. A standard point-source analysis uses `evclass=128` (SOURCE) — strict enough that residual cosmic-ray contamination is small, loose enough to keep good photon statistics.

The event-type bitfield encodes orthogonal *partitions* of the same events:

| EVENT_TYPE bit | name | `evtype` value |
|---:|---|----:|
| 0 | FRONT  (thin-converter)         |   1 |
| 1 | BACK   (thick-converter)        |   2 |
| 2 | PSF0   (worst PSF quartile)     |   4 |
| 3 | PSF1                            |   8 |
| 4 | PSF2                            |  16 |
| 5 | PSF3   (best PSF quartile)      |  32 |
| 6 | EDISP0 (worst E-disp quartile)  |  64 |
| 7 | EDISP1                          | 128 |
| 8 | EDISP2                          | 256 |
| 9 | EDISP3 (best E-disp quartile)   | 512 |

Each event has *exactly one* of FRONT/BACK, *exactly one* of PSF0..3, and *exactly one* of EDISP0..3. `evtype = 3` (`= 1|2`) means "FRONT or BACK", i.e. *all* events independent of conversion type. A multi-component PSF analysis (the one fermipy uses by default for PG 1553) splits events into 4 sub-datasets along the PSF partition and fits them jointly with class-specific IRFs.

**FITS bit-packing convention.** When astropy reads a `32X` column it returns an `(N, 32)` boolean array. The most-significant bit of the underlying 32-bit integer is at *array index 0*, so FSSC bit `n` lives at *array index `(31 − n)`*. The cell below packs the bool array back into a single integer per row using `np.packbits` with big-endian byte order, so `mask & 128` is True iff the SOURCE bit is set.
"""),
    ("py", """\
def bits_to_mask(bits32):
    \"\"\"Pack a (N, 32) bool array (FITS 32X) into an N-vector of FSSC bitmasks.

    Bits are stored MSB-first across the 32 bits; FSSC \"bit n\" maps to
    value 2**n in the returned uint32 mask.
    \"\"\"
    return np.packbits(bits32.astype(np.uint8), axis=1).view('>u4').reshape(-1)

evclass_mask = bits_to_mask(events_chunk0["EVENT_CLASS"])
evtype_mask  = bits_to_mask(events_chunk0["EVENT_TYPE"])

print(f"first event:  EVENT_CLASS = 0x{evclass_mask[0]:08x}   "
      f"EVENT_TYPE = 0x{evtype_mask[0]:08x}")

CLASSES = {"TRANSIENT020": 16, "TRANSIENT010": 64, "SOURCE": 128,
           "CLEAN": 256, "ULTRACLEAN": 512, "ULTRACLEANVETO": 1024,
           "SOURCEVETO": 2048, "TRANSIENT015S": 65536}
print("\\nEVENT_CLASS membership (this chunk only):")
for name, val in CLASSES.items():
    n = ((evclass_mask & val) != 0).sum()
    print(f"  {name:18s} (evclass={val:6d}): {n:8,d}  "
          f"({100*n/len(evclass_mask):5.1f} %)")

TYPES = {"FRONT": 1, "BACK": 2,
         "PSF0": 4, "PSF1": 8, "PSF2": 16, "PSF3": 32,
         "EDISP0": 64, "EDISP1": 128, "EDISP2": 256, "EDISP3": 512}
print("\\nEVENT_TYPE membership (this chunk only):")
for name, val in TYPES.items():
    n = ((evtype_mask & val) != 0).sum()
    print(f"  {name:8s} (evtype={val:4d}): {n:8,d}  "
          f"({100*n/len(evtype_mask):5.1f} %)")
"""),
    ("md", """\
**Sanity checks.**

- The four PSF sub-classes partition the dataset exactly: each event has one and only one of PSF0..3 set, so the four percentages should sum to 100 %. Same for EDISP0..3, and FRONT+BACK = 100 %. Verify above.
- The class hierarchy nests: SOURCE ≥ CLEAN ≥ ULTRACLEAN ≥ ULTRACLEANVETO. The numbers shrink as the class becomes stricter.
- TRANSIENT020 ≥ TRANSIENT010 ≥ SOURCE: the transient classes are deliberately looser (more accepted events, more residual background) so they can be used on short flares where every photon counts.
"""),
    ("md", """\
## 3. The FT2 spacecraft file

One row roughly every 30 s, telling you where Fermi was pointing and how good the livetime was. You almost never read it directly — `gtltcube` consumes it to build a livetime cube — but it is good to *see* once.

Documented columns ([FSSC, *Cicerone — LAT Data Columns*](https://fermi.gsfc.nasa.gov/ssc/data/analysis/documentation/Cicerone/Cicerone_Data/LAT_Data_Columns.html)):

| column | unit | FSSC definition |
|---|---|---|
| `START`, `STOP`         | s   | "Mission Elapsed Time of start / end of interval" |
| `RA_SCZ`, `DEC_SCZ`     | deg | "viewing direction at START (RA / Dec of S/C +z axis)" |
| `RA_ZENITH`, `DEC_ZENITH` | deg | "RA / Dec of zenith at START" |
| `LIVETIME`              | s   | "Accumulated livetime of the LAT during the interval from START to STOP" |
| `DATA_QUAL`             | flag | run-level quality flag set by the LAT processing pipeline (values below) |
| `LAT_CONFIG`            | flag | "1 = nominal science configuration, 0 = not recommended for analysis" |
| `IN_SAA`                | bool | "Whether the spacecraft was in the SAA at START" |

`LIVETIME < (STOP − START)` whenever the LAT was paused (SAA passages, calibration, downlinks, target-of-opportunity slews, …); the ratio is what `gtltcube` integrates over the sky to produce the exposure map.
"""),
    ("py", """\
sc_files = sorted(glob(FT2_GLOB))
assert sc_files, f"no FT2 file matching {FT2_GLOB}"
sc_hdul = fits.open(sc_files[0])
sc_hdul.info()

sc = sc_hdul["SC_DATA"].data
print(f"\\nFT2 rows: {len(sc):,}  "
      f"(~{len(sc)*30/86400/365.25:.2f} yr at 30 s/row)")
print("first row:")
for n in ("START", "STOP", "RA_SCZ", "DEC_SCZ", "RA_ZENITH", "DEC_ZENITH",
         "LIVETIME", "DATA_QUAL", "LAT_CONFIG", "IN_SAA"):
    if n in sc.columns.names:
        print(f"  {n:12s} = {sc[n][0]}")

# Livetime fraction over the analysis window.
in_win = (sc['START'] >= 239557417) & (sc['STOP'] <= 271093418)
ontime   = (sc['STOP'][in_win] - sc['START'][in_win]).sum()
livetime = sc['LIVETIME'][in_win].sum()
print(f"\\nover the 1-yr Meyer window (in-window FT2 rows: {in_win.sum():,}):")
print(f"  on-time  Σ(STOP-START) = {ontime:.3e} s = {ontime/86400:.1f} d")
print(f"  livetime Σ(LIVETIME)   = {livetime:.3e} s = {livetime/86400:.1f} d")
print(f"  livetime fraction       = {livetime/ontime*100:.1f} %")
"""),
    ("md", """\
**On-time vs livetime.** The cell prints `Σ(LIVETIME) / Σ(STOP−START) ≈ 90 %` — i.e. *given that the LAT was on*, it accumulated effective livetime ~90 % of the elapsed seconds; the rest is lost mostly to dead-time. But `Σ(STOP−START)` itself is ~303 d out of the 365.25 d wall-clock window — the missing ~60 d is when the LAT was *off* (mostly SAA crossings, ~13 % of the orbit, plus calibration / downlinks). So the wall-clock duty cycle is closer to ~75 %.

## 4. Plot the data-quality flags vs time

Before any analysis, sanity-check that the LAT was actually taking science-quality data over the time range you queried. The two flags that matter:

`DATA_QUAL` — set by the LAT processing pipeline when each run is finalised (FSSC values):

| value | meaning |
|------:|---|
|  1  | good data |
|  2  | GPS timing anomaly (small clock wobble; *still usable* for non-pulsar work) |
|  0  | bad data |
| −1  | solar-flare contamination |
| −2  | particle event |
| −3  | excluded interval (e.g. GRB 221009A) |

`LAT_CONFIG` — 1 means the LAT was in its nominal science configuration; 0 means engineering / commissioning / off-pointed mode.

The recommended GTI filter for a standard SOURCE-class analysis is

```
(DATA_QUAL>0) && (LAT_CONFIG==1)
```

— this keeps both ordinary good data (`DATA_QUAL==1`) and the GPS-flagged but otherwise fine intervals (`DATA_QUAL==2`), and rejects everything ≤ 0 ([FSSC, *Cicerone — Data Preparation*](https://fermi.gsfc.nasa.gov/ssc/data/analysis/documentation/Cicerone/Cicerone_Data_Exploration/Data_preparation.html)).
"""),
    ("py", """\
fig, ax = plt.subplots(figsize=(11, 3))
in_win = (sc['START'] >= 239557417) & (sc['STOP'] <= 271093418)
ax.plot(sc["START"][in_win], sc["DATA_QUAL"][in_win],
        ".", ms=2, label="DATA_QUAL")
ax.plot(sc["START"][in_win], sc["LAT_CONFIG"][in_win],
        ".", ms=2, alpha=0.5, label="LAT_CONFIG")
ax.set_xlabel("MET (s)")
ax.set_ylabel("flag value")
ax.set_ylim(-0.2, 2.2)
ax.set_title("Spacecraft-file quality flags over the 1-yr Meyer window")
ax.legend()
fig.tight_layout()
"""),
    ("md", """\
## 5. Filtering by hand: `gtselect` + `gtmktime`

These are the first two boxes of the FSSC analysis flowchart ([FSSC, *Cicerone — Data Preparation*](https://fermi.gsfc.nasa.gov/ssc/data/analysis/documentation/Cicerone/Cicerone_Data_Exploration/Data_preparation.html)). When fermipy's `gta.setup()` runs them under the hood it uses the parameters from `config.yaml`. Knowing what each parameter does is most of fermipy fluency.

- **`gtselect`** keeps events that pass *event-level* cuts:
  - spatial: `ra`, `dec`, `rad` (acceptance cone, deg),
  - temporal: `tmin`, `tmax` (MET; `INDEF` = use `TSTART`/`TSTOP` from the FT1 header),
  - energy: `emin`, `emax` (MeV),
  - zenith: `zmax` (deg),
  - quality: `evclass`, `evtype` (the bits we just decoded).
- **`gtmktime`** builds Good-Time-Intervals from the FT2 file using a logical
  expression of FT2 keywords and ANDs them into the FT1's `GTI` extension:
  - `filter`: the boolean expression (here `(DATA_QUAL>0) && (LAT_CONFIG==1)`),
  - `roicut="no"`: do *not* cut on the ROI staying inside the LAT FoV (we already did the radial cut in `gtselect`; using `roicut="yes"` would also throw out intervals where the source approached within `zmax` of the limb),
  - `apply_filter="yes"`: actually drop events outside the new GTIs.

**Why `zmax = 90°`?** Photons reconstructed at zenith ≥ 113° are inside the Earth's limb and are dominated by atmospheric γ-ray showers. The FSSC SOURCE-class recommendation, `zmax = 90°`, leaves a comfortable ~23° margin against the limb so that residual atmospheric contamination is negligible without throwing away too much exposure.

**Why `evclass=128, evtype=3`?** SOURCE class is the FSSC-recommended default for point-source analyses (looser than CLEAN — keeps statistics — but strict enough that residual cosmic rays sit well below the source). `evtype=3 = 1|2` means "FRONT or BACK", i.e. *all* events regardless of conversion type. Meyer's PG 1553 setup further splits the SOURCE photons into PSF0..3 components inside fermipy.

**Important quirk.** `gtselect` and `gtmktime` both read parameter defaults from a `.par` file in `$PFILES`. Setting them via `gt_apps` overrides the defaults *and* writes the new values back to that local `.par` for the rest of the session — that is why the FSSC manual warns *"once you have selected a value for a parameter, do not modify it throughout the analysis chain"*: re-running an upstream tool with a different value can leave inconsistent header keywords in downstream files.
"""),
    ("py", """\
# gtselect can take either a single FT1 file or an "@listfile" of paths.
# We have 3 chunks, so build the listfile.
events_txt = ANADIR / "events.txt"
events_txt.write_text("\\n".join(str(p) for p in ft1_files) + "\\n")
print("events.txt:")
print(events_txt.read_text())

import gt_apps                                  # provided by fermitools
from gt_apps import filter as gtselect
gtselect["infile"]  = f"@{events_txt}"
gtselect["outfile"] = str(ANADIR / "PG1553_filtered.fits")
gtselect["ra"]      = 238.929                   # PG 1553+113
gtselect["dec"]     = 11.190
gtselect["rad"]     = 10                        # ROI radius (deg)
gtselect["tmin"]    = "INDEF"                   # use TSTART from FT1
gtselect["tmax"]    = "INDEF"                   # use TSTOP  from FT1
gtselect["emin"]    = 100                       # MeV (Meyer's lower bound)
gtselect["emax"]    = 1000000                   # 1 TeV
gtselect["zmax"]    = 90                        # deg, FSSC recommendation
gtselect["evclass"] = 128                       # SOURCE
gtselect["evtype"]  = 3                         # FRONT + BACK

print("\\ngtselect command:")
print(gtselect.command())
gtselect.run()
"""),
    ("py", """\
from gt_apps import maketime as gtmktime
gtmktime["evfile"]       = str(ANADIR / "PG1553_filtered.fits")
gtmktime["outfile"]      = str(ANADIR / "PG1553_mktime.fits")
gtmktime["scfile"]       = sc_files[0]
gtmktime["filter"]       = "(DATA_QUAL>0) && (LAT_CONFIG==1)"
gtmktime["roicut"]       = "no"
gtmktime["apply_filter"] = "yes"

print("gtmktime command:")
print(gtmktime.command())
gtmktime.run()
"""),
    ("py", """\
# What survived?
flt = fits.open(ANADIR / "PG1553_mktime.fits")
flt.info()

n_in  = sum(fits.open(f)["EVENTS"].header["NAXIS2"] for f in ft1_files)
n_sel = fits.open(ANADIR / "PG1553_filtered.fits")["EVENTS"].header["NAXIS2"]
n_out = flt["EVENTS"].header["NAXIS2"]
print(f"\\ntotal events before                        : {n_in:>9,}")
print(f"events after gtselect (cone+E+zenith+class): {n_sel:>9,}  "
      f"({100*n_sel/n_in:5.1f} %)")
print(f"events after gtmktime (+ DATA_QUAL & LAT_CONFIG GTIs): {n_out:>9,}  "
      f"({100*n_out/n_in:5.1f} %)")
"""),
    ("md", """\
**Why didn't `gtmktime` remove any events?** With this dataset it usually doesn't, because the LAT Data Server already pre-filtered the FT1 chunks before delivering them — the events you got back are already inside `(DATA_QUAL>0) && (LAT_CONFIG==1)` GTIs. What `gtmktime` *does* still do is *refine the GTI extension* (it splits intervals at every flag transition, so the GTI count goes up — see the `5,463 R` in the new GTI extension above). The event count usually only drops when you process FT1 files exported from the *Data Catalog* directly (no server-side filtering), or when you tighten the filter expression beyond what the server applied.

You just executed the first two boxes of the FSSC flowchart by hand. Notebook 01 picks up at the third box (`gtltcube` → `gtbin` → `gtexpcube2` → `gtsrcmaps` → `gtlike`) and lets fermipy stitch all of it together via `GTAnalysis.setup()`.

**Block I done.**
"""),
]

# ---------------------------------------------------------------------------
# 01 — Fermipy PG 1553+113 (Meyer ISAPP 2021)
# ---------------------------------------------------------------------------
nb01 = [
    ("md", """\
# 01 — Likelihood Analysis of a bright point source with fermipy

This notebook follows M. Meyer's PG 1553+113 fermipy hands-on (ISAPP 2021) section by section. The original sample analysis is based on the LAT-team study of PG 1553+113 in [Abdo et al. 2010, ApJ 708, 1310](https://ui.adsabs.harvard.edu/abs/2010ApJ...708.1310A) and closely follows the FSSC [Likelihood Analysis with Python](https://fermi.gsfc.nasa.gov/ssc/data/analysis/scitools/python_tutorial.html) thread. fermipy docs: <https://fermipy.readthedocs.io>.
"""),
    ("md", """\
## Get the Data

For this thread the original data were extracted from the [LAT data server](https://fermi.gsfc.nasa.gov/cgi-bin/ssc/LAT/LATDataQuery.cgi) with the following selections (Meyer's exact query — close to the parameters in Abdo+2010):

* Search Center (RA, Dec) = (238.929, 11.1901)
* Radius = 30°  (we used 20° for our local copy — fermipy uses only what it needs)
* Start Time (MET) = 239 557 417 s   (2008-08-04 15:43:37 UTC)
* Stop Time  (MET) = 256 970 880 s   (2009-02-22 04:48:00 UTC)
* Minimum Energy = 100 MeV
* Maximum Energy = 300 GeV

Our local FT1 / FT2 are already in `data/pg1553/` (you saw them in notebook 00). Meyer's original tutorial unpacked a tarball into a `pg1553/` directory; we use the same convention but pointed at our local path.
"""),
    ("py", """\
import os
from pathlib import Path

# Working directory: same idea as Meyer's `pg1553/`, but our local path.
ANADIR = Path("/Users/mcrnogor/Library/CloudStorage/Dropbox/"
              "lectures/fermipy/lecture/data/pg1553")

# fermipy's config uses $FERMI_DIFFUSE_DIR; the diffuse files ship inside the
# fermipy conda env at this path.
os.environ['FERMI_DIFFUSE_DIR'] = (
    "/Users/mcrnogor/miniconda3/envs/fermipy/share/"
    "fermitools/refdata/fermi/galdiffuse"
)

os.chdir(ANADIR)
print("working in:", os.getcwd())
print("\\ncontents:")
for p in sorted(ANADIR.iterdir()):
    print(f"  {p.name}")
"""),
    ("md", """\
### Make a file list

fermipy needs a text file listing the FT1 chunks (and a similar one for FT2). We already wrote `ft1.txt` and `ft2.txt` into the working directory; let's verify them.
"""),
    ("py", """\
print("=== ft1.txt ===")
print(open("ft1.txt").read())
print("=== ft2.txt ===")
print(open("ft2.txt").read())
"""),
    ("md", """\
## Make a config file

fermipy's analysis is configured through a [yaml](https://yaml.org) file. Ours is the *exact* config Meyer used (cf. `fermipy-extras/data/pg1553/config.yaml`):

* `data.evfile` / `data.scfile`: the FT1 / FT2 listfiles.
* `binning`: 10° ROI side, 0.1°/pixel, 8 bins/decade in energy.
* `selection`: 100 MeV–300 GeV, MET window matches the LAT-server query, `evclass=128` (SOURCE), `evtype=3` (FRONT+BACK), `target='4FGL J1555.7+1111'`.
* `gtlike`: enable energy dispersion (`edisp=True`) with the `P8R3_SOURCE_V3` IRFs.
* `model`: 15° model-source ROI (slightly *larger* than the 10° fit ROI so PSF tails leak in correctly), galactic + isotropic diffuse from `$FERMI_DIFFUSE_DIR`, 4FGL catalog (fermipy 1.4.0 ships up to DR4 — the alias `'4FGL'` resolves to the latest available).

Full config reference: <https://fermipy.readthedocs.io/en/latest/config.html>.
"""),
    ("py", """\
print(open("config.yaml").read())
"""),
    ("md", """\
## Start the analysis

We instantiate `GTAnalysis(config.yaml)`, then run `gta.setup()` which executes the rest of the FSSC analysis chain (`gtselect` → `gtmktime` → `gtltcube` → `gtbin` → `gtexpcube2` → `gtsrcmaps`) and stages every intermediate product under the working directory.

This is where the magic happens: fermipy loads the catalog, builds an XML source model for everything in the ROI, picks all the cuts and binnings, and runs the science tools for you. If files already exist on disk, it skips the corresponding step — so the *first* `gta.setup()` is slow (~15–30 min on a laptop, dominated by `gtltcube` and `gtsrcmaps`); subsequent calls are seconds.
"""),
    ("md", """\
### Load up some useful modules
"""),
    ("py", """\
%matplotlib inline
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
"""),
    ("md", """\
Silence a couple of harmless deprecation warnings emitted by the underlying tools.
"""),
    ("py", """\
import warnings
try:
    from matplotlib import MatplotlibDeprecationWarning
    warnings.filterwarnings("ignore", category=MatplotlibDeprecationWarning)
except ImportError:
    pass
warnings.filterwarnings("ignore", category=FutureWarning)
"""),
    ("md", """\
### Import the GTAnalysis module from fermipy

Constructing the object reads the config and prints every parameter fermipy is going to use — including the many defaults you didn't override. Verbosity 3 = INFO (suppresses DEBUG).
"""),
    ("py", """\
from fermipy.gtanalysis import GTAnalysis
gta = GTAnalysis("config.yaml", logging={"verbosity": 3})
matplotlib.interactive(True)
"""),
    ("md", """\
Let's take a look at the initial input event files,
"""),
    ("py", """\
with open("ft1.txt") as f:
    input_files = [line.strip() for line in f if line.strip()]
print(input_files)
"""),
    ("md", """\
…and read one of them as an `astropy.table.Table` so we can browse the columns interactively.
"""),
    ("py", """\
from astropy.table import Table
t = Table.read(input_files[0], hdu=1)
t
"""),
    ("md", """\
### The setup routine

`gta.setup()` runs every preprocessing step needed before likelihood. fermipy will *skip* any ancillary file that already exists — so re-running this cell after an interrupt is safe.

⏱ **First-run cost.** On Meyer's 6.5-month window expect ~15–30 min; the bottlenecks are `gtltcube` (livetime cube, all-sky × cos θ × time) and `gtsrcmaps` (one model map per source in the ROI, convolved with PSF and exposure). Re-runs that find the cached `*_00.fits` files complete in seconds.
"""),
    ("py", """\
gta.setup()
"""),
    ("md", """\
Before proceeding we have a quick look at what fermipy produced.
"""),
    ("py", """\
import glob
for f in sorted(glob.glob("*.fits")):
    print(f)
"""),
    ("md", """\
Brief explanation of the contents of each file and its role in the analysis (verbatim from Meyer):

* **`ft1_00.fits`** — Event list. Generated by running `gtselect` and `gtmktime` on our input file list.
* **`bexpmap_00.fits`** — All-sky binned exposure map. Interpolated to create the exposure model when generating the source-map file.
* **`bexpmap_roi_00.fits`** — Binned exposure map *for the ROI*. Provided for visualisation (same binning as data and model maps).
* **`ccube_00.fits`** — Counts cube for the ROI (energy × lon × lat).
* **`ltcube_00.fits`** — Livetime cube. Map of the livetime over the whole sky as a function of incidence angle.
* **`srcmap_00.fits`** — Source-map cube. One map per ROI component, after convolution with exposure and PSF. (Energy dispersion is applied at run-time.)

The `_00` suffix is the analysis-component index — a multi-component analysis would have `_00`, `_01`, …, plus co-added maps without an index for visualisation.

To see one of these, open the counts cube and sum it over energy to make a 2-D sky image.
"""),
    ("py", """\
from astropy.io import fits
from astropy.wcs import WCS

h = fits.open('ccube.fits')
h.info()

wcs = WCS(h[0].header).dropaxis(-1)   # drop the energy axis for plotting

counts = h[0].data
plt.subplot(projection=wcs)
im = plt.imshow(np.sum(counts, axis=0), interpolation='nearest',
                origin='lower', cmap='plasma')
plt.colorbar(im, label="counts")
plt.grid()
plt.gca().tick_params(direction='out')
plt.gca().set_xlabel("R.A. (deg)")
plt.gca().set_ylabel("Dec. (deg)")
"""),
    ("md", """\
Next, the sky map of the exposure for the ROI:
"""),
    ("py", """\
exp = fits.open('bexpmap_roi_00.fits')
exp.info()
exposure = exp[0].data
wcs = WCS(exp[0].header).dropaxis(-1)

plt.subplot(projection=wcs)
im = plt.imshow(np.sum(exposure, axis=0), interpolation='nearest',
                origin='lower', cmap='plasma')
plt.colorbar(im, label=r"Exposure (cm$^{2}$ s)")
plt.grid()
plt.gca().tick_params(direction='out')
plt.gca().set_xlabel("R.A. (deg)")
plt.gca().set_ylabel("Dec. (deg)")
"""),
    ("md", """\
…and the energy dependence of the exposure for the central pixel.
"""),
    ("py", """\
energy = exp[1].data
plt.loglog(energy, exposure[:, 50, 50])
plt.ylabel(r"Exposure (cm$^{2}$ s)")
plt.xlabel("Energy (MeV)")
plt.grid()
"""),
    ("md", """\
We can now inspect the state of the ROI prior to fitting with the `print_roi()` method.
"""),
    ("py", """\
gta.print_roi()
"""),
    ("md", """\
Additional details about an individual source can be retrieved by printing the corresponding source object — here PG 1553+113.
"""),
    ("py", """\
print(gta.roi['4FGL J1555.7+1111'])
"""),
    ("md", """\
## Do the likelihood fitting

Now that all of the ancillary files have been generated, we can move on to the actual fitting. The first thing you should do is free some of the sources, since they are all initially fixed. We free those near the centre of the ROI.
"""),
    ("py", """\
gta.free_sources(free=False)                  # make sure everything is fixed first

# Free Normalization of all Sources within 3 deg of ROI center
gta.free_sources(distance=3.0, pars='norm')

# Free normalizations of isotropic and galactic diffuse components
gta.free_source('galdiff', pars='norm')
gta.free_source('isodiff')
"""),
    ("md", """\
In this simple analysis we leave the spectral *shapes* of nearby sources fixed but free the full spectral shape of our target.
"""),
    ("py", """\
gta.free_source('4FGL J1555.7+1111')
"""),
    ("md", """\
Now actually run the fit. fermipy retries internally to coax the fitter into convergence.
"""),
    ("py", """\
fit_results = gta.fit()
"""),
    ("md", """\
The dictionary returned by `fit()` carries diagnostics: the fit quality, the relative likelihood improvement, parameter correlations. Inspect the post-fit source object for PG 1553.
"""),
    ("py", """\
print('Fit Quality:', fit_results['fit_quality'])
print(gta.roi['4FGL J1555.7+1111'])
"""),
    ("md", """\
And take another look at the ROI table and the full parameter list after the fit:
"""),
    ("py", """\
gta.print_roi()
"""),
    ("py", """\
gta.print_params()
"""),
    ("md", """\
You can save the state of the ROI to disk for later inspection. The first argument prefixes the output files; `make_plots=True` writes a stack of PNG diagnostics.
"""),
    ("py", """\
gta.write_roi('fit0', make_plots=True)
"""),
    ("md", """\
We can also produce the *model map* (predicted counts per pixel under the best-fit model) and load it as a `gammapy.Map` (gammapy is a Cherenkov-telescope analysis package whose multi-dimensional Map class is convenient for this kind of cube; docs: <https://docs.gammapy.org>).
"""),
    ("py", """\
model_map = gta.write_model_map("fit0")
"""),
    ("py", """\
print(model_map)
"""),
    ("md", """\
Plot the model map summed over the energy axis — predicted counts for *all* model components combined:
"""),
    ("py", """\
model_map[0].sum_over_axes(["energy"]).plot(stretch='log', add_cbar=True)
"""),
    ("md", """\
Plot each energy bin of the model map. This nicely illustrates the broad PSF at low energies (the source blob is degrees-wide at 100 MeV and shrinks to ≲ 0.1° at 100 GeV).
"""),
    ("py", """\
_ = model_map[0].plot_grid(stretch='log', add_cbar=True)
"""),
    ("md", """\
There are also several diagnostic plots `write_roi` saved to disk — counts map, x/y projections, counts spectrum, model map. Display them inline.
"""),
    ("py", """\
from IPython.display import Image, display
pngs = sorted(glob.glob("fit0_*.png"))
for p in pngs:
    print(p)
    display(Image(p))
"""),
    ("md", """\
### Reading in the results

Since the results are pickled, you can reload them at any time. The on-disk numpy file mirrors the live `gta.roi` dictionary.
"""),
    ("py", """\
c = np.load('fit0.npy', allow_pickle=True).flat[0]
"""),
    ("md", """\
The `sources` dictionary has an entry for each source in the model:
"""),
    ("py", """\
sorted(c['sources'].keys())
"""),
    ("md", """\
And we can pull the flux, spectral parameters, and TS:
"""),
    ("py", """\
print("flux        :", c['sources']['4FGL J1555.7+1111']['flux'])
print("param_names :", c['sources']['4FGL J1555.7+1111']['param_names'][:4])
print("param_values:", c['sources']['4FGL J1555.7+1111']['param_values'][:4])
print("TS          :", c['sources']['4FGL J1555.7+1111']['ts'])
"""),
    ("md", """\
The best-fit model SED is also stored in the `model_flux` sub-dictionary. Plot it.
"""),
    ("py", """\
E       = np.array(c['sources']['4FGL J1555.7+1111']['model_flux']['energies'])
dnde    = np.array(c['sources']['4FGL J1555.7+1111']['model_flux']['dnde'])
dnde_hi = np.array(c['sources']['4FGL J1555.7+1111']['model_flux']['dnde_hi'])
dnde_lo = np.array(c['sources']['4FGL J1555.7+1111']['model_flux']['dnde_lo'])

plt.loglog(E, (E**2)*dnde,    'k--')
plt.loglog(E, (E**2)*dnde_hi, 'k')
plt.loglog(E, (E**2)*dnde_lo, 'k')
plt.xlabel('E [MeV]')
plt.ylabel(r'E$^2$ dN/dE [MeV cm$^{-2}$ s$^{-1}$]')
plt.show()
"""),
    ("md", """\
If you want SED *points* (binned likelihood per energy bin, with everything but the bin's normalisation frozen), there's `gta.sed`. Many options can be set in the config file or as keyword arguments — see [`fermipy.gtanalysis.GTAnalysis.sed`](https://fermipy.readthedocs.io/en/latest/fermipy.html#fermipy.gtanalysis.GTAnalysis.sed).
"""),
    ("py", """\
sed = gta.sed('4FGL J1555.7+1111')
"""),
    ("md", """\
You can save the state to a yaml file or just access it directly. This is also the way to get at the dictionary for any individual source.
"""),
    ("py", """\
src = gta.roi['4FGL J1555.7+1111']
"""),
    ("md", """\
Plot the SED points on top of the best-fit model band.
"""),
    ("py", """\
plt.loglog(E, (E**2)*dnde,    'k--')
plt.loglog(E, (E**2)*dnde_hi, 'k')
plt.loglog(E, (E**2)*dnde_lo, 'k')
plt.errorbar(np.array(sed['e_ctr']),
             sed['e2dnde'],
             yerr=sed['e2dnde_err'], fmt='o')
plt.xlabel('E [MeV]')
plt.ylabel(r'E$^{2}$ dN/dE [MeV cm$^{-2}$ s$^{-1}$]')
plt.show()
"""),
    ("md", """\
Looks like the last two points should be upper limits — they're noisy because PG 1553+113 is faint above ~30 GeV in 6.5 months. Replace them with proper 95 % upper limits (`e2dnde_ul95`, drawn as down-arrows).
"""),
    ("py", """\
plt.loglog(E, (E**2)*dnde,    'k--')
plt.loglog(E, (E**2)*dnde_hi, 'k')
plt.loglog(E, (E**2)*dnde_lo, 'k')
plt.errorbar(sed['e_ctr'][:-2],
             sed['e2dnde'][:-2],
             yerr=sed['e2dnde_err'][:-2], fmt='o')
plt.errorbar(np.array(sed['e_ctr'][-2:]),
             sed['e2dnde_ul95'][-2:],
             yerr=0.2*sed['e2dnde_ul95'][-2:],
             fmt='o', uplims=True)
plt.xlabel('E [MeV]')
plt.ylabel(r'E$^{2}$ dN/dE [MeV cm$^{-2}$ s$^{-1}$]')
plt.show()
"""),
    ("md", """\
### Summary

There is much more functionality (TS maps, extension tests, event-type splitting, light-curves, …); see the fermipy docs and the rest of `fermipy-extras/notebooks/`. For PG 1553 specifically, the *Going further* options Meyer suggests:

- Re-run with `tmax: 'INDEF'` to use the full mission and reproduce the ~2.2-yr quasi-periodic flux modulation (Ackermann+ 2015, ApJL 813 L41) via `gta.lightcurve(...)` with monthly binning.
- Add an EBL absorption model on top of the intrinsic spectrum.

Next: the same machinery on a *less* clean and time-variable source — **TXS 0506+056**.
"""),
]

# ---------------------------------------------------------------------------
# 02 — Fermipy TXS 0506+056
# ---------------------------------------------------------------------------
nb02 = [
    ("md", """\
# 02 — Fermipy on TXS 0506+056 (the neutrino blazar)

**Goal (~25 min).** Same machinery as notebook 01, applied to a science-driven analysis.

- Source: 4FGL J0509.4+0541 (TXS 0506+056), z=0.3365 BL Lac.
- Trigger: IceCube-170922A (290 TeV neutrino, 2017-09-22).
- We reproduce a *qualitative* version of IceCube + Fermi-LAT + MAGIC, *Science* 361, 6398 (2018):
  * detection,
  * SED in the alert period,
  * monthly lightcurve showing the LAT flare.

Adapted from the Black Hole Group fermipy tutorial (Cafardo, Nemmen, de Menezes; CC-BY).
"""),
    ("py", """\
%matplotlib inline
import os, numpy as np, matplotlib.pyplot as plt
from IPython.display import Image, display
from glob import glob

ANADIR = "/data/blazar"
os.chdir(ANADIR)
print("config:")
print(open("config.yaml").read())
"""),
    ("py", """\
from fermipy.gtanalysis import GTAnalysis
gta = GTAnalysis("config.yaml", logging={"verbosity": 3})
gta.setup()
gta.print_roi()
print(gta.roi["4FGL J0509.4+0541"])   # TXS 0506+056 in 4FGL-DR3
"""),
    ("md", """\
## Fit
"""),
    ("py", """\
gta.free_sources(False)
gta.free_sources(distance=3.0, pars="norm")
gta.free_source("galdiff");  gta.free_source("isodiff")
gta.free_source("4FGL J0509.4+0541")
fit = gta.fit()
print("fit_quality:", fit["fit_quality"])
print(gta.roi["4FGL J0509.4+0541"])
gta.write_roi("fit_txs", make_plots=True)
"""),
    ("md", """\
## SED
"""),
    ("py", """\
sed = gta.sed("4FGL J0509.4+0541", loge_bins=8, make_plots=True)
e = sed["e_ctr"]; e2 = e**2 * sed["dnde"]; e2err = e**2 * sed["dnde_err"]
e2ul = e**2 * sed["dnde_ul95"]; det = sed["ts"] >= 4
fig, ax = plt.subplots(figsize=(7,5))
ax.errorbar(e[det], e2[det], yerr=e2err[det], fmt="o", label="TXS 0506+056")
ax.errorbar(e[~det], e2ul[~det], yerr=0.3*e2ul[~det], uplims=True, fmt="v", alpha=0.5)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("E (MeV)"); ax.set_ylabel(r"$E^2 dN/dE$ (MeV cm$^{-2}$ s$^{-1}$)")
ax.legend(); ax.set_title("TXS 0506+056, Fermi-LAT — alert window")
fig.tight_layout()
"""),
    ("md", """\
## Lightcurve around IC-170922A

Build a 30-day-binned LAT lightcurve, with bin 13 covering the IceCube alert.
"""),
    ("py", """\
binsize_days = 30.0
tneutrino = 527806475.4   # MET seconds for 2017-09-22T20:54:30 UTC (IC-170922A)
n_before, n_after = 13, 6
edges = tneutrino + (np.arange(-n_before, n_after) * binsize_days * 86400.)
time_bins = np.column_stack([edges[:-1], edges[1:]])

lc = gta.lightcurve("4FGL J0509.4+0541",
                    free_params=["Prefactor"],
                    time_bins=time_bins)
"""),
    ("py", """\
tmean = (lc["tmin"] + lc["tmax"])/2.
fig, ax = plt.subplots(figsize=(8,4))
ax.errorbar(tmean, lc["flux"], yerr=lc["flux_err"],
            xerr=binsize_days*86400/2, fmt="o", color="C0", label="LAT 30-d bins")
ax.axvline(tneutrino, color="C3", ls="--", label="IC-170922A")
ax.set_xlabel("MET (s)")
ax.set_ylabel(r"Flux (>100 MeV) (cm$^{-2}$ s$^{-1}$)")
ax.set_title("TXS 0506+056 monthly lightcurve")
ax.legend()
fig.tight_layout()
"""),
    ("md", """\
The bin centred on 2017-09-22 sits well above the catalog mean — the same flare reported in IceCube et al. 2018.

That is what fermipy is for. From here, real science: harder time binning around the alert, fits for variability time-scale, multiwavelength SED modelling (which we will do next, in **gammapy**).
"""),
]

# ---------------------------------------------------------------------------
# 03 — Gammapy
# ---------------------------------------------------------------------------
nb03 = [
    ("md", """\
# 03 — Same data in Gammapy, joint multi-instrument fits

**Goal (~20 min).**
1. Load the *same* Fermi-LAT counts, exposure, PSF, and EDISP we just built (or the public 3FHL Galactic-centre tutorial files) into Gammapy's `MapDataset`.
2. Fit a point source — show that the likelihood is the same machinery as fermipy's.
3. Sketch how a **joint** fit with H.E.S.S. / CTA / HAWC works in code.

This is closely adapted from the official *Fermi-LAT with Gammapy* tutorial.
"""),
    ("py", """\
%matplotlib inline
import os
import numpy as np
import matplotlib.pyplot as plt
from astropy import units as u
from astropy.coordinates import SkyCoord

from gammapy.data import EventList
from gammapy.datasets import Datasets, MapDataset
from gammapy.irf import EDispKernelMap, PSFMap
from gammapy.maps import Map, MapAxis, WcsGeom
from gammapy.modeling import Fit
from gammapy.modeling.models import (
    Models, PointSpatialModel, PowerLawNormSpectralModel,
    PowerLawSpectralModel, SkyModel, TemplateSpatialModel,
    create_fermi_isotropic_diffuse_model,
)
"""),
    ("md", """\
## 1. Load Fermi 3FHL prepared data (10 GeV — 2 TeV, GC region)

These files are produced by the same Fermi Science Tools (`gtbin`, `gtexpcube2`, `gtpsf`) we used for fermipy. Gammapy reads them directly.
"""),
    ("py", """\
events = EventList.read("$GAMMAPY_DATA/fermi_3fhl/fermi_3fhl_events_selected.fits.gz")
print(events)
"""),
    ("py", """\
gc_pos = SkyCoord(0, 0, unit="deg", frame="galactic")
energy_axis = MapAxis.from_edges([1e4, 3e4, 1e5, 3e5, 2e6],
                                 name="energy", unit="MeV", interp="log")
counts = Map.create(skydir=gc_pos, npix=(100, 80), proj="TAN",
                    frame="galactic", binsz=0.1, axes=[energy_axis], dtype=float)
counts.fill_events(events)
plt.figure(); counts.sum_over_axes().smooth(2).plot(stretch="sqrt", vmax=30)
"""),
    ("py", """\
exposure_hpx = Map.read("$GAMMAPY_DATA/fermi_3fhl/fermi_3fhl_exposure_cube_hpx.fits.gz")
e_true = MapAxis.from_energy_bounds("10 GeV", "2 TeV", nbin=10,
                                    per_decade=True, name="energy_true")
geom_true = WcsGeom(wcs=counts.geom.wcs, npix=counts.geom.npix, axes=[e_true])
exposure  = exposure_hpx.interp_to_geom(geom_true)
"""),
    ("py", """\
psf   = PSFMap.read("$GAMMAPY_DATA/fermi_3fhl/fermi_3fhl_psf_gc.fits.gz", format="gtpsf")
edisp = EDispKernelMap.from_diagonal_response(energy_axis_true=e_true,
                                              energy_axis=energy_axis)

template_diffuse = TemplateSpatialModel.read(
    "$GAMMAPY_DATA/fermi-3fhl-gc/gll_iem_v06_gc.fits.gz", normalize=False)
diffuse_iem = SkyModel(spectral_model=PowerLawNormSpectralModel(),
                       spatial_model=template_diffuse, name="diffuse-iem")
diffuse_iso = create_fermi_isotropic_diffuse_model(
    "$GAMMAPY_DATA/fermi_3fhl/iso_P8R2_SOURCE_V6_v06.txt",
    interp_kwargs={"fill_value": None})
"""),
    ("md", """\
## 2. Define a sky model and fit
"""),
    ("py", """\
source = SkyModel(
    spectral_model=PowerLawSpectralModel(index=2.7,
                                         amplitude="5.8e-10 cm-2 s-1 TeV-1",
                                         reference="100 GeV"),
    spatial_model =PointSpatialModel(lon_0="0 deg", lat_0="0 deg", frame="galactic"),
    name="source-gc")

dataset = MapDataset(models=Models([source, diffuse_iem, diffuse_iso]),
                     counts=counts, exposure=exposure, psf=psf, edisp=edisp,
                     name="fermi-gc")

result = Fit().run(datasets=[dataset])
print(result)
print(dataset.models)
"""),
    ("py", """\
residual = counts - dataset.npred()
plt.figure()
residual.sum_over_axes().smooth("0.1 deg").plot(cmap="coolwarm", vmin=-3, vmax=3, add_cbar=True)
plt.title("Fermi 3FHL GC — residual (counts − model)")
"""),
    ("md", """\
This is the *same* forward-folded Poisson-likelihood machinery as fermipy. We just spelled the model out in Gammapy's grammar and used Gammapy's optimiser.

## 3. Joint multi-instrument fit — the punchline

The reason to learn Gammapy is this:
"""),
    ("py", """\
# Pseudo-code: do not run unless you have the IACT files locally.
#
# from gammapy.datasets import SpectrumDatasetOnOff
#
# ds_lat  = dataset                                     # what we just built
# ds_hess = SpectrumDatasetOnOff.read("hess_pks2155.fits.gz")
# ds_cta  = MapDataset.read("cta_simulated.fits.gz")
#
# joint_source = SkyModel(spectral_model=LogParabolaSpectralModel(...),
#                         spatial_model=PointSpatialModel(...),
#                         name="PKS 2155-304")
# for d in (ds_lat, ds_hess, ds_cta):
#     d.models = [joint_source, *d.background_models]
#
# joint = Fit().run([ds_lat, ds_hess, ds_cta])
# # one likelihood, three instruments, one set of source parameters
"""),
    ("md", """\
**Internally**

$$
\\ln\\mathcal{L}_\\text{tot}(\\boldsymbol{\\theta}) \\;=\\; \\sum_{d\\in\\{\\text{LAT, HESS, CTA}\\}} \\ln \\mathcal{L}_d(\\boldsymbol{\\theta})
$$

with $\\boldsymbol{\\theta}$ the *single* set of parameters of `joint_source` — TS, errors, contours all come out of `joint`.

**That is the whole point.** From a fermipy-only world, this is the upgrade.

## Exercises (homework)

1. Replace the GC source above with a fit at the position of TXS 0506+056 using your fermipy-prepared `ccube`, `bexpmap`, and `psf` files (Notebook 02 produces them). Compare the index and flux to fermipy's.
2. Run `gta.localize("4FGL J0509.4+0541")` in fermipy and Gammapy's `gammapy.estimators.PositionEstimator` on the same data. Are the 1σ contours consistent?
3. Pick a TeV blazar with a public H.E.S.S. SED point list (e.g. Mrk 421) and do a joint Fermi-LAT + H.E.S.S. log-parabola fit.
"""),
]

write("00_data_levels.ipynb", nb00)
write("01_fermipy_pg1553.ipynb", nb01)
write("02_fermipy_txs0506.ipynb", nb02)
write("03_gammapy_joint.ipynb", nb03)
print("done.")
