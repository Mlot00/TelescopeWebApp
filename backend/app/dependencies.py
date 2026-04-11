from fastapi import Depends

from .core.config import Settings, get_settings
from .domain.data_loader import DataLoader
from .domain.dataset_registry import DatasetRegistry


def get_registry(settings: Settings = Depends(get_settings)) -> DatasetRegistry:
    return DatasetRegistry(settings.datasets_file)


def get_data_loader(
    settings: Settings = Depends(get_settings),
    registry: DatasetRegistry = Depends(get_registry),
) -> DataLoader:
    return DataLoader(data_root=settings.data_dir, registry=registry)
