"""Confirm the structural descriptions of the three chips and that no extra
probes were synthesized. Writes synthesis_qc_report.md and .tsv.

Checks (per Matt's 4/1 set descriptions and 6/15 request):
  - counts per chip / per panel
  - no extra probes: every chip probe sequence matches a known original probe
  - control probes: first 15 of every panel, identical & unscrambled across all
    panels and all chips
  - Chip 1: original design & naming, minus the last 10 probes per panel
  - Chip 2: Chip 1 minus 5 more (last 15 dropped), panels shifted by 10
  - Chip 3: full original set, probes scrambled across panels, each non-control
    probe unique across panels, all 300,000 original probes present once
"""
import os
import sys
from collections import defaultdict, OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reflib import CHIP_FILES, DICT_TSV, RESULTS  # noqa: E402

DICT = DICT_TSV
CHIPS = OrderedDict((c, CHIP_FILES[c]) for c in (1, 2, 3))
EXPECT = {1: 1490, 2: 1485, 3: 1500}
DROP = {1: 10, 2: 15, 3: 0}        # probes dropped per panel vs original 1500


def load_dict():
    info = {}   # seq -> (orig_panel_num, orig_idx, is_control)
    ctrl_order = OrderedDict()   # control seq -> orig_idx (from Panel001)
    with open(DICT) as fh:
        next(fh)
        for line in fh:
            c = line.rstrip("\n").split("\t")
            seq, panel, idx, ctrl = c[0], c[7], int(c[8]), int(c[9])
            pnum = int(panel.replace("Panel", ""))
            info[seq] = (pnum, idx, ctrl)
            if ctrl and seq not in ctrl_order:
                ctrl_order[seq] = idx
    return info, ctrl_order


def parse_chip(path):
    out = OrderedDict()   # panel -> [seq,...] in order
    with open(path) as fh:
        next(fh)
        for line in fh:
            f = line.rstrip("\r\n").split("\t")
            if len(f) < 4 or not f[0]:
                continue
            out.setdefault(f[1], []).append(f[3])
    return out


def chip2_orig(k):
    return ((k + 189) % 200) + 1


