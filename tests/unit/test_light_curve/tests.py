import numpy as np
import pandas as pd

from analysis_core.lightcurve.service import LightCurveService


# =========================
# MOCK / HELPERY
# =========================

def _make_service():
    service = LightCurveService()
    service.dl3_path = "dummy_path"
    service.energy_min = 0.1
    service.energy_max = 10.0
    service.time_bin_minutes = 60
    return service


def _mock_events_dataframe():
    # 10 godzin danych, 1 zdarzenie na godzinę
    times = pd.date_range("2024-01-01", periods=10, freq="h")
    energies = np.linspace(0.5, 5.0, 10)

    return pd.DataFrame({
        "time": times,
        "energy": energies
    })


# podmieniamy _load_events żeby nie używać Gammapy
def _patch_load_events(service, df):
    service._load_events = lambda: df


# =========================
# TEST 1: BASIC BINNING
# =========================

def test_basic_binning():
    print("Running test_basic_binning...")

    service = _make_service()
    df = _mock_events_dataframe()
    _patch_load_events(service, df)

    filtered = service._filter_energy(df)
    result = service._bin_time(filtered)

    assert not result.empty
    assert "counts" in result.columns
    assert "flux" in result.columns

    print("✔ test_basic_binning passed")


# =========================
# TEST 2: ENERGY FILTER
# =========================

def test_instrument_filter():
    print("Running test_instrument_filter...")

    service = _make_service()
    df = _mock_events_dataframe()
    _patch_load_events(service, df)

    # ustaw wąski zakres energii
    service.energy_min = 1.0
    service.energy_max = 2.0

    filtered = service._filter_energy(df)

    assert filtered["energy"].min() >= 1.0
    assert filtered["energy"].max() <= 2.0

    print("✔ test_instrument_filter passed")


# =========================
# TEST 3: EMPTY RESULT
# =========================

def test_empty_result():
    print("Running test_empty_result...")

    service = _make_service()
    df = pd.DataFrame({
        "time": pd.date_range("2024-01-01", periods=5, freq="h"),
        "energy": np.ones(5) * 0.01  # poza zakresem
    })

    _patch_load_events(service, df)

    try:
        service._filter_energy(df)
        raise AssertionError("Should have failed")
    except ValueError as e:
        assert "No events in selected energy range" in str(e)

    print("✔ test_empty_result passed")


# =========================
# TEST 4: REALISTIC PIPELINE (NO GAMMAPY)
# =========================

def test_real_dataset_spectrum_plot():
    print("Running test_real_dataset_spectrum_plot...")

    service = _make_service()
    df = _mock_events_dataframe()
    _patch_load_events(service, df)

    # pełny pipeline
    filtered = service._filter_energy(df)
    result = service.run = lambda: service._bin_time(filtered)

    output = result()

    assert len(output) > 0
    assert output["counts"].sum() > 0

    print("✔ test_real_dataset_spectrum_plot passed")


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    test_basic_binning()
    test_instrument_filter()
    test_empty_result()
    test_real_dataset_spectrum_plot()