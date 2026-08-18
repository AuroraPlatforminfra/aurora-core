"""Pydantic models for drift detection"""

from pydantic import BaseModel
from typing import Optional, Any


class ChangeModel(BaseModel):
    field: str
    current: Optional[Any] = None
    desired: Optional[Any] = None
    change_type: str


class DriftRequestModel(BaseModel):
    current_manifest: dict
    desired_manifest: dict


class DriftResponseModel(BaseModel):
    drift_id: str
    drift_detected: bool
    changes: list[ChangeModel]
    latency_ms: float
    confidence: float
    timestamp: str
