"""Confirm the three chip arrangements against the original Kyudo2 bed files.

These tests encode Matt's 4/1 set descriptions:
  Chip 1: original design & order, minus the last 10 probes per panel.
  Chip 2: Chip 1 minus 5 more (last 15 dropped), panels shifted by 10.
  Chip 3: full original set, probes scrambled across panels (controls intact).
And the 6/15 ask: confirm no extra probes were synthesized.
"""
import pytest

import conftest as C


# ----- Chip 1: original minus last 10 per panel --------------------------

@pytest.mark.parametrize("num", [1, 2, 50, 100, 191, 200])
def test_chip1_probe_bed_matches_original_first_1490(num):
    """Chip 1 Probe.bed is byte-identical to the first 1490 rows of the
    original Kyudo2 panel (original design & order, last 10 dropped)."""
    orig = C.read_lines(C.orig_probe_bed(num))[:C.PROBES_PER_PANEL[1]]
    got = C.read_lines(C.panel_probe_bed(1, num))
    assert got == orig


@pytest.mark.parametrize("num", [1, 2, 50, 100, 191, 200])
def test_chip1_target_bed_matches_original_first_1490(num):
    """Chip 1 Target.bed is byte-identical to the first 1490 rows of the
    original panel's Target.bed (hotspots carried through unchanged)."""
    orig = C.read_lines(C.orig_target_bed(num))[:C.PROBES_PER_PANEL[1]]
    got = C.read_lines(C.panel_target_bed(1, num))
    assert got == orig


def test_chip1_drops_exactly_last_10():
    """Chip 1 removes exactly the last 10 probes (original indices 1491-1500)
    of each panel and keeps the remaining 1490 in order."""
    for num in (1, 100, 200):
        orig = C.read_lines(C.orig_probe_bed(num))
        got = C.read_lines(C.panel_probe_bed(1, num))
        assert got == orig[:C.ORIG_PER_PANEL - C.DROP_PER_PANEL[1]]
        assert len(orig) - len(got) == 10


# ----- Chip 2: Chip 1 minus 5 more, panels shifted by 10 -----------------

@pytest.mark.parametrize("num", [1, 2, 11, 100, 200])
def test_chip2_probe_bed_matches_shifted_original_first_1485(num):
    """Chip 2 Probe.bed equals the first 1485 rows of the shifted original
    panel (panels moved by 10, so chip panel k uses original panel k+190)."""
    src = C.chip2_orig_panel(num)
    orig = C.read_lines(C.orig_probe_bed(src))[:C.PROBES_PER_PANEL[2]]
    got = C.read_lines(C.panel_probe_bed(2, num))
    assert got == orig, "chip2 panel %d should be original panel %d" % (
        num, src)


@pytest.mark.parametrize("num", [1, 2, 11, 100, 200])
def test_chip2_target_bed_matches_shifted_original_first_1485(num):
    """Chip 2 Target.bed equals the first 1485 rows of the shifted original
    panel's Target.bed (consistent with the probe shift)."""
    src = C.chip2_orig_panel(num)
    orig = C.read_lines(C.orig_target_bed(src))[:C.PROBES_PER_PANEL[2]]
    got = C.read_lines(C.panel_target_bed(2, num))
    assert got == orig


def test_chip2_shift_mapping_examples():
    """The 10-panel shift maps the last 10 panels to the first 10:
    chip P001<-orig P191, chip P011<-orig P001, chip P200<-orig P190."""
    assert C.chip2_orig_panel(1) == 191
    assert C.chip2_orig_panel(11) == 1
    assert C.chip2_orig_panel(200) == 190


def test_chip2_is_chip1_minus_5_more():
    """Chip 2 (1485 probes) is a strict prefix of the corresponding Chip 1
    panel (1490 probes), i.e. Chip 1 with 5 additional probes removed."""
    for num in (1, 11, 100, 200):
        src = C.chip2_orig_panel(num)
        chip1 = C.read_lines(C.panel_probe_bed(1, src))
        chip2 = C.read_lines(C.panel_probe_bed(2, num))
        assert chip2 == chip1[:C.PROBES_PER_PANEL[2]]
        assert len(chip1) - len(chip2) == 5


