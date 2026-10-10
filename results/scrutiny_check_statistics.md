# Scrutiny check statistics

Source: the largest candidate-scrutiny run (scrutiny_full_report.txt, 318 candidates, 16 checks each). Verdict = REJECT if any check FAILs, UNCERTAIN if any WARNs, else PROMISING/EXCELLENT.

## Verdicts

| Verdict | Candidates |
|---|---|
| UNCERTAIN | 230 |
| REJECT | 76 |
| PROMISING | 12 |

## How often each check fires

| Check | PASS | WARN | FAIL | FAIL rate |
|---|---|---|---|---|
| EAZY grid edge | 249 | 2 | 67 | 21.1% |
| Photo-z quality | 87 | 82 | 149 | 46.9% |
| SED consistency | 295 | 13 | 10 | 3.1% |
| Single-band spike | 301 | 8 | 9 | 2.8% |
| Morphology | 256 | 58 | 4 | 1.3% |
| Band coverage | 318 | 0 | 0 | 0.0% |
| Proximity | 318 | 0 | 0 | 0.0% |
| Multi-wavelength | 318 | 0 | 0 | 0.0% |
| Duplicates | 237 | 81 | 0 | 0.0% |
| SED slope | 163 | 62 | 93 | 29.2% |
| Crowding | 135 | 109 | 74 | 23.3% |
| Bright neighbor | 302 | 15 | 1 | 0.3% |
| Fragment cluster | 103 | 215 | 0 | 0.0% |
| ICL contamination | 282 | 28 | 8 | 2.5% |
| Brightness vs novelty | 151 | 35 | 132 | 41.5% |
| Catalog gap | 179 | 139 | 0 | 0.0% |
