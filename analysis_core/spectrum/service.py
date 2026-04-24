import numpy as np

from backend.app.domain.schemas import (
    SpectrumRequest,
    SpectrumResponse
)


class EnergySpectrumModule:

    def __init__(self, data_loader):
        self.data_loader = data_loader

        self.dataset_id = None
        self.instruments = None
        self.bins = None
        self.energy_max = None
        self.energy_min = None

    def config(self, request: SpectrumRequest):
        self.dataset_id = request.dataset_id
        self.energy_min = request.e_min_tev
        self.energy_max = request.e_max_tev
        self.bins = request.n_bins
        self.instruments = request.instruments

    def run(self) -> SpectrumResponse:
        valid, message = self.data_loader.validate_dataset(self.dataset_id)

        if not valid:
            return SpectrumResponse(
                dataset_id=self.dataset_id,
                message=message,
                data={}
            )

        events = self.data_loader.load_events(self.dataset_id)

        filtered = events

        if self.instruments:
            filtered = [
                e for e in filtered
                if e["instrument"] in self.instruments
            ]

        filtered = [
            e for e in filtered
            if self.energy_min <= e["energy"] <= self.energy_max
        ]

        energies = [e["energy"] for e in filtered]

        if not energies:
            return SpectrumResponse(
                dataset_id=self.dataset_id,
                message="No events in selected energy range",
                data={
                    "bin_edges": [],
                    "counts": []
                }
            )

        bins = np.logspace(
            np.log10(self.energy_min),
            np.log10(self.energy_max),
            self.bins + 1
        )

        hist, edges = np.histogram(energies, bins=bins)

        return SpectrumResponse(
            dataset_id=self.dataset_id,
            message="Energy spectrum generated",
            data={
                "bin_edges": edges.tolist(),
                "counts": hist.tolist()
            }
        )