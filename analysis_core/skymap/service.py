import logging

import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from regions import CircleSkyRegion

from gammapy.data import DataStore
from gammapy.datasets import MapDataset
from gammapy.estimators import ExcessMapEstimator
from gammapy.makers import MapDatasetMaker, RingBackgroundMaker, SafeMaskMaker
from gammapy.maps import MapAxis, WcsGeom

log = logging.getLogger(__name__)

_SOURCE_COORDS: dict[str, tuple[float, float]] = {
    "crab_sample":   (83.633, 22.014),
    "hess-dl3-dr1":  (228.32, -59.08),
    "hess_rx_j1713": (258.35, -39.76),
    "magic_crab":    (83.633, 22.014),
}

_DEFAULT_COORD = (83.633, 22.014)


def _get_source_coord(dataset_id: str) -> tuple[float, float]:
    for key, coord in _SOURCE_COORDS.items():
        if key in dataset_id.lower():
            return coord
    return _DEFAULT_COORD


def run_skymap(
    datastore_path: str,
    dataset_id: str,
    *,
    width_deg: float = 3.0,
    binsz_deg: float = 0.02,
    energy_min_tev: float = 0.5,
    energy_max_tev: float = 10.0,
    ring_r_in_deg: float = 0.5,
    ring_width_deg: float = 0.3,
    exclusion_radius_deg: float = 0.3,
    correlation_radius_deg: float = 0.1,
    offset_max_deg: float = 2.5,
) -> dict:

    log.info(
        "run_skymap: dataset=%s  width=%.2f  binsz=%.3f",
        dataset_id, width_deg, binsz_deg,
    )

    datastore = DataStore.from_dir(datastore_path)
    observations = datastore.get_observations()

    ra, dec = _get_source_coord(dataset_id)
    source_pos = SkyCoord(ra, dec, unit="deg", frame="icrs")

    energy_axis = MapAxis.from_energy_bounds(
        f"{energy_min_tev} TeV",
        f"{energy_max_tev} TeV",
        nbin=1,
    )

    energy_axis_true = MapAxis.from_energy_bounds(
        f"{energy_min_tev * 0.5} TeV",
        f"{energy_max_tev * 2.0} TeV",
        nbin=10,
        per_decade=True,
        name="energy_true",
    )

    geom = WcsGeom.create(
        skydir=source_pos,
        width=(width_deg, width_deg) * u.deg,
        binsz=binsz_deg * u.deg,
        frame="icrs",
        axes=[energy_axis],
    )

    exclusion_region = CircleSkyRegion(
        center=source_pos,
        radius=exclusion_radius_deg * u.deg,
    )
    exclusion_mask = ~geom.region_mask([exclusion_region])

    dataset_empty = MapDataset.create(
        geom=geom,
        energy_axis_true=energy_axis_true,
        name="empty",
    )

    maker = MapDatasetMaker(
        selection=["counts", "exposure", "background", "psf", "edisp"]
    )

    safe_mask_maker = SafeMaskMaker(
        methods=["offset-max"],
        offset_max=offset_max_deg * u.deg,
    )

    ring_maker = RingBackgroundMaker(
        r_in=f"{ring_r_in_deg} deg",
        width=f"{ring_width_deg} deg",
        exclusion_mask=exclusion_mask,
    )

    stacked_onoff = None

    for obs in observations:
        cutout = dataset_empty.cutout(
            position=source_pos,
            width=(width_deg + 1.0) * u.deg,
            name=f"obs-{obs.obs_id}",
        )

        cutout = maker.run(cutout, obs)
        cutout = safe_mask_maker.run(cutout, obs)
        cutout_image = cutout.to_image()
        onoff = ring_maker.run(cutout_image)

        if stacked_onoff is None:
            stacked_onoff = onoff
        else:
            stacked_onoff.stack(onoff)

    if stacked_onoff is None:
        raise RuntimeError("No observations processed")

    estimator = ExcessMapEstimator(
        correlation_radius=correlation_radius_deg * u.deg,
        selection_optional=[],
        correlate_off=False,
    )

    result_maps = estimator.run(stacked_onoff)

    def _to_list(m) -> list:
        arr = m.data
        if arr.ndim == 3:
            arr = arr[0]
        return np.nan_to_num(arr, nan=0.0).tolist()

    counts_arr = _to_list(stacked_onoff.counts)
    bkg_arr = _to_list(stacked_onoff.counts_off)
    excess_arr = _to_list(result_maps["npred_excess"])
    significance_arr = _to_list(result_maps["sqrt_ts"])

    sig_flat = np.array(significance_arr).ravel()

    stats = {
        "n_counts":          int(np.nansum(counts_arr)),
        "n_background":      float(round(np.nansum(bkg_arr), 1)),
        "n_excess":          float(round(np.nansum(excess_arr), 1)),
        "significance_max":  float(round(np.nanmax(sig_flat), 2)),
        "significance_mean": float(round(np.nanmean(sig_flat), 2)),
        "n_observations":    len(observations),
    }

    return {
        "counts":       counts_arr,
        "background":   bkg_arr,
        "excess":       excess_arr,
        "significance": significance_arr,
        "stats":        stats,
    }