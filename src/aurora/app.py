"""FastAPI application factory"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .validator.core import Validator
from .validator.models import ValidationRequestModel, ValidationResponseModel
from .drift.core import DriftDetector
from .drift.models import DriftRequestModel, DriftResponseModel
from .remediation.core import RemediationEngine
from .remediation.models import RemediationRequestModel, RemediationResponseModel


validator = Validator()
drift_detector = DriftDetector()
remediation_engine = RemediationEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic"""
    print(f"[startup] {settings.app_name} v{settings.app_version}")
    yield
    print("[shutdown] Aurora Core")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/health")
    async def health():
        return {"status": "healthy"}
    
    @app.get("/ready")
    async def ready():
        return {"ready": True}
    
    @app.post("/v1/validate", response_model=ValidationResponseModel)
    async def validate(request: ValidationRequestModel):
        """Validate deployment manifest"""
        result = await validator.validate(request.manifest, request.policies)
        return {
            "validation_id": result.validation_id,
            "status": result.status,
            "violations": [
                {
                    "rule_id": v.rule_id,
                    "severity": v.severity,
                    "message": v.message,
                    "remediation": v.remediation,
                }
                for v in result.violations
            ],
            "passed_rules": result.passed_rules,
            "latency_ms": result.latency_ms,
            "timestamp": result.timestamp,
        }
    
    @app.post("/v1/detect-drift", response_model=DriftResponseModel)
    async def detect_drift(request: DriftRequestModel):
        """Detect configuration drift"""
        result = await drift_detector.detect_drift(
            request.current_manifest,
            request.desired_manifest,
        )
        return {
            "drift_id": result.drift_id,
            "drift_detected": result.drift_detected,
            "changes": [
                {
                    "field": c.field,
                    "current": c.current,
                    "desired": c.desired,
                    "change_type": c.change_type,
                }
                for c in result.changes
            ],
            "latency_ms": result.latency_ms,
            "confidence": result.confidence,
            "timestamp": result.timestamp,
        }
    
    @app.post("/v1/remediate", response_model=RemediationResponseModel)
    async def remediate(request: RemediationRequestModel):
        """Generate remediation plan"""
        plan = await remediation_engine.generate_plan(
            request.drift_report,
            request.desired_manifest,
            request.repo_url,
        )
        return {
            "remediation_id": plan.remediation_id,
            "status": plan.status,
            "branch_name": plan.branch_name,
            "pr_url": plan.pr_url,
            "timestamp": plan.timestamp,
        }
    
    return app
