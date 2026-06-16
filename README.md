# Octave panel bed files & synthesis QC

Reproducible pipeline that converts the three Octave "chip" probe-sequence
tables into per-panel probe/target BED files matching the original Kyudo2
layout, and confirms the probe arrangements requested in the 4/1 design thread.

## Directory layout
```
octave-panels/
├── README.md
├── environment.yml          # pinned conda env (python 3.11 + pytest)
├── pytest.ini
├── data/
│   └── chips/               # inputs: the three probe-sequence tables (as delivered)
├── docs/                    # source correspondence
│   ├── design-tradeoffs.md
│   └── request-from-matt.md
├── scripts/                 # pipeline
│   ├── reflib.py            # paths/config + indexed-FASTA reader
│   ├── build_dict.py        # -> results/dict.tsv
│   ├── process.py           # -> results/Chip_{1,2,3}/*
│   └── qc.py                # -> results/synthesis_qc_report.{md,tsv}
├── tests/                   # pytest suite (70 tests)
├── results/                 # generated deliverables (large dict.tsv git-ignored)
└── env/                     # local conda env (git-ignored)
```

## Inputs
- `data/chips/All 200 panel sequences_Chip_{1,2,3} 1.txt` — `(Panel, Probe, Seq-wo-flank)`.
- Original coordinates: `/mnt/archive/work/lren/projects/xGen/POTA/Design_200_Panels/Kyudo2_Panel_Files`.
- Reference: hg38p2 (`/mnt/archive/data/genomeLinks/hg38p2/hg38p2_primary.fa`).

All external paths are defined in `scripts/reflib.py`.

## How probes get coordinates
Each probe `Seq-wo-flank` matches hg38p2 exactly (identity 1.0, reverse-
complemented for `-` strand). A `sequence -> coordinate` dictionary
(`results/dict.tsv`) is built directly from the reference at the original
probe intervals; target/hotspot coordinates are carried verbatim from the
original `Target.bed` files (the hotspot is off-centre by 1–118 bp).

## Reproducible environment
Project-local conda env, pinned in `environment.yml`:

```bash
export MAMBA_ROOT_PREFIX=/mnt/archive/work/skyhl/micromamba
micromamba create -y -p ./env -f environment.yml
```

## Run the pipeline
```bash
./env/bin/python scripts/build_dict.py   # -> results/dict.tsv
./env/bin/python scripts/process.py      # -> results/Chip_{1,2,3}/*
./env/bin/python scripts/qc.py           # -> results/synthesis_qc_report.{md,tsv}
```

## Run the tests
```bash
./env/bin/pytest
```
70 tests validate every deliverable: bed structure/format, that Chip 1/2 beds
are byte-identical to the (shifted) originals, the Chip 3 scramble is a complete
unique re-assignment, controls are intact, no extra probes were synthesized, and
the QC report is all-PASS.

## Outputs (`results/`)
- `Chip_{1,2,3}/` — 200x `*_Probe.bed` + 200x `*_Target.bed` + `ALL_Probe.bed`
  + `panel_mapping.tsv` (chip panel <-> original panel identity).
- `dict.tsv`, `synthesis_qc_report.md`, `synthesis_qc_report.tsv`.
