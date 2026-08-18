"""Unit tests for FastAPI app"""

import pytest
from src.aurora.app import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def client(app):
    from fastapi.testclient import TestClient
    return TestClient(app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_ready(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["ready"] is True


def test_validate_endpoint(client):
    response = client.post("/v1/validate", json={"manifest": {}})
    assert response.status_code == 200
    assert "validation_id" in response.json()


def test_drift_endpoint(client):
    response = client.post(
        "/v1/detect-drift",
        json={"current_manifest": {}, "desired_manifest": {}}
    )
    assert response.status_code == 200
    assert "drift_id" in response.json()


def test_remediate_endpoint(client):
    response = client.post(
        "/v1/remediate",
        json={
            "drift_report": {},
            "desired_manifest": {},
            "repo_url": "https://github.com/test/repo"
        }
    )
    assert response.status_code == 200
    assert "remediation_id" in response.json()
