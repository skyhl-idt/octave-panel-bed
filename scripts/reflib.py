"""Random-access reader for an indexed FASTA (.fai) plus helpers."""
import os

_COMP = str.maketrans("ACGTNacgtn", "TGCANtgcan")


def revcomp(s):
    return s.translate(_COMP)[::-1]


class Fasta:
    def __init__(self, path):
        self.path = path
        self.idx = {}
        with open(path + ".fai") as fh:
            for line in fh:
                p = line.split("\t")
                # name -> (length, offset, bases_per_line, bytes_per_line)
                self.idx[p[0]] = (int(p[1]), int(p[2]), int(p[3]), int(p[4]))
        self._fh = open(path, "rb")

    def fetch(self, chrom, start, end):
        """0-based half-open [start, end) on the + strand, uppercased."""
        length, off, bp, bpl = self.idx[chrom]
        need = end - start
        nlines = (end - 1) // bp - start // bp + 1
        self._fh.seek(off + (start // bp) * bpl + (start % bp))
        data = self._fh.read(need + nlines + 8).decode("ascii")
        return data.replace("\n", "").replace("\r", "")[:need].upper()

    def probe_seq(self, chrom, start, end, strand):
        s = self.fetch(chrom, start, end)
        return revcomp(s) if strand == "-" else s

    def close(self):
        self._fh.close()


REF = "/mnt/archive/data/genomeLinks/hg38p2/hg38p2_primary.fa"
KYUDO = ("/mnt/archive/work/lren/projects/xGen/POTA/Design_200_Panels/"
         "Kyudo2_Panel_Files")

# --- project layout -------------------------------------------------------
PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(PROJECT, "data")
CHIPS_DIR = os.path.join(DATA, "chips")
RESULTS = os.path.join(PROJECT, "results")
DICT_TSV = os.path.join(RESULTS, "dict.tsv")

# The three Octave probe-sequence tables, keyed by chip number.
CHIP_FILES = {
    1: os.path.join(CHIPS_DIR, "All 200 panel sequences_Chip_1 1.txt"),
    2: os.path.join(CHIPS_DIR, "All 200 panel sequences_Chip_2 1.txt"),
    3: os.path.join(CHIPS_DIR, "All 200 panel sequences_Chip_3 1.txt"),
}


def chip_dir(chip):
    return os.path.join(RESULTS, "Chip_%d" % chip)


def orig_probe_bed(panel_num):
    return os.path.join(
        KYUDO, "Octave_Hotspot_Panel_120bp_%03d_Probe.bed" % panel_num)


def orig_target_bed(panel_num):
    return os.path.join(
        KYUDO, "Octave_Hotspot_Panel_120bp_%03d_Target.bed" % panel_num)

