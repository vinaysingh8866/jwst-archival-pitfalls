"""
Phase 0 smoke test v4 — correct HST FGS Transfer-mode parsing.

The PRIMARY HDU shape is (7, N_samples). Group identities are in the header:
    GTYPE1..GTYPE7 — names of the 7 channels.

For HST FGS Transfer (astrometric) mode the channels are:
    PMTXA   PMT A fine counts, X axis
    PMTXB   PMT B fine counts, X axis
    PMTYA   PMT A fine counts, Y axis
    PMTYB   PMT B fine counts, Y axis
    SSENCA  Star-Selector A encoder position
    SSENCB  Star-Selector B encoder position
    FLAGS   FGS status flags

The total photometric signal is PMTXA+PMTXB+PMTYA+PMTYB.

Also: with a TGT_MAG=12.1 reference star at 40 Hz, the photon-noise floor is
sqrt(N)/N ≈ 4% per 25-ms sample. Brighter guide stars (mag<10) hit Schlichting's
0.1-0.5% regime. So we report photon-noise floor too, and assess vs that, not
just absolute % RMS.
"""

from __future__ import annotations

import os
import sys
import warnings
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits

warnings.filterwarnings("ignore")

OUT_DIR = Path(os.path.expanduser("~/.jwst-discovery/shadow_census/hst"))
OUT_DIR.mkdir(parents=True, exist_ok=True)


