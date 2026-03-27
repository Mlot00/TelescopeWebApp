from pathlib import Path

from .dataset_registry import DatasetRegistry
from .schemas import ObservationInfo


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
                    "Missing DL3 index files (hdu-index.fits.gz / obs-index.fits.gz). "
                    "Generate them before running analysis.",
                )

        return True, "Dataset is valid"

    def list_observations(self, dataset_id: str) -> list[ObservationInfo]:
        valid, _ = self.validate_dataset(dataset_id)
        if not valid:
            return []
        return []
