"""Structure & format checks for the emitted bed files."""
import os

import pytest

import conftest as C


@pytest.mark.parametrize("chip", C.ALL_CHIPS)
def test_chip_dir_exists(chip):
    """The per-chip results directory (results/Chip_N) exists."""
    assert os.path.isdir(os.path.join(C.BED, "Chip_%d" % chip))


@pytest.mark.parametrize("chip", C.ALL_CHIPS)
def test_all_panel_files_present(chip):
    """All 200 Probe/Target bed pairs plus ALL_Probe.bed and the panel
    mapping table are present for the chip."""
    for num in range(1, C.N_PANELS + 1):
        assert os.path.isfile(C.panel_probe_bed(chip, num)), \
            "missing Probe.bed panel %d chip %d" % (num, chip)
        assert os.path.isfile(C.panel_target_bed(chip, num)), \
            "missing Target.bed panel %d chip %d" % (num, chip)
    assert os.path.isfile(C.all_probe_bed(chip))
    assert os.path.isfile(os.path.join(C.BED, "Chip_%d" % chip,
                                       "panel_mapping.tsv"))


@pytest.mark.parametrize("chip", C.ALL_CHIPS)
def test_exactly_200_panel_bed_pairs(chip):
    """There are exactly 200 per-panel Probe.bed and 200 Target.bed files
    (no stray or missing panels), excluding the combined ALL file."""
    d = os.path.join(C.BED, "Chip_%d" % chip)
    probe = [f for f in os.listdir(d)
             if f.endswith("_Probe.bed") and "ALL" not in f]
    target = [f for f in os.listdir(d) if f.endswith("_Target.bed")]
    assert len(probe) == C.N_PANELS
    assert len(target) == C.N_PANELS


@pytest.mark.parametrize("chip", C.ALL_CHIPS)
def test_probes_per_panel(chip):
    """Every panel holds the expected probe count for its chip
    (1490 / 1485 / 1500 for Chip 1 / 2 / 3)."""
    exp = C.PROBES_PER_PANEL[chip]
    for num in range(1, C.N_PANELS + 1):
        n = len(C.read_lines(C.panel_probe_bed(chip, num)))
        assert n == exp, "chip %d panel %d has %d probes (want %d)" % (
            chip, num, n, exp)


@pytest.mark.parametrize("chip", C.ALL_CHIPS)
def test_probe_and_target_parallel_length(chip):
    """Each panel's Probe.bed and Target.bed have the same number of rows so
    the two files stay row-for-row aligned."""
    for num in range(1, C.N_PANELS + 1):
        p = len(C.read_lines(C.panel_probe_bed(chip, num)))
        t = len(C.read_lines(C.panel_target_bed(chip, num)))
        assert p == t, "chip %d panel %d probe/target length mismatch" % (
            chip, num)


@pytest.mark.parametrize("chip", C.ALL_CHIPS)
def test_bed_format_five_columns_and_valid(chip):
    """Probe bed rows are well-formed: 5 columns, end>start, a 120bp interval,
    strand in {+,-}, and the name column equals 'chrom:start-end'."""
    for num in (1, 100, 200):
        for ln in C.read_lines(C.panel_probe_bed(chip, num)):
            f = ln.split("\t")
            assert len(f) == 5, "not 5 cols: %r" % ln
            chrom, start, end, strand, name = f
            start, end = int(start), int(end)
            assert end > start
            assert end - start == 120, "probe not 120bp: %r" % ln
            assert strand in ("+", "-")
            assert name == "%s:%d-%d" % (chrom, start, end)


@pytest.mark.parametrize("chip", C.ALL_CHIPS)
def test_target_within_probe(chip):
    """Each target interval is 1bp wide, lies inside the parallel probe
    interval, and shares the probe's chromosome and strand."""
    for num in (1, 100, 200):
        probes = C.read_lines(C.panel_probe_bed(chip, num))
        targets = C.read_lines(C.panel_target_bed(chip, num))
        for p, t in zip(probes, targets):
            pf, tf = p.split("\t"), t.split("\t")
            assert pf[0] == tf[0]              # chrom
            assert pf[3] == tf[3]              # strand
            ps, pe = int(pf[1]), int(pf[2])
            ts, te = int(tf[1]), int(tf[2])
            assert te - ts == 1, "target not 1bp: %r" % t
            assert ps <= ts < pe, "target outside probe: %r vs %r" % (t, p)


@pytest.mark.parametrize("chip", C.ALL_CHIPS)
def test_all_probe_bed_is_concatenation(chip):
    """The combined ALL_Probe.bed equals the per-panel Probe.beds concatenated
    in panel order, with the expected total row count."""
    expected = []
    for num in range(1, C.N_PANELS + 1):
        expected.extend(C.read_lines(C.panel_probe_bed(chip, num)))
    actual = C.read_lines(C.all_probe_bed(chip))
    assert len(actual) == C.N_PANELS * C.PROBES_PER_PANEL[chip]
    assert actual == expected
