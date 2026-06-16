"""Shared fixtures, constants and path helpers for the deliverable test suite.

All filesystem locations are imported from ``scripts/reflib.py`` so the tests
and the pipeline always agree on where inputs and outputs live.
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
sys.path.insert(0, SCRIPTS)

import reflib  # noqa: E402

BED = reflib.RESULTS
KYUDO = reflib.KYUDO
CHIP_FILES = reflib.CHIP_FILES

PROBES_PER_PANEL = {1: 1490, 2: 1485, 3: 1500}
DROP_PER_PANEL = {1: 10, 2: 15, 3: 0}      # vs original 1500
N_PANELS = 200
N_CONTROLS = 15
ORIG_PER_PANEL = 1500
ALL_CHIPS = (1, 2, 3)


def chip2_orig_panel(k):
    """Return the original panel number that Chip-2 panel ``k`` is built from.

    Chip 2 shifts the panels by 10 (the last 10 panels become the first 10),
    so chip panel ``k`` corresponds to original panel ``((k + 189) % 200) + 1``.
    """
    return ((k + 189) % 200) + 1


def panel_name(num):
    """Format a panel number as its ``PanelNNN`` label."""
    return "Panel%03d" % num


def panel_probe_bed(chip, num):
    """Path to the emitted per-panel Probe.bed for ``chip``/``num``."""
    return os.path.join(reflib.chip_dir(chip),
                        "Octave_Hotspot_Panel_120bp_%03d_Probe.bed" % num)


def panel_target_bed(chip, num):
    """Path to the emitted per-panel Target.bed for ``chip``/``num``."""
    return os.path.join(reflib.chip_dir(chip),
                        "Octave_Hotspot_Panel_120bp_%03d_Target.bed" % num)


def all_probe_bed(chip):
    """Path to the combined ALL_Probe.bed for ``chip``."""
    return os.path.join(reflib.chip_dir(chip),
                        "Octave_Hotspot_Panel_120bp_ALL_Probe.bed")


def orig_probe_bed(num):
    """Path to the original Kyudo2 Probe.bed for panel ``num``."""
    return reflib.orig_probe_bed(num)


def orig_target_bed(num):
    """Path to the original Kyudo2 Target.bed for panel ``num``."""
    return reflib.orig_target_bed(num)


def read_lines(path):
    """Read a file into a list of newline-stripped, non-blank lines."""
    with open(path) as fh:
        return [ln.rstrip("\n") for ln in fh if ln.strip()]


@pytest.fixture(scope="session")
def dict_rows():
    """Parse ``results/dict.tsv`` into a list of column->value dicts."""
    path = os.path.join(BED, "dict.tsv")
    rows = []
    with open(path) as fh:
        header = fh.readline().rstrip("\n").split("\t")
        for line in fh:
            rows.append(dict(zip(header, line.rstrip("\n").split("\t"))))
    return rows


@pytest.fixture(scope="session")
def original_coords():
    """Set of every original probe coordinate string across the 200 panels.

    Each element is ``"chrom\\tstart\\tend\\tstrand"`` (deduplicated), giving the
    ground-truth universe of probes that any chip is allowed to draw from.
    """
    coords = set()
    for num in range(1, N_PANELS + 1):
        for ln in read_lines(orig_probe_bed(num)):
            f = ln.split("\t")
            coords.add("\t".join(f[:4]))
    return coords
