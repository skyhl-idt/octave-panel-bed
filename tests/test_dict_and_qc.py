"""Tests for dict.tsv, sequence->genome correctness, panel mapping tables,
and the synthesis QC report."""
import os

import pytest

import conftest as C


# ----- dict.tsv -----------------------------------------------------------

def test_dict_row_count(dict_rows):
    """The dictionary covers every original probe: 200 panels x 1500 = 300000
    rows."""
    assert len(dict_rows) == C.N_PANELS * C.ORIG_PER_PANEL  # 300000


def test_dict_has_15_controls_per_panel(dict_rows):
    """Exactly 15 probes per panel are flagged as universal control probes,
    for all 200 panels."""
    from collections import Counter
    ctrl_by_panel = Counter()
    for r in dict_rows:
        if r["is_control"] == "1":
            ctrl_by_panel[r["orig_panel"]] += 1
    assert set(ctrl_by_panel.values()) == {C.N_CONTROLS}
    assert len(ctrl_by_panel) == C.N_PANELS


def test_dict_noncontrol_sequences_unique(dict_rows):
    """Each non-control probe sequence belongs to exactly one panel."""
    from collections import defaultdict
    panels = defaultdict(set)
    for r in dict_rows:
        if r["is_control"] == "0":
            panels[r["seq"]].add(r["orig_panel"])
    multi = {s: p for s, p in panels.items() if len(p) > 1}
    assert not multi, "%d non-control seqs in >1 panel" % len(multi)


def test_dict_target_within_probe(dict_rows):
    """Dictionary coordinates are internally consistent: 120bp probe, 1bp
    target, and the target sits inside the probe interval."""
    for r in dict_rows[:5000]:
        s, e = int(r["start"]), int(r["end"])
        ts, te = int(r["tstart"]), int(r["tend"])
        assert e - s == 120
        assert te - ts == 1
        assert s <= ts < e


# ----- sequence matches the reference genome ------------------------------

def test_probe_sequences_match_hg38(dict_rows):
    """Spot-check: the probe sequence equals the hg38p2 reference at the probe
    interval (reverse-complemented for '-' strand). This is the basis of the
    whole coordinate mapping."""
    reflib = pytest.importorskip("reflib")
    if not os.path.exists(reflib.REF + ".fai"):
        pytest.skip("hg38p2 reference not available")
    fa = reflib.Fasta(reflib.REF)
    try:
        # sample across the file: first, last, and a stride
        sample = dict_rows[::5000] + dict_rows[-3:]
        for r in sample:
            seq = fa.probe_seq(r["chrom"], int(r["start"]), int(r["end"]),
                               r["strand"])
            assert seq == r["seq"], "seq mismatch at %s:%s-%s%s" % (
                r["chrom"], r["start"], r["end"], r["strand"])
    finally:
        fa.close()


def test_chip_sequences_resolve_to_dict_coords(dict_rows):
    """Every probe sequence in each chip file is present in the dictionary and
    its emitted bed coordinate matches the dictionary coordinate."""
    seq2coord = {r["seq"]: (r["chrom"], r["start"], r["end"], r["strand"])
                 for r in dict_rows}
    for chip in C.ALL_CHIPS:
        # walk the chip txt and the emitted ALL_Probe.bed in parallel order
        bed = C.read_lines(C.all_probe_bed(chip))
        i = 0
        with open(C.CHIP_FILES[chip]) as fh:
            next(fh)
            for line in fh:
                f = line.rstrip("\r\n").split("\t")
                if len(f) < 4 or not f[0]:
                    continue
                seq = f[3]
                assert seq in seq2coord, "chip %d seq not in dict" % chip
                chrom, start, end, strand = seq2coord[seq]
                bf = bed[i].split("\t")
                assert (bf[0], bf[1], bf[2], bf[3]) == (chrom, start, end,
                                                        strand)
                i += 1
        assert i == len(bed)


# ----- panel mapping tables ----------------------------------------------

@pytest.mark.parametrize("chip", C.ALL_CHIPS)
def test_panel_mapping_has_200_rows(chip):
    """Each chip's panel_mapping.tsv has one row per panel (200 data rows)."""
    path = os.path.join(C.BED, "Chip_%d" % chip, "panel_mapping.tsv")
    rows = C.read_lines(path)[1:]  # skip header
    assert len(rows) == C.N_PANELS


def test_chip2_mapping_is_single_shifted_origin():
    """In Chip 2 each panel maps back to a single original panel, following
    the 10-panel shift recorded in panel_mapping.tsv."""
    path = os.path.join(C.BED, "Chip_2", "panel_mapping.tsv")
    for ln in C.read_lines(path)[1:]:
        chip_panel, origins, counts = ln.split("\t")
        k = int(chip_panel.replace("Panel", ""))
        assert origins == C.panel_name(C.chip2_orig_panel(k))


def test_chip3_mapping_is_multi_origin():
    """In Chip 3 each scrambled panel draws probes from many original panels
    (more than one origin listed per panel)."""
    path = os.path.join(C.BED, "Chip_3", "panel_mapping.tsv")
    for ln in C.read_lines(path)[1:]:
        chip_panel, origins, counts = ln.split("\t")
        assert origins.count("Panel") > 1


# ----- QC report ----------------------------------------------------------

def test_qc_report_files_exist():
    """Both the human-readable (.md) and machine-readable (.tsv) QC reports
    were written."""
    assert os.path.isfile(os.path.join(C.BED, "synthesis_qc_report.md"))
    assert os.path.isfile(os.path.join(C.BED, "synthesis_qc_report.tsv"))


def test_qc_report_all_pass():
    """Every check in the QC report passed (no FAIL rows)."""
    path = os.path.join(C.BED, "synthesis_qc_report.tsv")
    rows = C.read_lines(path)[1:]  # skip header
    assert rows, "QC report is empty"
    results = [r.split("\t")[2] for r in rows]
    assert set(results) == {"PASS"}, "QC has non-PASS rows: %s" % [
        r for r in rows if "\tPASS\t" not in r]
    assert "FAIL" not in results
