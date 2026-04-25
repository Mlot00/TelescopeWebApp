from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "telescope-webapp-api"


class DatasetInfo(BaseModel):
    id: str
    title: str
    instrument: str
    source: str
    datastore_path: str
    dl3_index_required: bool = True


class ObservationInfo(BaseModel):
    obs_id: int
    start_time: datetime | None = None
    end_time: datetime | None = None


class Theta2Request(BaseModel):
    dataset_id: str
    theta2_max: float = Field(default=0.3, gt=0)
    n_bins: int = Field(default=30, ge=5, le=300)


class Theta2Response(BaseModel):
    dataset_id: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)


class SkyMapRequest(BaseModel):
    dataset_id: str
    width_deg: float = Field(default=3.0, gt=0)
    binsz_deg: float = Field(default=0.02, gt=0)
    energy_min_tev: float = Field(default=0.5, gt=0)
    energy_max_tev: float = Field(default=10.0, gt=0)
    ring_r_in_deg: float = Field(default=0.5, gt=0)
    ring_width_deg: float = Field(default=0.3, gt=0)
    exclusion_radius_deg: float = Field(default=0.3, gt=0)
    correlation_radius_deg: float = Field(default=0.1, gt=0)
    offset_max_deg: float = Field(default=2.5, gt=0)

class SkyMapResponse(BaseModel):
    dataset_id: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)


class SpectrumRequest(BaseModel):
    dataset_id: str
    e_min_tev: float = Field(default=0.05, gt=0)
    e_max_tev: float = Field(default=20.0, gt=0)
    n_bins: int = Field(default=12, ge=3, le=100)
    instruments: list[str] = Field(default_factory=list)


class SpectrumResponse(BaseModel):
    dataset_id: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)


class LightCurveRequest(BaseModel):
    dataset_id: str
    e_min_tev: float = Field(default=0.05, gt=0)
    e_max_tev: float = Field(default=20.0, gt=0)
    time_bin: str = "1d"


class LightCurveResponse(BaseModel):
    dataset_id: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
