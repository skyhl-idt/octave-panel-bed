"""Build the sequence -> genomic-coordinate dictionary from the original
Kyudo2 per-panel probe bed files and the hg38p2 reference.

Output: dict.tsv with columns
  seq  chrom  start  end  strand  tstart  tend  orig_panel  orig_idx  is_control
where (start,end) is the probe interval and (tstart,tend) is the parallel
target (hotspot) interval taken from the original Target.bed (NOT computable
from the probe centre -- the hotspot is off-centre by 1..118 bp).
orig_idx is the 1-based probe line within the original panel bed,
and is_control marks the 15 universal probes shared by every panel.

The probe sequence is the reference sequence at the probe interval,
reverse-complemented for '-' strand probes (verified identity == 1.0).
"""
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reflib import Fasta, REF, KYUDO, DICT_TSV  # noqa: E402

OUT = DICT_TSV


def main():
    fa = Fasta(REF)
    rows = []  # (seq, chrom, start, end, strand, tstart, tend, panel, idx)
    seq_panels = defaultdict(set)
    n_panels = 0
    for panel_num in range(1, 201):
        bed = os.path.join(
            KYUDO, "Octave_Hotspot_Panel_120bp_%03d_Probe.bed" % panel_num)
        tbed = os.path.join(
            KYUDO, "Octave_Hotspot_Panel_120bp_%03d_Target.bed" % panel_num)
        if not os.path.exists(bed) or not os.path.exists(tbed):
            raise SystemExit("missing bed for panel %d" % panel_num)
        n_panels += 1
        panel = "Panel%03d" % panel_num
        plines = [l.rstrip("\n").split("\t") for l in open(bed)]
        tlines = [l.rstrip("\n").split("\t") for l in open(tbed)]
        if len(plines) != len(tlines):
            raise SystemExit("probe/target length mismatch %s" % panel)
        for i, (f, tf) in enumerate(zip(plines, tlines), start=1):
            chrom, start, end, strand = f[0], int(f[1]), int(f[2]), f[3]
            tstart, tend = int(tf[1]), int(tf[2])
            seq = fa.probe_seq(chrom, start, end, strand)
            rows.append((seq, chrom, start, end, strand,
                         tstart, tend, panel, i))
            seq_panels[seq].add(panel)
    fa.close()

    # control probes = sequences present in (essentially) every panel
    controls = {s for s, ps in seq_panels.items() if len(ps) >= n_panels}
    sys.stderr.write("panels=%d probes=%d unique_seq=%d controls=%d\n" % (
        n_panels, len(rows), len(seq_panels), len(controls)))

    # uniqueness of non-control sequences
    nonctrl_dup = {s: ps for s, ps in seq_panels.items()
                   if s not in controls and len(ps) > 1}
    sys.stderr.write("non-control sequences in >1 panel: %d\n"
                     % len(nonctrl_dup))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as out:
        out.write("seq\tchrom\tstart\tend\tstrand\ttstart\ttend"
                  "\torig_panel\torig_idx\tis_control\n")
        for seq, chrom, start, end, strand, tstart, tend, panel, i in rows:
            out.write("%s\t%s\t%d\t%d\t%s\t%d\t%d\t%s\t%d\t%d\n" % (
                seq, chrom, start, end, strand, tstart, tend, panel, i,
                1 if seq in controls else 0))
    sys.stderr.write("wrote %s\n" % OUT)


if __name__ == "__main__":
    main()
