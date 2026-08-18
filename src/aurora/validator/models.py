from pydantic import BaseModel, Field
from typing import Optional

class ViolationModel(BaseModel):
    rule_id: str
    severity: str
    message: str
    remediation: str

class ValidationRequestModel(BaseModel):
    manifest: dict
    policies: Optional[list[str]] = Field(default=None)

class ValidationResponseModel(BaseModel):
    validation_id: str
    status: str
    violations: list[ViolationModel] = Field(default_factory=list)
    passed_rules: list[str] = Field(default_factory=list)
    latency_ms: float
    timestamp: str
