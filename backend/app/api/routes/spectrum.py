from fastapi import APIRouter

from ...domain.schemas import SpectrumRequest, SpectrumResponse

router = APIRouter(tags=["spectrum"])


@router.post("/spectrum", response_model=SpectrumResponse)
def compute_spectrum(request: SpectrumRequest) -> SpectrumResponse:
    return SpectrumResponse(
        dataset_id=request.dataset_id,
        message="Spectrum endpoint stub ready for analysis_core.spectrum integration",
    )
