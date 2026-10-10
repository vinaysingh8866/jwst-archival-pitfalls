# jwst-archival-pitfalls

**A reference catalog of the artifact classes, selection effects and archive-access failures that produce false candidates in archival JWST searches, with the check that catches each one.**

Everything here was measured on real runs: 27 NIRCam fields and 690,358 sources through a detection, photo-z, cross-match and anomaly pipeline; 11 fields of multi-epoch difference imaging; a JWST × ALMA cross-match; a colour-space outlier search; and a moving-object search. Each section states what was run, what came out, the technical cause of every false positive, and the test that removes it. The code for the checks is in the linked repositories.

| Repository | Contents |
|---|---|
| [jwst-discovery](https://github.com/vinaysingh8866/jwst-discovery) | NIRCam detection, photometry, photo-z, cross-match and anomaly pipeline; the 16-check candidate scrutiny script |
| [jwst-nircam-timedomain](https://github.com/vinaysingh8866/jwst-nircam-timedomain) | Multi-epoch alignment and difference imaging; persistence ratio filter; direct-S3 downloader |
| [WHATS_POSSIBLE.md](WHATS_POSSIBLE.md) | Eight things that can be built or measured now from these tools and numbers: completeness maps, a per-position oracle, an artifact atlas, a two-filter transient census, spectrum-first source finding, an FGS occultation search, a shared catalog registry, reuse on other surveys |
| [prototypes/](prototypes/) | FGS guide-star photometry smoke test for HST and JWST |
| [results/](results/) | The run summaries behind every number here: per-field unmatched fractions, per-check PASS/WARN/FAIL rates, validation and photo-z reports, colour-outlier list, epoch inventory and survey volume |
| [pitfalls.yaml](pitfalls.yaml) + [checklist.py](checklist.py) | The same catalog as data: 32 entries with id, domain, signature, cause, check and the function that implements it. `python checklist.py --domain time-domain` prints a checklist; `--json` for tooling |

---

## 1. Photometric high-redshift candidates

**Run:** EAZY photo-z on ~690k sources across 27 fields; sources with z_phot > 6 selected; 16 automated checks per candidate.
**Outcome:** 318 gold-tier candidates before reference-catalog expansion, 83 after, 0 surviving at z > 6.

| Failure mode | Signature | Check |
|---|---|---|
| Photo-z grid ceiling | Every source with z > 12.8 returns z = 12.87308 exactly, the top of the template grid | Reject any z equal to the grid maximum; extend the grid or treat as unconstrained |
| Reference-catalog gap | Fields with no published JWST catalog show 28 to 49 percent "unmatched" sources | Unmatched fraction above ~10 percent means the reference set is incomplete, not that the field is novel; a source brighter than mag 23 with zero matches is a catalog gap |
| V-shaped SED | Flux dip of more than 1 mag between adjacent bands, mimicking a Lyman break | Reject dips > 1 mag; require a monotonic break with ≥ 2 bands above it and no detection below it |
| Deblending fragments | Multiple sources within 3" sharing a bright neighbour; > 30 sources within 3" | Flag fragment clusters and crowding; bright neighbour within a few arcseconds disqualifies |
| Intracluster light | Extended, low surface brightness, low chi2, near a cluster core | Combine extent, surface brightness and position relative to the BCG |
| Underconstrained fit | chi2 < 0.1 with few valid bands | Treat very low chi2 as a warning, not a good fit; require a minimum band count |
| Foreground star | Gaia counterpart at "high z" | Cross-match Gaia before trusting any photo-z |
| Duplicate detection | Same source twice within 1" | Deduplicate on position before ranking |

## 2. Colour-space outliers

**Run:** k-nearest-neighbour distance in four NIRCam colours over 60k sources with good photometry; top 50 inspected.
**Outcome:** 50 of 50 were artifacts.

| Failure mode | Signature | Check |
|---|---|---|
| Broken photometry at faint magnitudes | Unphysical colours with |colour| > 9 mag, concentrated in one field | Require |colour| < 5 and S/N > 10 before any outlier ranking |
| Diffraction spikes | Candidates sit on the arms of the six-vane PSF pattern of a bright star | Mask spike geometry around every star brighter than the saturation limit; visual check of cutouts |
| Single hot pixel | One band at mag 22 with S/N > 2000 in a 5×5 aperture, other bands at mag 24 to 25 | Compare peak pixel to aperture flux; reject single-pixel dominated detections |

## 3. Multi-epoch difference imaging

**Run:** 11 fields with two or more F200W epochs; translation and affine alignment; subtraction with a flux-ratio filter; 127 GB downloaded.
**Outcome:** 10 candidates, 0 surviving a second-filter check.

| Failure mode | Signature | Check |
|---|---|---|
| NIRCam SW persistence | 4 to 10× brightening in F200W with no change in F277W at the same epoch | Require the variation in two filters; persistence is confined to the short-wavelength detectors |
| Persistence rate | About 6 false transients per arcmin² per year at 5σ | Budget for it: this is comparable to the real supernova rate in the same volume |
| Alignment residuals | Dipole residuals around stars at 0.4 to 0.5 px | Residual is set by centroid noise, not geometry; affine over translation gains little; a position-dependent distortion model would be needed |
| ZOGY with few PSF stars | 10× more candidates, all noise | ZOGY needs ~100 high-S/N stars per epoch; with ~35 the matching kernel is ill-conditioned |
| Detector seams | Residual lines along SCA boundaries | Mask from the WHT plane; removes ~5 percent of area and changes the candidate count negligibly |
| MIRI pixel scale | 99.7 percent of MIRI pixels masked | Masks expressed in pixels were tuned for NIRCam; express mask radii in arcseconds |

Archive volume available for this kind of search as of early 2026: about 360 arcmin² × yr of multi-epoch NIRCam imaging.

## 4. Cross-archive "dark" sources

**Run:** ALMA sub-mm sources cross-matched against a JWST catalog, the DJA GOODS-S catalog, Euclid Q1 and the Chandra Source Catalog; 49 candidates with no JWST counterpart, 4 also undetected in DJA and Euclid.
**Outcome:** Forced photometry on the deep JADES coadd recovered the top candidate at F200W S/N = 132.

| Failure mode | Signature | Check |
|---|---|---|
| Catalog-depth bias | "No source within 1.5"" in a 5σ multi-band catalog, but clear flux at AB 28 to 29 in the deep coadd | Never classify a position as dark from a catalog; run forced photometry on the deepest available image |
| Footprint mismatch | Reference catalog reports no source because the position is outside its mosaic | Check the weight or coverage map at the position, not just the source list |
| Positional offset assumption | Expected 1.5 to 5" sub-mm to NIR offsets; actual offsets are 0.3 to 1.0" | Match at 1" and treat larger offsets as separate objects |
| Coordinate rounding | RA/Dec rounded to 4 decimals introduces 0.36" offsets | Keep full precision through every intermediate file |

## 5. Moving objects

**Run:** Pairwise cross-match of detections between epochs of the same field; 6,187 pairwise candidates; linking into tracks.
**Outcome:** 1 multi-edge track, a slow proper-motion star.

| Failure mode | Signature | Check |
|---|---|---|
| Independent-pair counting | The same object appears in many epoch pairs and is counted each time | Link pairs into tracks with consistent motion and position angle before counting |
| Coadd-level motion | Level-3 mosaics average out within-visit motion | Use per-exposure data for fast movers |

## 6. Archive access

| Problem | Symptom | Working approach |
|---|---|---|
| MAST product lists for large programs | `get_product_list` hangs or returns `ChunkedEncodingError` for fields with 1000+ products | List the `stpubdata` S3 bucket directly and read TARG_RA/TARG_DEC from FITS headers via byte-range requests (`download_direct_s3.py` in jwst-nircam-timedomain) |
| Anonymous S3 rate limiting | `Max Retries Exceeded` above ~20 concurrent streams | Keep to 8 streams per IP with adaptive retry |
| DJA bucket enumeration | `s3://grizli-v2/JwstMosaics/v7/` allows GET but denies LIST | Build file names from the published pattern; about 22 percent of guessed names existed |
| VizieR row limit | Queries return exactly 50 rows | Instantiate `Vizier(row_limit=-1)` per call; the class attribute is not always honoured |
| SIMBAD timeouts on crowded fields | Query hangs | 120 s timeout and a 50,000-row limit |
| SEP deblending overflow | Extraction fails on crowded cluster cores | Raise `sub_object_limit` from 2048 to 32768, retry at 131072 |

## 7. Candidate checklist

Before reporting any source from an archival search:

1. Photo-z is not at a grid edge and chi2 is neither high nor suspiciously low.
2. No flux detected below the claimed break; at least two bands above it.
3. Peak pixel is consistent with the aperture flux in every band.
4. No source brighter than the candidate within a few arcseconds; fewer than 30 sources within 3".
5. Position is off any diffraction spike, mosaic edge and detector seam.
6. Any variability is present in two filters.
7. Forced photometry has been run on the deepest available image at the position.
8. The reference catalogs actually cover the position (weight map, not source list).
9. Gaia, NED and SIMBAD have been queried at full-precision coordinates.
10. The field's published catalogs have all been included in the reference set.

## Evidence

The headline numbers come from runs whose summaries are in [results/](results/):

| Number in this document | File |
|---|---|
| Unmatched fraction per field, 0.0 percent (CEERS) to 33.1 percent (RXC J0032) | `results/per_field_unmatched.md` |
| FAIL rate per check: photo-z quality 46.9 percent, brightness-vs-novelty 41.5 percent, SED slope 29.2 percent, crowding 23.3 percent, grid edge 21.1 percent | `results/scrutiny_check_statistics.md` |
| 24,345 candidates → 824 validated, 2,693 rejected; 1,108 at z > 5 → 1 validated | `results/validation_summary.txt` |
| Dual-template photo-z agreement on 16,397 candidates | `results/photoz_crosscheck_report.txt` |
| Top 50 colour outliers, 50 artifacts | `results/color_outlier_report.txt` |
| 360 arcmin² × yr of multi-epoch volume across 23 fields | `results/archive_volume_summary.txt` |
| 49 "JWST-dark" ALMA sources | `results/alma_dark_candidates.txt` |

## Related published work

Directions that overlap with the searches above and should be consulted before starting similar work: Nakajima/Welch 2025 (Pop III template matching, LAP1-B); Pierel/Pascale 2024–25 and TDCOSMO 2025 (lensed-supernova time delays); spaceKLIP (coronagraph archive reprocessing); JWST-PRIMAL 2025 (JWST × Spitzer dust-obscured galaxies); Fudamoto+ and Yan+ (caustic-crossing stars in cluster arcs); DiSCo-TNOs (archival solar-system objects); Tang+ 2024 (HST+JWST variability-selected AGN); Schlichting+ 2009 (HST FGS occultations).

## License

Text: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Code in `prototypes/`: MIT. Copyright (c) 2026 Vinay Singh.
