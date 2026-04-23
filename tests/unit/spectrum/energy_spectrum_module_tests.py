from pathlib import Path
import matplotlib.pyplot as plt

from analysis_core.spectrum.service import EnergySpectrumModule
from backend.app.domain.schemas import SpectrumRequest
from backend.app.domain.data_loader import DataLoader
from backend.app.domain.dataset_registry import DatasetRegistry

class FakeDataLoader:
    def __init__(self, events):
        self._events = events

    def validate_dataset(self, dataset_id):
        return True, "ok"

    def load_events(self, dataset_id):
        return self._events


def test_basic_binning():
    events = [
        {"energy": 0.2, "instrument": "A"},
        {"energy": 1.0, "instrument": "A"},
        {"energy": 5.0, "instrument": "A"},
    ]

    module = EnergySpectrumModule(FakeDataLoader(events))

    module.config(
        SpectrumRequest(
            dataset_id="test",
            e_min_tev=0.1,
            e_max_tev=10,
            n_bins=3
        )
    )

    result = module.run()

    assert len(result.data["counts"]) == 3
    assert result.dataset_id == "test"
    assert result.message == "Energy spectrum generated"


def test_instrument_filter():
    events = [
        {"energy": 1.0, "instrument": "A"},
        {"energy": 1.0, "instrument": "B"},
    ]

    module = EnergySpectrumModule(FakeDataLoader(events))

    module.config(
        SpectrumRequest(
            dataset_id="test",
            e_min_tev=0.1,
            e_max_tev=10,
            n_bins=3,
            instruments=["A"]
        )
    )

    result = module.run()

    assert sum(result.data["counts"]) == 1
    assert result.dataset_id == "test"


def test_empty_result():
    events = [
        {"energy": 1.0, "instrument": "A"}
    ]

    module = EnergySpectrumModule(FakeDataLoader(events))

    module.config(
        SpectrumRequest(
            dataset_id="test",
            e_min_tev=10,
            e_max_tev=20,
            n_bins=3
        )
    )

    result = module.run()

    assert result.data["counts"] == []
    assert result.message == "No events in selected energy range"

def test_real_dataset_spectrum_plot():

    root = Path(__file__).resolve()
    while not (root / "data").exists():
        root = root.parent

    registry = DatasetRegistry(
        root / "data/datasets.yml"
    )

    data_loader = DataLoader(
        data_root=root / "data",
        registry=registry
    )

    module = EnergySpectrumModule(data_loader)

    module.config(
        SpectrumRequest(
            dataset_id="hess-dl3-dr1",
            e_min_tev=0.05,
            e_max_tev=20,
            n_bins=20
        )
    )

    result = module.run()

    edges = result.data["bin_edges"]
    counts = result.data["counts"]

    assert len(counts) > 0

    plt.figure()
    plt.step(edges[:-1], counts, where="post")
    plt.xscale("log")
    plt.xlabel("Energy (TeV)")
    plt.ylabel("Counts")
    plt.title("HESS DL3 DR1 Energy Spectrum")

    plt.show()

if __name__ == "__main__":
    test_basic_binning()
    test_instrument_filter()
    test_empty_result()
    test_real_dataset_spectrum_plot()