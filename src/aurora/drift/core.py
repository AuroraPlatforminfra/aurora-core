"""Drift detection logic"""

from typing import Any
from dataclasses import dataclass, field
from datetime import datetime
import uuid
from deepdiff import DeepDiff


@dataclass
class Change:
    """Configuration change"""
    field: str
    current: Any
    desired: Any
    change_type: str


@dataclass
class DriftReport:
    """Drift detection report"""
    drift_id: str
    drift_detected: bool
    changes: list[Change] = field(default_factory=list)
    latency_ms: float = 0.0
    confidence: float = 0.99
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class DriftDetector:
    """Detects configuration drift between Git and Kubernetes"""

    def __init__(self):
        self.ignore_paths = {
            "metadata.uid",
            "metadata.resourceVersion",
            "metadata.generation",
            "metadata.managedFields",
            "status",
        }

    async def detect_drift(
        self,
        current_manifest: dict,
        desired_manifest: dict,
    ) -> DriftReport:
        """Detect drift between current and desired state"""
        import time
        start = time.time()

        drift_id = f"drift-{uuid.uuid4().hex[:8]}"
        changes = []

        # Deep diff with ignored paths
        diff = DeepDiff(
            desired_manifest,
            current_manifest,
            ignore_order=True,
            exclude_paths=self.ignore_paths,
        )

        if diff:
            for change_type, change_details in diff.items():
                if change_type == "values_changed":
                    for path, values in change_details.items():
                        changes.append(
                            Change(
                                field=path.replace("root['", "").replace("']", ""),
                                current=values.get("new_value"),
                                desired=values.get("old_value"),
                                change_type="value_mismatch",
                            )
                        )
                elif change_type in ["dictionary_item_added", "dictionary_item_removed"]:
                    for path in change_details:
                        changes.append(
                            Change(
                                field=path,
                                current=None,
                                desired=None,
                                change_type=change_type,
                            )
                        )

        latency = (time.time() - start) * 1000

        return DriftReport(
            drift_id=drift_id,
            drift_detected=len(changes) > 0,
            changes=changes,
            latency_ms=round(latency, 2),
            confidence=0.99 if changes else 1.0,
        )
