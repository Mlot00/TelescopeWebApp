from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from analysis_core.skymap.service import (
    _DEFAULT_COORD,
    _SOURCE_COORDS,
    _get_source_coord,
    run_skymap,
)


class TestGetSourceCoord:

    def test_known_key_exact(self):
        ra, dec = _get_source_coord("hess-dl3-dr1")
        assert (ra, dec) == _SOURCE_COORDS["hess-dl3-dr1"]

    def test_known_key_substring(self):
        ra, dec = _get_source_coord("my_project_hess-dl3-dr1_v2")
        assert (ra, dec) == _SOURCE_COORDS["hess-dl3-dr1"]

    def test_known_key_case_insensitive(self):
        ra, dec = _get_source_coord("hess-dl3-dr1")
        assert (ra, dec) == _SOURCE_COORDS["hess-dl3-dr1"]

    def test_crab_sample(self):
        ra, dec = _get_source_coord("crab_sample")
        assert (ra, dec) == _SOURCE_COORDS["crab_sample"]

    def test_magic_crab(self):
        ra, dec = _get_source_coord("magic_crab")
        assert (ra, dec) == _SOURCE_COORDS["magic_crab"]

    def test_hess_rx_j1713(self):
        ra, dec = _get_source_coord("hess_rx_j1713")
        assert (ra, dec) == _SOURCE_COORDS["hess_rx_j1713"]

    def test_unknown_key_returns_default(self):
        ra, dec = _get_source_coord("totally_unknown_source")
        assert (ra, dec) == _DEFAULT_COORD

    def test_empty_string_returns_default(self):
        ra, dec = _get_source_coord("")
        assert (ra, dec) == _DEFAULT_COORD

    def test_default_coord_values(self):
        assert _DEFAULT_COORD == (83.633, 22.014)

    def test_source_coords_not_empty(self):
        assert len(_SOURCE_COORDS) > 0

    def test_all_registered_keys_resolve(self):
        for key, expected in _SOURCE_COORDS.items():
            result = _get_source_coord(key)
            assert result == expected, f"Klucz '{key}' nie rozwiązał się poprawnie"


def _make_mock_map(data_2d: np.ndarray):
    m = MagicMock()
    m.data = data_2d[np.newaxis, :, :]
    return m


def _make_result_maps(sig_data: np.ndarray, excess_data: np.ndarray):
    maps = {}
    maps["sqrt_ts"] = _make_mock_map(sig_data)
    maps["npred_excess"] = _make_mock_map(excess_data)
    return maps


@pytest.fixture()
def mock_gammapy(monkeypatch):
    sig_data = np.array([[1.0, 2.0], [3.0, 4.0]])
    excess_data = np.array([[10.0, 20.0], [30.0, 40.0]])
    counts_data = np.array([[5.0, 6.0], [7.0, 8.0]])
    bkg_data = np.array([[1.0, 2.0], [3.0, 4.0]])

    stacked_onoff = MagicMock()
    stacked_onoff.counts = _make_mock_map(counts_data)
    stacked_onoff.counts_off = _make_mock_map(bkg_data)

    obs = MagicMock()
    obs.obs_id = 42

    cutout = MagicMock()
    cutout.cutout.return_value = cutout
    cutout.to_image.return_value = cutout

    datastore = MagicMock()
    datastore.get_observations.return_value = [obs]

    dataset_empty = MagicMock()
    dataset_empty.cutout.return_value = cutout

    maker = MagicMock()
    maker.run.return_value = cutout

    safe_mask_maker = MagicMock()
    safe_mask_maker.run.return_value = cutout

    ring_maker = MagicMock()
    ring_maker.run.return_value = stacked_onoff

    estimator = MagicMock()
    estimator.run.return_value = _make_result_maps(sig_data, excess_data)

    patches = {
        "DataStore": patch(
            "analysis_core.skymap.service.DataStore",
            return_value=datastore,
        ),
        "DataStore_from_dir": patch(
            "analysis_core.skymap.service.DataStore.from_dir",
            return_value=datastore,
        ),
        "MapDataset_create": patch(
            "analysis_core.skymap.service.MapDataset.create",
            return_value=dataset_empty,
        ),
        "MapDatasetMaker": patch(
            "analysis_core.skymap.service.MapDatasetMaker",
            return_value=maker,
        ),
        "SafeMaskMaker": patch(
            "analysis_core.skymap.service.SafeMaskMaker",
            return_value=safe_mask_maker,
        ),
        "RingBackgroundMaker": patch(
            "analysis_core.skymap.service.RingBackgroundMaker",
            return_value=ring_maker,
        ),
        "ExcessMapEstimator": patch(
            "analysis_core.skymap.service.ExcessMapEstimator",
            return_value=estimator,
        ),
    }

    started = {k: p.start() for k, p in patches.items()}
    yield {
        "mocks": started,
        "stacked_onoff": stacked_onoff,
        "sig_data": sig_data,
        "excess_data": excess_data,
        "counts_data": counts_data,
        "bkg_data": bkg_data,
        "observations": [obs],
        "estimator": estimator,
        "ring_maker": ring_maker,
    }
    for p in patches.values():
        p.stop()


