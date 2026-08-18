"""Drift detector"""

from typing import Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class Change:
    field: str
    current: Any
    desired: Any
    change_type: str


@dataclass
class DriftReport:
    drift_id: str
    drift_detected: bool
    changes: list[Change] = field(default_factory=list)
    latency_ms: float = 0.0
    confidence: float = 0.99
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DriftDetector:
    def __init__(self):
        self.ignore_paths = {"metadata.uid", "metadata.resourceVersion", "status"}

    async def detect_drift(
        self,
        current_manifest: dict,
        desired_manifest: dict,
    ) -> DriftReport:
        import time
        start = time.time()

        drift_id = f"drift-{uuid.uuid4().hex[:8]}"
        changes = []

        if current_manifest != desired_manifest:
            for key in desired_manifest:
                if desired_manifest.get(key) != current_manifest.get(key):
                    changes.append(
                        Change(
                            field=key,
                            current=current_manifest.get(key),
                            desired=desired_manifest.get(key),
                            change_type="value_mismatch",
                        )
                    )

        latency = (time.time() - start) * 1000

        return DriftReport(
            drift_id=drift_id,
            drift_detected=len(changes) > 0,
            changes=changes,
            latency_ms=round(latency, 2),
        )
