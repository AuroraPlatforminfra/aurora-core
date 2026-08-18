"""Validator core"""

from typing import Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class Violation:
    rule_id: str
    severity: str
    message: str
    remediation: str


@dataclass
class ValidationResult:
    validation_id: str
    status: str
    violations: list[Violation] = field(default_factory=list)
    passed_rules: list[str] = field(default_factory=list)
    latency_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class Validator:
    def __init__(self):
        self.policies = {
            "rbac": self._validate_rbac,
            "network_isolation": self._validate_network,
        }

    async def validate(self, manifest: dict, policies: list[str] | None = None) -> ValidationResult:
        import time
        start = time.time()
        validation_id = f"val-{uuid.uuid4().hex[:8]}"
        violations = []
        passed = []

        policies_to_check = policies or list(self.policies.keys())

        for policy_name in policies_to_check:
            if policy_name not in self.policies:
                continue
            result = self.policies[policy_name](manifest)
            if result:
                violations.extend(result)
            else:
                passed.append(policy_name)

        latency = (time.time() - start) * 1000

        return ValidationResult(
            validation_id=validation_id,
            status="failed" if violations else "passed",
            violations=violations,
            passed_rules=passed,
            latency_ms=round(latency, 2),
        )

    def _validate_rbac(self, manifest: dict) -> list[Violation]:
        violations = []
        if manifest.get("kind") == "ServiceAccount":
            roles = manifest.get("roleBindings", [])
            for role in roles:
                if role.get("name") == "cluster-admin":
                    violations.append(
                        Violation(
                            rule_id="rbac-001",
                            severity="critical",
                            message="ServiceAccount has cluster-admin",
                            remediation="Remove cluster-admin",
                        )
                    )
        return violations

    def _validate_network(self, manifest: dict) -> list[Violation]:
        return []
