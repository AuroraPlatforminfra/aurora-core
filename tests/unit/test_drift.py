"""Tests for drift detector"""

import pytest
from src.aurora.drift.core import DriftDetector


@pytest.fixture
def drift_detector():
    return DriftDetector()


@pytest.mark.asyncio
async def test_drift_detected(drift_detector):
    """Test drift detection"""
    desired = {"spec": {"replicas": 3, "image": "model:v1.0"}}
    current = {"spec": {"replicas": 3, "image": "model:v1.1"}}
    
    report = await drift_detector.detect_drift(current, desired)
    assert report.drift_detected is True
    assert len(report.changes) > 0


@pytest.mark.asyncio
async def test_no_drift(drift_detector):
    """Test when no drift exists"""
    desired = {"spec": {"replicas": 3}}
    current = {"spec": {"replicas": 3}}
    
    report = await drift_detector.detect_drift(current, desired)
    assert report.drift_detected is False
    assert len(report.changes) == 0


@pytest.mark.asyncio
async def test_drift_id_unique(drift_detector):
    """Test drift ID is unique"""
    manifest = {"spec": {"replicas": 3}}
    report1 = await drift_detector.detect_drift(manifest, manifest)
    report2 = await drift_detector.detect_drift(manifest, manifest)
    assert report1.drift_id != report2.drift_id
