from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analysis_core.lightcurve.service import run_lightcurve
from backend.app.domain.data_loader import DataLoader
from backend.app.domain.schemas import LightCurveRequest
from backend.app.domain.dataset_registry import DatasetRegistry


def _get_data_root():
    root = Path(__file__).resolve()
    while not (root / "data").exists():
        root = root.parent
    return root


def _get_loader(root):
    registry = DatasetRegistry(root / "data/datasets.yml")
    return DataLoader(
        data_root=root / "data",
        registry=registry
    )


def test_lightcurve_basic():
    root = _get_data_root()
    data_loader = _get_loader(root)

    request = LightCurveRequest(
        dataset_id="hess-dl3-dr1",
        e_min_tev=0.1,
        e_max_tev=10,
        time_bin="30min"
    )

    response = run_lightcurve(request, data_loader)

    assert response.message == "Light curve generated successfully"
    assert len(response.data["time"]) > 0
    assert len(response.data["counts"]) == len(response.data["time"])
    assert len(response.data["flux"]) == len(response.data["time"])


def test_lightcurve_energy_filter_empty():
    root = _get_data_root()
    data_loader = _get_loader(root)

    request = LightCurveRequest(
        dataset_id="hess-dl3-dr1",
        e_min_tev=1000,
        e_max_tev=2000,
        time_bin="10min"
    )

    try:
        run_lightcurve(request, data_loader)
        assert False, "Expected ValueError for empty energy range"
    except ValueError as e:
        assert "No events in selected energy range" in str(e)


def test_lightcurve_time_bin_parsing():
    root = _get_data_root()
    data_loader = _get_loader(root)

    request = LightCurveRequest(
        dataset_id="hess-dl3-dr1",
        e_min_tev=0.1,
        e_max_tev=10,
        time_bin="1h"
    )

    response = run_lightcurve(request, data_loader)

    assert len(response.data["time"]) > 0


def test_lightcurve_plot_real_data():
    root = _get_data_root()
    data_loader = _get_loader(root)

    request = LightCurveRequest(
        dataset_id="hess-dl3-dr1",
        e_min_tev=0.05,
        e_max_tev=0.50,
        time_bin="720min"
    )

    response = run_lightcurve(request, data_loader)

    time = response.data["time"]

    assert len(time) > 0

    df = pd.DataFrame({
        "time": pd.to_datetime(response.data["time"]),
        "flux": response.data["flux"],
        "counts": response.data["counts"]
    })

    df = df.sort_values("time")

    #opcjonalnie: zakres lat (2004–2005)
    df = df[(df["time"] >= "2004-01-01") & (df["time"] <= "2005-01-01")]

    #  usuwanie zer
    df_plot = df[df["flux"] > 0]

    # --- wykres
    plt.figure(figsize=(12, 6))

    plt.step(df_plot["time"], df_plot["flux"], where="mid", label="Flux")

    plt.xlabel("Time")
    plt.ylabel("Flux")
    plt.title("Light Curve")

    ymax = np.percentile(df_plot["flux"], 95)
    plt.ylim(0, ymax * 1.2)

    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    test_lightcurve_basic()
    test_lightcurve_energy_filter_empty()
    test_lightcurve_time_bin_parsing()
    test_lightcurve_plot_real_data()