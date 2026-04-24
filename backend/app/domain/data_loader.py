from pathlib import Path

from astropy.io import fits
from astropy import units as u

from .dataset_registry import DatasetRegistry


class DataLoader:
    def __init__(self, data_root: Path, registry: DatasetRegistry):
        self.data_root = data_root
        self.registry = registry

    def validate_dataset(self, dataset_id: str) -> tuple[bool, str]:
        dataset = self.registry.get_dataset(dataset_id)
        dataset_path = self.data_root / dataset.datastore_path
        if not dataset_path.exists():
            return False, f"Dataset path does not exist: {dataset_path}"

        if dataset.dl3_index_required:
            hdu = dataset_path / "hdu-index.fits.gz"
            obs = dataset_path / "obs-index.fits.gz"
            if not hdu.exists() or not obs.exists():
                return (
                    False,
                    "Missing DL3 index files (hdu-index.fits.gz / obs-index.fits.gz).",
                )

        return True, "Dataset is valid"

    def load_events(self, dataset_id: str):
        dataset = self.registry.get_dataset(dataset_id)
        dataset_path = self.data_root / dataset.datastore_path

        events = []

        for file in dataset_path.rglob("*.fits.gz"):
            with fits.open(file) as hdul:

                if "EVENTS" not in hdul:
                    continue

                table = hdul["EVENTS"].data
                header = hdul["EVENTS"].header

                energy_unit = header.get("TUNIT5", "TeV")

                for row in table:
                    energy = row["ENERGY"]
                    energy = (energy * u.Unit(energy_unit)).to(u.TeV).value
                    events.append(
                        {
                            "energy": float(energy),
                            "instrument": dataset.instrument,
                        }
                    )

        return events