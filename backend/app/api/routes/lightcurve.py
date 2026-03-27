from fastapi import APIRouter

from ...domain.schemas import LightCurveRequest, LightCurveResponse

router = APIRouter(tags=["lightcurve"])


@router.post("/lightcurve", response_model=LightCurveResponse)
def compute_lightcurve(request: LightCurveRequest) -> LightCurveResponse:
    return LightCurveResponse(
        dataset_id=request.dataset_id,
        message="Light curve endpoint stub ready for analysis_core.lightcurve integration",
    )
