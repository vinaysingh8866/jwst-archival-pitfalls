# Run evidence

Summaries from the runs that produced the numbers in the main README. Paths are
scrubbed; candidate tables themselves are on Zenodo
(https://doi.org/10.5281/zenodo.19394042) and are not duplicated here.

| File | Run | What it contains |
|---|---|---|
| `per_field_unmatched.md` | 27-field NIRCam survey, 690,358 sources | Sources, unmatched count and fraction, and validation verdicts per field |
| `scrutiny_check_statistics.md` | Candidate scrutiny, 318 gold-tier candidates | How often each of the 16 checks returns PASS/WARN/FAIL, and the verdict split |
| `validation_summary.txt` | Consolidated validation, 24,345 candidates (2026-04-05) | Verdict distribution, per-field breakdown, SED-physics flag counts, z > 5 outcome, the 824 validated sources |
| `photoz_crosscheck_report.txt` | Dual-template photo-z, 16,397 candidates (2026-04-03) | FSPS versus Carnall SFH-z agreement classes and the sources that moved |
| `color_outlier_report.txt` | k-NN colour-space outliers, 32,519 sources | The top 50 outliers with colours and classification (all artifacts on inspection) |
| `archive_volume_summary.txt` | Multi-epoch inventory, 23 fields | Epoch pairs and cadence-weighted survey volume per field: 360 arcmin² × yr total |
| `epoch_index_report.txt` | Local mosaic inventory, 29 workspaces | Which field/filter pairs have two epochs at least 7 days apart |
| `mast_epoch_availability_report.txt` | MAST query across the archive | Fields with two or more NIRCam epochs available for download |
| `alma_dark_candidates.txt` | JWST × ALMA cross-match | The 49 sub-mm sources with no catalog counterpart that forced photometry later recovered |

Not included: the NIRCam persistence figure (regenerate with
`jwst-td figure` in jwst-nircam-timedomain once the multi-epoch data is downloaded).
