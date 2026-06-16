# Octave panel synthesis QC / confirmation report

Reference: hg38p2. Probe sequences matched exactly (identity 1.0) to the original Kyudo2 probe set; coordinates and targets taken from the original per-panel bed files.

**18 checks PASS, 0 FAIL.**

## Confirmed set descriptions

| Chip | Probes/panel | Description (confirmed) |
|---|---|---|
| 1 | 1490 | Original design & naming, last 10 probes dropped per panel |
| 2 | 1485 | Chip 1 minus 5 more (last 15 dropped), panels shifted by 10 (P001<-orig P191) |
| 3 | 1500 | Full original set, probes scrambled across panels; every non-control probe unique across panels; controls intact |

Control probes: the first 15 probes of every panel are the same 15 universal probes, in the same order, unscrambled, across all panels and all three chips.

No extra probes: every synthesized probe in all three chips matches exactly one probe in the original 300,000-probe set; 0 unknown/extra sequences.

## Detailed checks

| chip | check | result | detail |
|---|---|---|---|
| all | controls_first15_identical_unscrambled | PASS | first 15 probes identical & flagged control in all 600 panel-instances |
| 1 | panel_count_200 | PASS | panels=200 |
| 1 | probes_per_panel_1490 | PASS | sizes=[1490] |
| 1 | no_extra_probes | PASS | 0/298000 probes unmatched to original set |
| 1 | panels_single_origin | PASS | 0 probes from unexpected original panel |
| 1 | dropped_last_10_per_panel | PASS | 0 panels with unexpected missing-index set |
| 2 | panel_count_200 | PASS | panels=200 |
| 2 | probes_per_panel_1485 | PASS | sizes=[1485] |
| 2 | no_extra_probes | PASS | 0/297000 probes unmatched to original set |
| 2 | panels_single_origin | PASS | 0 probes from unexpected original panel |
| 2 | dropped_last_15_per_panel | PASS | 0 panels with unexpected missing-index set |
| 2 | panels_shifted_by_10 | PASS | chip Panel_k <- original Panel_((k+189)%200+1); e.g. P001<-P191, P011<-P001 |
| 3 | panel_count_200 | PASS | panels=200 |
| 3 | probes_per_panel_1500 | PASS | sizes=[1500] |
| 3 | no_extra_probes | PASS | 0/300000 probes unmatched to original set |
| 3 | noncontrol_unique_across_panels | PASS | 0 non-control sequences appear in >1 panel |
| 3 | all_original_noncontrol_present_once | PASS | distinct non-control probes=297000 (expected 297000) |
| 3 | probes_scrambled_across_panels | PASS | each panel draws from 198-200 original panels (mean 200) |
