from pathlib import Path

import yaml

from .schemas import DatasetInfo


class DatasetRegistry:
    def __init__(self, registry_path: Path):
        self.registry_path = registry_path

    def list_datasets(self) -> list[DatasetInfo]:
        if not self.registry_path.exists():
            return []

        payload = yaml.safe_load(self.registry_path.read_text()) or {}
        datasets = payload.get("datasets", [])
        return [DatasetInfo(**row) for row in datasets]

    def get_dataset(self, dataset_id: str) -> DatasetInfo:
        for dataset in self.list_datasets():
            if dataset.id == dataset_id:
                return dataset
        raise KeyError(f"Dataset '{dataset_id}' not found")
