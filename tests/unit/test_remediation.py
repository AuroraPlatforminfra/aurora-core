"""Tests for remediation engine"""

import pytest
from src.aurora.remediation.core import RemediationEngine


@pytest.fixture
def remediation_engine():
    return RemediationEngine()


@pytest.mark.asyncio
async def test_generate_plan(remediation_engine):
    """Test remediation plan generation"""
    drift_report = {
        "changes": [
            {"field": "spec.replicas", "current": 3, "desired": 2},
        ]
    }
    desired = {"spec": {"replicas": 2}}
    
    plan = await remediation_engine.generate_plan(
        drift_report, desired, "https://github.com/test/repo"
    )
    
    assert plan.remediation_id.startswith("rem-")
    assert plan.status == "proposed"
    assert "aurora/remediation" in plan.branch_name


@pytest.mark.asyncio
async def test_plan_id_unique(remediation_engine):
    """Test remediation ID is unique"""
    drift = {"changes": []}
    manifest = {}
    
    plan1 = await remediation_engine.generate_plan(drift, manifest, "https://test")
    plan2 = await remediation_engine.generate_plan(drift, manifest, "https://test")
    
    assert plan1.remediation_id != plan2.remediation_id
