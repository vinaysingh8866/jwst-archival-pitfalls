# What these tools and measurements make possible

Each item below is something that can be built or measured now with the public archive and the code in these repositories. For each: what it is, what already exists here to start from, and what it would produce.

## 1. A catalog-completeness map of the JWST archive

**What:** For every field with public NIRCam imaging, a map of where published catalogs actually have detections, the local 5σ depth, and the fraction of sources the catalogs miss.

**Exists here:** the per-field unmatched fractions for 27 fields (`results/per_field_unmatched.md`), the reference-catalog registry covering 50+ catalogs per field (jwst-discovery, `catalog_registry.py`), forced photometry (`measure` stage), and the catalog-gap and brightness-vs-novelty checks.

**Would produce:** a per-pixel completeness and depth product per field, and a ranked list of fields where the public catalogs are thinnest. The unmatched fraction already separates well-catalogued fields (0.0 to 0.2 percent) from uncatalogued ones (15 to 33 percent); the map makes that spatial.

## 2. A per-position oracle: coverage, depth, forced flux, artifact risk

**What:** Given any RA/Dec, return whether JWST actually covers it, the local depth per filter, the forced-photometry flux at that position regardless of catalog detection, nearby artifact risk (spikes, persistence zones, seams), and which catalogs list it.

**Exists here:** forced aperture photometry on arbitrary positions, the weight-map coverage check from the catalog-depth pitfall, the diffraction-spike and bright-star proximity checks, and the multi-archive cross-match (NED, SIMBAD, Gaia, Chandra, XMM, VLASS, eROSITA, WISE, Spitzer).

**Would produce:** the test every "catalog-dark" claim needs. The 49 ALMA sources in `results/alma_dark_candidates.txt` were all "dark" by catalog and detected by forced photometry on the deep coadd; the oracle makes that check routine.

## 3. An artifact-risk atlas for NIRCam

**What:** Per-field maps of where a detection is likely to be a persistence ghost, a diffraction spike, a hot pixel, a seam residual or a deblending fragment, with measured rates.

**Exists here:** the NIRCam short-wavelength persistence rate (about 6 false transients per arcmin² per year at 5σ, two-filter rejection in jwst-nircam-timedomain), the colour-outlier list where every top candidate was a spike or a hot pixel (`results/color_outlier_report.txt`), the crowding and fragment checks with their failure rates (`results/scrutiny_check_statistics.md`), and the SCA seam masking from the weight plane.

**Would produce:** a mask layer anyone can apply before selecting candidates, and a false-positive budget per artifact class.

## 4. A two-filter transient census of the public multi-epoch archive

**What:** Apply the alignment and difference-imaging pipeline to every field with repeat NIRCam visits, requiring variation in two filters, and publish the surviving variables with light curves plus the non-detection statistics.

**Exists here:** the full pipeline from epoch discovery to light curves (`jwst-td index`, `query-epochs`, `download`, `align`, `diff`, `lightcurves`), the epoch inventory and the 360 arcmin² × yr volume estimate (`results/archive_volume_summary.txt`, `results/mast_epoch_availability_report.txt`).

**Would produce:** a variable-source table and rate limits. The volume is small today and grows with every cycle's public release; the pipeline reruns on new data unchanged.

## 5. Spectrum-first source finding in slitless and MSA data

**What:** Forward-model the dispersed trace of every catalogued source in public NIRCam and NIRISS WFSS and NIRSpec MSA exposures, subtract, and search the residual for emission lines from sources no image-first catalog contains.

**Exists here:** the direct-S3 downloader that bypasses MAST product-list hangs, the segmentation maps and per-source photometry needed to predict traces, the forced-photometry cross-check at implied sky positions, and the artifact catalog for the imaging-side checks.

**Would produce:** a list of line emitters whose redshift comes from the line itself, with no photometric-redshift grid involved. The image-first failure modes in this catalog do not transfer to the residual: persistence is broadband, hot pixels do not disperse, and the grid ceiling does not exist.

## 6. A stellar-occultation search in FGS guide-star photometry

**What:** Matched-filter search of HST and JWST Fine Guidance Sensor time series for Fresnel-shaped dips from sub-kilometre Kuiper Belt objects.

**Exists here:** `prototypes/fgs_smoke_test.py`, which downloads one HST and one JWST FGS observation, parses the guide-star channels, and reports cadence and photometric precision (HST at 40 Hz, JWST at 16 Hz). HST FGS has about 75,000 hours since the last published search; JWST FGS about 25,000 hours.

**Would produce:** either detections or a surface-density upper limit. Both are measurements; neither needs spectroscopic follow-up.

## 7. A reference-catalog registry as a shared resource

**What:** The per-field list of published catalogs, with download recipes, column mappings and coverage footprints, maintained independently of any one pipeline.

**Exists here:** `catalog_registry.py` in jwst-discovery (29 fields, DJA, UNCOVER, JADES, CANUCS, RELICS, HFF, CLASH, MUSE and VizieR sources), the `scripts/downloads/` recipes, and the field-selection scripts that find JWST cluster fields with no published catalog.

**Would produce:** a YAML registry other tools can consume, and a running list of uncatalogued fields. The catalog-gap check already warns when a known catalog is missing from the reference set; a shared registry makes that warning complete.

## 8. Reusing the validation stack on other surveys

**What:** The 16 checks, the cutout classifier and the dual-template photo-z cross-check applied to Euclid, Roman or Rubin catalogs.

**Exists here:** the checks are written against column names, not against JWST specifics; the photo-z checks (grid ceiling, chi2 extremes, below-break detections) and the deblending checks (crowding, bright neighbour, fragment cluster) apply to any multi-band catalog with segmentation.

**Would produce:** per-check failure rates for each survey, comparable to `results/scrutiny_check_statistics.md`.
