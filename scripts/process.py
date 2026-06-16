"""Map each chip's probes to genomic coordinates via the sequence dictionary,
emit per-panel Probe.bed + Target.bed and combined ALL_Probe.bed per chip,
write panel mapping tables, and collect QC facts.
"""
import os
import sys
from collections import defaultdict, OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reflib import CHIP_FILES, DICT_TSV, RESULTS, chip_dir  # noqa: E402

DICT = DICT_TSV
CHIPS = OrderedDict((c, CHIP_FILES[c]) for c in (1, 2, 3))


def load_dict():
    seq2coord = {}          # seq -> (chrom,start,end,strand,tstart,tend)
    seq2orig = {}           # seq -> (orig_panel, is_control)
    orig_panel_seqs = defaultdict(list)   # orig_panel -> [seq,...] in order
    with open(DICT) as fh:
        next(fh)
        for line in fh:
            (seq, chrom, start, end, strand, tstart, tend,
             panel, idx, ctrl) = line.rstrip("\n").split("\t")
            coord = (chrom, int(start), int(end), strand,
                     int(tstart), int(tend))
            if seq in seq2coord and seq2coord[seq] != coord:
                sys.stderr.write("WARN seq maps to 2 coords: %s\n" % seq)
            seq2coord[seq] = coord
            seq2orig[seq] = (panel, int(ctrl))
            orig_panel_seqs[panel].append(seq)
    return seq2coord, seq2orig, orig_panel_seqs


def parse_chip(path):
    """Yield (panel, probe_id, seq) in file order."""
    with open(path) as fh:
        header = next(fh)
        for line in fh:
            f = line.rstrip("\r\n").split("\t")
            if len(f) < 4 or not f[0]:
                continue
            yield f[1], f[2], f[3]


def emit_bed_lines(coord):
    chrom, start, end, strand, tstart, tend = coord
    probe_name = "%s:%d-%d" % (chrom, start, end)
    probe = "%s\t%d\t%d\t%s\t%s" % (chrom, start, end, strand, probe_name)
    tname = "%s:%d-%d" % (chrom, tstart, tend)
    target = "%s\t%d\t%d\t%s\t%s" % (chrom, tstart, tend, strand, tname)
    return probe, target


def main():
    seq2coord, seq2orig, orig_panel_seqs = load_dict()
    qc = []

    for chip, path in CHIPS.items():
        outdir = chip_dir(chip)
        os.makedirs(outdir, exist_ok=True)

        panel_rows = OrderedDict()      # panel -> [(probe_id, seq)]
        for panel, pid, seq in parse_chip(path):
            panel_rows.setdefault(panel, []).append((pid, seq))

        unmatched = []
        all_probe = []
        # mapping table: chip panel -> Counter of original panels (non-control)
        panel_origin = OrderedDict()

        for panel, rows in panel_rows.items():
            probe_lines = []
            target_lines = []
            origins = defaultdict(int)
            for pid, seq in rows:
                coord = seq2coord.get(seq)
                if coord is None:
                    unmatched.append((panel, pid))
                    continue
                p, t = emit_bed_lines(coord)
                probe_lines.append(p)
                target_lines.append(t)
                all_probe.append(p)
                op, ctrl = seq2orig[seq]
                if not ctrl:
                    origins[op] += 1
            panel_origin[panel] = origins
            pnum = panel.replace("Panel", "")
            with open(os.path.join(
                    outdir,
                    "Octave_Hotspot_Panel_120bp_%s_Probe.bed" % pnum),
                    "w") as fo:
                fo.write("\n".join(probe_lines) + "\n")
            with open(os.path.join(
                    outdir,
                    "Octave_Hotspot_Panel_120bp_%s_Target.bed" % pnum),
                    "w") as fo:
                fo.write("\n".join(target_lines) + "\n")

        with open(os.path.join(
                outdir, "Octave_Hotspot_Panel_120bp_ALL_Probe.bed"),
                "w") as fo:
            fo.write("\n".join(all_probe) + "\n")

        # mapping table
        with open(os.path.join(outdir, "panel_mapping.tsv"), "w") as fo:
            fo.write("chip_panel\toriginal_panel(s)\tn_from_each\n")
            for panel, origins in panel_origin.items():
                items = sorted(origins.items(), key=lambda x: -x[1])
                src = ",".join(p for p, _ in items)
                cnt = ",".join(str(c) for _, c in items)
                fo.write("%s\t%s\t%s\n" % (panel, src, cnt))

        qc.append((chip, panel_rows, panel_origin, unmatched, all_probe))
        sys.stderr.write("Chip %d: panels=%d probes=%d unmatched=%d\n" % (
            chip, len(panel_rows), len(all_probe), len(unmatched)))

    # stash for qc script via simple re-read; here just print summary
    import json
    summ = {c: {"n_panels": len(pr), "n_probes": len(ap),
                "n_unmatched": len(um)}
            for c, pr, po, um, ap in qc}
    sys.stderr.write(json.dumps(summ) + "\n")


if __name__ == "__main__":
    main()
