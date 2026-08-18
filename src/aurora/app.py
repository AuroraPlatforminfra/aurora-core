"""FastAPI application factory"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings


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
    
    @app.post("/v1/validate")
    async def validate(manifest: dict):
        """Validate deployment manifest"""
        return {
            "validation_id": "val-001",
            "status": "pending",
            "violations": []
        }
    
    @app.post("/v1/detect-drift")
    async def detect_drift(config: dict):
        """Detect configuration drift"""
        return {
            "drift_detected": False,
            "changes": []
        }
    
    @app.post("/v1/remediate")
    async def remediate(drift_report: dict):
        """Generate remediation PR"""
        return {
            "remediation_id": "rem-001",
            "pr_url": None,
            "status": "pending"
        }
    
    return app