def find_and_download_hst_fgs(prefer_bright: bool = True):
    from astroquery.mast import Observations
    print("Querying HST FGS observations post-2010...")
    obs = Observations.query_criteria(
        obs_collection="HST",
        instrument_name="FGS",
        t_min=55197,
    )
    obs_subset = sorted(
        [r for r in obs if r["t_exptime"] and 50 < r["t_exptime"] < 200],
        key=lambda r: r["t_exptime"],
    )
    target = obs_subset[len(obs_subset) // 2]
    print(f"  Selected obs_id={target['obs_id']}, target={target['target_name']}, "
          f"exptime={target['t_exptime']}s")

    products = Observations.get_product_list(target)
    sci = products[products["productType"] == "SCIENCE"]
    af_products = [
        r for r in sci
        if "_a" in str(r["productFilename"]) and str(r["productFilename"]).endswith("f.fits")
    ]
    if not af_products:
        af_products = list(sci[:1])
    target_product = af_products[0]
    fn = str(target_product["productFilename"])
    out_path = OUT_DIR / fn
    if out_path.exists() and out_path.stat().st_size == (target_product["size"] or 0):
        print(f"  Cached: {fn}")
    else:
        print(f"Downloading {fn}...")
        Observations.download_file(target_product["dataURI"], local_path=str(out_path), cache=False)
    return out_path


def parse_hst_fgs(path: Path):
    print(f"\n=== Parsing {path.name} ===")
    with fits.open(path) as hdul:
        data = hdul[0].data
        hdr = hdul[0].header

    n_rows, n_samples = data.shape
    exptime = hdr.get("EXPTIME", 0)
    cadence_hz = n_samples / exptime if exptime > 0 else float("nan")
    avg_time = hdr.get("AAVG_TIM", float("nan"))
    target = hdr.get("TARGNAME", "?").strip()
    tgt_mag = hdr.get("TGT_MAG", float("nan"))
    filt = hdr.get("AAST_FLT", "?").strip()
    fgsno = hdr.get("FGSNO", "?")

    gtypes = [str(hdr.get(f"GTYPE{i+1}", f"GTYPE{i+1}")).strip() for i in range(n_rows)]
    print(f"  Target: {target}  mag={tgt_mag}  filter={filt}  FGS-{fgsno}")
    print(f"  Shape: {n_rows} rows x {n_samples} samples")
    print(f"  EXPTIME: {exptime} sec  AAVG_TIM={avg_time}  -> cadence ~ {cadence_hz:.2f} Hz")
    print(f"  Channel labels: {gtypes}")

    print("\n  Per-row statistics:")
    print(f"    {'idx':>3s}  {'name':>8s}  {'mean':>12s}  {'std':>12s}  {'min':>12s}  {'max':>12s}  {'rel_rms_%':>10s}")
    for i in range(n_rows):
        row = data[i]
        mean = float(np.mean(row))
        std = float(np.std(row))
        rel_rms = (std / mean * 100) if mean != 0 else float("nan")
        print(f"    {i:>3d}  {gtypes[i]:>8s}  {mean:>12.3g}  {std:>12.3g}  "
              f"{float(np.min(row)):>12.3g}  {float(np.max(row)):>12.3g}  {rel_rms:>10.4f}")

    # Identify the 4 PMT rows by GTYPE
    pmt_idx = [i for i, g in enumerate(gtypes) if g.startswith("PMT")]
    flags_idx = [i for i, g in enumerate(gtypes) if g == "FLAGS"]
    print(f"\n  PMT rows by GTYPE: {pmt_idx}  ({[gtypes[i] for i in pmt_idx]})")
    print(f"  FLAGS row: {flags_idx}")

    flux = np.zeros(n_samples, dtype=np.float64)
    for i in pmt_idx:
        flux += data[i].astype(np.float64)

    flags = data[flags_idx[0]] if flags_idx else None
    t = np.arange(n_samples) / cadence_hz

    # Per-row diagnostic plot
    fig, axes = plt.subplots(n_rows, 1, figsize=(12, 14), sharex=True)
    for i in range(n_rows):
        axes[i].plot(t, data[i], lw=0.4, color=f"C{i}")
        axes[i].set_ylabel(f"{i}: {gtypes[i]}")
        axes[i].grid(alpha=0.3)
    axes[-1].set_xlabel("Time (sec)")
    axes[0].set_title(f"{path.name}  target={target} mag={tgt_mag} filter={filt}")
    plt.tight_layout()
    out = OUT_DIR / f"diagnostic_rows_{path.stem}.png"
    plt.savefig(out, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"\n  Per-row diagnostic plot: {out}")

    return flux, t, cadence_hz, flags, tgt_mag


def analyze_lightcurve(t, flux, flags, cadence_hz, tgt_mag, label):
    flux = np.asarray(flux, dtype=float)

    # Mask FILL values (99999998 / 99999999) and obvious bad samples
    finite = np.isfinite(flux) & (flux > 0) & (flux < 1e7)
    if flags is not None:
        # FLAGS row contains huge numbers; we drop samples flagged non-zero in a coarse way.
        # For now just keep finite/positive flux constraint.
        pass

    f = flux[finite]
    tt = t[finite]
    if len(f) < 100:
        print(f"  {label}: {len(f)} usable samples — too few")
        return None

    median = float(np.median(f))
    mean = float(np.mean(f))
    rel = f / median
    rms = float(np.std(rel))

    # Photon-noise floor: per-sample relative noise = 1/sqrt(N)
    photon_floor_pct = 100.0 / np.sqrt(median) if median > 0 else float("nan")

    print(f"\n  {label} statistics:")
    print(f"    samples (good):    {len(f)} / {len(flux)}")
    print(f"    median total:      {median:.4g} cts/sample")
    print(f"    relative RMS:      {rms*100:.4f}%")
    print(f"    photon-noise floor: {photon_floor_pct:.4f}% (Poisson on {median:.0f} cts)")
    print(f"    excess over photon: {rms*100/photon_floor_pct:.2f}x  (1.0=photon-limited)")
    print(f"    cadence:           {cadence_hz:.2f} Hz")
    print(f"    duration:          {tt[-1]-tt[0]:.2f} sec")

    # Schlichting threshold: detect a 0.3-sec dip with depth >2 sigma against
    # local fluctuations. Equivalent depth required:
    sigma_per_sample = rms
    n_in_dip = max(int(round(0.3 * cadence_hz)), 1)  # samples in 0.3 s
    sigma_dip = sigma_per_sample / np.sqrt(n_in_dip)
    print(f"    0.3-sec dip 1sigma: {sigma_dip*100:.4f}%  (need >2x for Schlichting-class detection)")

    fig, axes = plt.subplots(2, 1, figsize=(12, 7))
    axes[0].plot(tt - tt[0], rel, lw=0.5, color="C0")
    axes[0].axhline(1.0, color="k", lw=0.5, alpha=0.3)
    axes[0].set_xlabel("Time (sec)")
    axes[0].set_ylabel("Relative flux")
    axes[0].set_title(f"{label}  RMS={rms*100:.3f}%  photon-floor={photon_floor_pct:.3f}%  mag={tgt_mag}")
    axes[0].grid(alpha=0.3)

    rel_dc = rel - np.mean(rel)
    from numpy.fft import rfft, rfftfreq
    freqs = rfftfreq(len(rel_dc), d=1.0 / max(cadence_hz, 1.0))
    power = np.abs(rfft(rel_dc)) ** 2
    axes[1].loglog(freqs[1:], power[1:], lw=0.5, color="C1")
    axes[1].set_xlabel("Frequency (Hz)")
    axes[1].set_ylabel("Power")
    axes[1].set_title("Power spectrum")
    axes[1].grid(alpha=0.3, which="both")
    axes[1].axvspan(2, 10, color="green", alpha=0.15, label="occultation band (0.1-0.5 sec)")
    axes[1].legend()

    plt.tight_layout()
    out = OUT_DIR / f"lightcurve_{label.replace(' ', '_')}.png"
    plt.savefig(out, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"  plot: {out}")

    return {
        "rms_pct": rms * 100,
        "photon_floor_pct": photon_floor_pct,
        "n": len(f),
        "cadence_hz": cadence_hz,
        "sigma_dip_pct": sigma_dip * 100,
    }


def main() -> None:
    print("\n" + "#" * 70)
    print("#  SHADOW CENSUS — Phase 0 smoke test (HST, parsing v4)")
    print("#" * 70 + "\n")

    path = find_and_download_hst_fgs()
    if not path or not path.exists():
        sys.exit(1)

    flux, t, cadence, flags, tgt_mag = parse_hst_fgs(path)
    if flux is None:
        sys.exit(1)
    stats = analyze_lightcurve(t, flux, flags, cadence, tgt_mag, "HST FGS Transfer-mode")

    print("\n" + "#" * 70)
    print("#  Verdict")
    print("#" * 70)
    if stats is None:
        print("  Could not analyze.")
        sys.exit(1)
    cad_ok = stats["cadence_hz"] > 30
    photon_excess = stats["rms_pct"] / stats["photon_floor_pct"]
    photon_ok = photon_excess < 3.0
    if cad_ok and photon_ok:
        print(f"\n  HST FGS Transfer-mode parses correctly.")
        print(f"    cadence:           {stats['cadence_hz']:.1f} Hz (need 40 Hz)")
        print(f"    RMS:               {stats['rms_pct']:.3f}%  (vs photon-noise floor {stats['photon_floor_pct']:.3f}%)")
        print(f"    excess over photon: {photon_excess:.2f}x")
        print(f"    0.3-sec dip 1sigma: {stats['sigma_dip_pct']:.3f}%")
        print("\n  PROCEED TO PHASE 1: scale up to ~3000 hr ecliptic-strip pilot.")
        print("  At this floor, brighter guide stars (mag<10) will reach Schlichting's")
        print("  0.1-0.5% regime; faint stars are usable for upper-limit work.")
    else:
        print(f"\n  Cadence={stats['cadence_hz']:.1f} Hz, RMS={stats['rms_pct']:.2f}%, "
              f"photon-floor={stats['photon_floor_pct']:.2f}%, excess={photon_excess:.1f}x")
        if not photon_ok:
            print("  RMS far above photon floor — likely jitter or systematic dominates.")


if __name__ == "__main__":
    main()
