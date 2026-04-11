from fastapi import APIRouter

from ...domain.schemas import Theta2Request, Theta2Response

router = APIRouter(tags=["theta2"])


@router.post("/theta2", response_model=Theta2Response)
def compute_theta2(request: Theta2Request) -> Theta2Response:
    return Theta2Response(
        dataset_id=request.dataset_id,
        message="Theta² endpoint stub ready for analysis_core.theta2 integration",
    )
