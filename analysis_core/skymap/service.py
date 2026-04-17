from gammapy.data import DataStore
from gammapy.maps import WcsGeom
from gammapy.datasets import MapDataset
from gammapy.makers import MapDatasetMaker, SafeMaskMaker
from gammapy.estimators import ExcessMapEstimator

from astropy import units as u


def run_skymap(
    datastore_path: str,
    width_deg: float = 2.0,
    binsz_deg: float = 0.02,
    smoothing_sigma: float = 0.1,
):
    datastore = DataStore.from_dir(datastore_path)
    observations = datastore.get_observations()

    geom = WcsGeom.create(
        skydir=(83.63, 22.01),
        width=(width_deg, width_deg),
        binsz=binsz_deg,
        frame="icrs",
    )

    dataset = MapDataset.create(geom=geom)

    maker = MapDatasetMaker()
    safe_mask_maker = SafeMaskMaker(methods=["offset-max"], offset_max=2.5 * u.deg)

    for obs in observations:
        cutout = dataset.cutout(
            position=geom.center_skydir,
            width=(width_deg, width_deg),
        )

        cutout = maker.run(cutout, obs)
        cutout = safe_mask_maker.run(cutout, obs)

        dataset.stack(cutout)

    estimator = ExcessMapEstimator(
        correlation_radius=smoothing_sigma * u.deg,
    )

    result = estimator.run(dataset)

    return {
        "counts": result["counts"].data.tolist(),
        "excess": result["excess"].data.tolist(),
        "significance": result["sqrt_ts"].data.tolist(),
    }