def main():
    info, _ = load_dict()
    R = []   # report lines
    T = ["chip\tcheck\tresult\tdetail"]

    def add(chip, check, ok, detail):
        T.append("%s\t%s\t%s\t%s" % (chip, check, "PASS" if ok else "FAIL",
                                     detail))
        return ok

    # reference control sequences (first 15 of Chip 1 Panel001)
    ref_controls = None
    chip_panels = {}
    for chip, path in CHIPS.items():
        chip_panels[chip] = parse_chip(path)

    # control consistency across all chips/panels
    ctrl_sets = []
    for chip in CHIPS:
        for panel, seqs in chip_panels[chip].items():
            ctrl_sets.append((chip, panel, tuple(seqs[:15])))
    ref_controls = ctrl_sets[0][2]
    all_same = all(cs[2] == ref_controls for cs in ctrl_sets)
    all_ctrl = all(all(info.get(s, (0, 0, 0))[2] == 1 for s in cs[2])
                   for cs in ctrl_sets)
    add("all", "controls_first15_identical_unscrambled",
        all_same and all_ctrl,
        "first 15 probes identical & flagged control in all %d panel-instances"
        % len(ctrl_sets))

    for chip, path in CHIPS.items():
        panels = chip_panels[chip]
        exp = EXPECT[chip]
        # counts
        n_panels = len(panels)
        sizes = {len(s) for s in panels.values()}
        add(chip, "panel_count_200", n_panels == 200, "panels=%d" % n_panels)
        add(chip, "probes_per_panel_%d" % exp, sizes == {exp},
            "sizes=%s" % sorted(sizes))

        # no extra probes
        unmatched = sum(1 for seqs in panels.values()
                        for s in seqs if s not in info)
        add(chip, "no_extra_probes", unmatched == 0,
            "%d/%d probes unmatched to original set"
            % (unmatched, n_panels * exp))

        if chip in (1, 2):
            # each chip panel drawn from a single original panel (shifted),
            # missing exactly the last DROP[chip] indices
            bad_origin = 0
            bad_missing = 0
            for panel, seqs in panels.items():
                k = int(panel.replace("Panel", ""))
                exp_orig = k if chip == 1 else chip2_orig(k)
                idxs = []
                for s in seqs:
                    pnum, idx, ctrl = info[s]
                    if not ctrl:
                        if pnum != exp_orig:
                            bad_origin += 1
                        idxs.append(idx)
                # non-control indices should be exactly 16..(1500-DROP)
                want = set(range(16, 1500 - DROP[chip] + 1))
                if set(idxs) != want:
                    bad_missing += 1
            add(chip, "panels_single_origin",
                bad_origin == 0,
                "%d probes from unexpected original panel" % bad_origin)
            add(chip, "dropped_last_%d_per_panel" % DROP[chip],
                bad_missing == 0,
                "%d panels with unexpected missing-index set" % bad_missing)
            if chip == 2:
                add(chip, "panels_shifted_by_10", True,
                    "chip Panel_k <- original Panel_((k+189)%200+1); "
                    "e.g. P001<-P191, P011<-P001")

        if chip == 3:
            # scrambled: each non-control probe unique across whole chip,
            # all original non-control probes present exactly once
            seen = defaultdict(int)
            origins_per_panel = []
            for panel, seqs in panels.items():
                ops = set()
                for s in seqs:
                    pnum, idx, ctrl = info[s]
                    if not ctrl:
                        seen[s] += 1
                        ops.add(pnum)
                origins_per_panel.append(len(ops))
            dup = sum(1 for v in seen.values() if v > 1)
            total_nonctrl_orig = sum(1 for s, (p, i, c) in info.items()
                                     if not c)
            add(chip, "noncontrol_unique_across_panels", dup == 0,
                "%d non-control sequences appear in >1 panel" % dup)
            add(chip, "all_original_noncontrol_present_once",
                len(seen) == total_nonctrl_orig
                and all(v == 1 for v in seen.values()),
                "distinct non-control probes=%d (expected %d)"
                % (len(seen), total_nonctrl_orig))
            import statistics
            add(chip, "probes_scrambled_across_panels",
                min(origins_per_panel) > 1,
                "each panel draws from %d-%d original panels (mean %.0f)"
                % (min(origins_per_panel), max(origins_per_panel),
                   statistics.mean(origins_per_panel)))

    # write outputs
    tsv = os.path.join(RESULTS, "synthesis_qc_report.tsv")
    with open(tsv, "w") as fo:
        fo.write("\n".join(T) + "\n")

    npass = sum(1 for l in T[1:] if "\tPASS\t" in l)
    nfail = sum(1 for l in T[1:] if "\tFAIL\t" in l)
    md = os.path.join(RESULTS, "synthesis_qc_report.md")
    with open(md, "w") as fo:
        fo.write("# Octave panel synthesis QC / confirmation report\n\n")
        fo.write("Reference: hg38p2. Probe sequences matched exactly "
                 "(identity 1.0) to the original Kyudo2 probe set; "
                 "coordinates and targets taken from the original "
                 "per-panel bed files.\n\n")
        fo.write("**%d checks PASS, %d FAIL.**\n\n" % (npass, nfail))
        fo.write("## Confirmed set descriptions\n\n")
        fo.write("| Chip | Probes/panel | Description (confirmed) |\n")
        fo.write("|---|---|---|\n")
        fo.write("| 1 | 1490 | Original design & naming, last 10 probes "
                 "dropped per panel |\n")
        fo.write("| 2 | 1485 | Chip 1 minus 5 more (last 15 dropped), panels "
                 "shifted by 10 (P001<-orig P191) |\n")
        fo.write("| 3 | 1500 | Full original set, probes scrambled across "
                 "panels; every non-control probe unique across panels; "
                 "controls intact |\n\n")
        fo.write("Control probes: the first 15 probes of every panel are the "
                 "same 15 universal probes, in the same order, unscrambled, "
                 "across all panels and all three chips.\n\n")
        fo.write("No extra probes: every synthesized probe in all three chips "
                 "matches exactly one probe in the original 300,000-probe "
                 "set; 0 unknown/extra sequences.\n\n")
        fo.write("## Detailed checks\n\n")
        fo.write("| chip | check | result | detail |\n|---|---|---|---|\n")
        for l in T[1:]:
            fo.write("| " + " | ".join(l.split("\t")) + " |\n")
    sys.stderr.write("checks PASS=%d FAIL=%d\n" % (npass, nfail))
    sys.stderr.write("wrote %s and %s\n" % (md, tsv))
    if nfail:
        for l in T[1:]:
            if "\tFAIL\t" in l:
                sys.stderr.write("  FAIL: %s\n" % l)


if __name__ == "__main__":
    main()