class TestRunSkymapReturnStructure:

    def test_returns_dict(self, mock_gammapy):
        result = run_skymap("/fake/path", "crab_sample")
        assert isinstance(result, dict)

    def test_has_all_required_keys(self, mock_gammapy):
        result = run_skymap("/fake/path", "crab_sample")
        assert set(result.keys()) == {"counts", "background", "excess", "significance", "stats"}

    def test_significance_is_list_of_lists(self, mock_gammapy):
        result = run_skymap("/fake/path", "crab_sample")
        sig = result["significance"]
        assert isinstance(sig, list)
        assert all(isinstance(row, list) for row in sig)

    def test_counts_is_list_of_lists(self, mock_gammapy):
        result = run_skymap("/fake/path", "crab_sample")
        assert isinstance(result["counts"], list)

    def test_background_is_list_of_lists(self, mock_gammapy):
        result = run_skymap("/fake/path", "crab_sample")
        assert isinstance(result["background"], list)

    def test_excess_is_list_of_lists(self, mock_gammapy):
        result = run_skymap("/fake/path", "crab_sample")
        assert isinstance(result["excess"], list)


class TestRunSkymapStats:

    def test_stats_has_all_keys(self, mock_gammapy):
        result = run_skymap("/fake/path", "crab_sample")
        stats = result["stats"]
        expected_keys = {
            "n_counts",
            "n_background",
            "n_excess",
            "significance_max",
            "significance_mean",
            "n_observations",
        }
        assert expected_keys.issubset(set(stats.keys()))

    def test_n_observations_matches_mock(self, mock_gammapy):
        result = run_skymap("/fake/path", "crab_sample")
        assert result["stats"]["n_observations"] == 1

    def test_significance_max_is_float(self, mock_gammapy):
        result = run_skymap("/fake/path", "crab_sample")
        assert isinstance(result["stats"]["significance_max"], float)

    def test_significance_mean_is_float(self, mock_gammapy):
        result = run_skymap("/fake/path", "crab_sample")
        assert isinstance(result["stats"]["significance_mean"], float)

    def test_n_counts_is_int(self, mock_gammapy):
        result = run_skymap("/fake/path", "crab_sample")
        assert isinstance(result["stats"]["n_counts"], int)

    def test_significance_max_correct_value(self, mock_gammapy):
        result = run_skymap("/fake/path", "crab_sample")
        expected = float(round(mock_gammapy["sig_data"].max(), 2))
        assert result["stats"]["significance_max"] == expected

    def test_significance_mean_correct_value(self, mock_gammapy):
        result = run_skymap("/fake/path", "crab_sample")
        expected = float(round(mock_gammapy["sig_data"].mean(), 2))
        assert result["stats"]["significance_mean"] == expected

    def test_n_counts_correct_value(self, mock_gammapy):
        result = run_skymap("/fake/path", "crab_sample")
        expected = int(mock_gammapy["counts_data"].sum())
        assert result["stats"]["n_counts"] == expected


class TestRunSkymapNanHandling:

    def test_nan_in_significance_replaced_with_zero(self, mock_gammapy, monkeypatch):
        nan_data = np.array([[np.nan, 1.0], [2.0, np.nan]])

        stacked_onoff = mock_gammapy["stacked_onoff"]
        stacked_onoff.counts = _make_mock_map(np.zeros((2, 2)))
        stacked_onoff.counts_off = _make_mock_map(np.zeros((2, 2)))

        mock_gammapy["mocks"]["ExcessMapEstimator"].run.return_value = (
            _make_result_maps(nan_data, np.zeros((2, 2)))
        )

        result = run_skymap("/fake/path", "crab_sample")
        sig_flat = np.array(result["significance"]).ravel()
        assert not np.any(np.isnan(sig_flat)), "NaN nie zostały zastąpione zerem"


class TestRunSkymapNoObservations:

    def test_raises_runtime_error_when_no_observations(self, mock_gammapy):
        mock_gammapy["mocks"]["DataStore_from_dir"].get_observations.return_value = []

        with patch("analysis_core.skymap.service.DataStore.from_dir") as mock_ds:
            ds = MagicMock()
            ds.get_observations.return_value = []
            mock_ds.return_value = ds

            mock_gammapy["ring_maker"].run.return_value = None

            with pytest.raises(RuntimeError, match="No observations processed"):
                run_skymap("/fake/path", "empty_dataset")


class TestRunSkymapParameters:

    def test_custom_width_passed(self, mock_gammapy):
        run_skymap("/fake/path", "crab_sample", width_deg=5.0)

    def test_custom_energy_range(self, mock_gammapy):
        run_skymap("/fake/path", "crab_sample", energy_min_tev=1.0, energy_max_tev=20.0)

    def test_all_params_accepted(self, mock_gammapy):
        run_skymap(
            "/fake/path",
            "hess-dl3-dr1",
            width_deg=4.0,
            binsz_deg=0.05,
            energy_min_tev=0.3,
            energy_max_tev=15.0,
            ring_r_in_deg=0.6,
            ring_width_deg=0.4,
            exclusion_radius_deg=0.2,
            correlation_radius_deg=0.15,
            offset_max_deg=3.0,
        )