from fastapi import APIRouter

from ...domain.schemas import SkyMapRequest, SkyMapResponse

router = APIRouter(tags=["skymap"])


@router.post("/skymap", response_model=SkyMapResponse)
def compute_skymap(request: SkyMapRequest) -> SkyMapResponse:
    return SkyMapResponse(
        dataset_id=request.dataset_id,
        message="Sky map endpoint stub ready for analysis_core.skymap integration",
    )