# ----- Chip 3: full original set scrambled across panels -----------------

def test_chip3_full_1500_per_panel():
    """Chip 3 keeps the full 1500 probes per panel (no probes dropped)."""
    for num in (1, 100, 200):
        assert len(C.read_lines(C.panel_probe_bed(3, num))) == C.ORIG_PER_PANEL


def test_chip3_is_full_original_probe_set(original_coords):
    """Every original probe coordinate appears exactly once across all of
    Chip 3 (controls excepted, which repeat once per panel)."""
    from collections import Counter
    counts = Counter()
    for num in range(1, C.N_PANELS + 1):
        for ln in C.read_lines(C.panel_probe_bed(3, num)):
            counts["\t".join(ln.split("\t")[:4])] += 1
    # control coords: first 15 of any panel, identical everywhere
    controls = set()
    for ln in C.read_lines(C.panel_probe_bed(3, 1))[:C.N_CONTROLS]:
        controls.add("\t".join(ln.split("\t")[:4]))
    noncontrol = {c: n for c, n in counts.items() if c not in controls}
    # all coords are real original coords
    assert set(counts) <= original_coords
    # every non-control original probe present exactly once
    orig_noncontrol = original_coords - controls
    assert set(noncontrol) == orig_noncontrol
    assert all(n == 1 for n in noncontrol.values())
    # each control appears once per panel
    for c in controls:
        assert counts[c] == C.N_PANELS


def test_chip3_noncontrol_unique_across_panels():
    """No non-control probe coordinate appears in more than one panel."""
    seen = {}
    controls = set("\t".join(ln.split("\t")[:4])
                   for ln in C.read_lines(
                       C.panel_probe_bed(3, 1))[:C.N_CONTROLS])
    for num in range(1, C.N_PANELS + 1):
        for ln in C.read_lines(C.panel_probe_bed(3, num)):
            coord = "\t".join(ln.split("\t")[:4])
            if coord in controls:
                continue
            assert coord not in seen, \
                "non-control probe in panels %s and %d" % (seen.get(coord), num)
            seen[coord] = num


def test_chip3_actually_scrambled():
    """Chip 3 panel 1 is not simply original panel 1 (probes reassigned)."""
    orig1 = C.read_lines(C.orig_probe_bed(1))[C.N_CONTROLS:]
    chip3_1 = C.read_lines(C.panel_probe_bed(3, 1))[C.N_CONTROLS:]
    assert chip3_1 != orig1


# ----- No extra probes (all chips) ---------------------------------------

@pytest.mark.parametrize("chip", C.ALL_CHIPS)
def test_no_extra_probes(chip, original_coords):
    """Every probe coordinate emitted for every chip exists in the original
    300k-probe set -- i.e. nothing extra/novel was synthesized."""
    for ln in C.read_lines(C.all_probe_bed(chip)):
        coord = "\t".join(ln.split("\t")[:4])
        assert coord in original_coords, "extra probe in chip %d: %r" % (
            chip, coord)


# ----- Control probes -----------------------------------------------------

def test_controls_identical_across_all_panels_and_chips():
    """First 15 Probe.bed lines are byte-identical across every panel and
    every chip (the universal/control probes, unscrambled)."""
    ref = C.read_lines(C.panel_probe_bed(1, 1))[:C.N_CONTROLS]
    assert len(ref) == C.N_CONTROLS
    for chip in C.ALL_CHIPS:
        for num in range(1, C.N_PANELS + 1):
            head = C.read_lines(C.panel_probe_bed(chip, num))[:C.N_CONTROLS]
            assert head == ref, "controls differ chip %d panel %d" % (
                chip, num)
