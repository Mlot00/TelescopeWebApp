from fastapi import APIRouter, Depends, HTTPException

from ...domain.data_loader import DataLoader
from ...domain.dataset_registry import DatasetRegistry
from ...domain.schemas import DatasetInfo, ObservationInfo
from ...main import get_data_loader, get_registry

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get("", response_model=list[DatasetInfo])
def list_datasets(registry: DatasetRegistry = Depends(get_registry)) -> list[DatasetInfo]:
    return registry.list_datasets()


@router.get("/{dataset_id}/observations", response_model=list[ObservationInfo])
def list_observations(
    dataset_id: str,
    loader: DataLoader = Depends(get_data_loader),
) -> list[ObservationInfo]:
    try:
        ok, message = loader.validate_dataset(dataset_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if not ok:
        raise HTTPException(status_code=400, detail=message)
    return loader.list_observations(dataset_id)
