"""Pydantic models for remediation"""

from pydantic import BaseModel
from typing import Optional


class RemediationRequestModel(BaseModel):
    drift_report: dict
    desired_manifest: dict
    repo_url: str


class RemediationResponseModel(BaseModel):
    remediation_id: str
    status: str
    branch_name: Optional[str] = None
    pr_url: Optional[str] = None
    timestamp: str
