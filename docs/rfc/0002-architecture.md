# RFC-0002: Aurora Core Architecture

**Status:** Accepted
**Date:** 2026-07-28
**Author:** Edwin Jonathan
**Reviewers:** TBD

## System Overview

Client (CLI / GitHub Actions)
↓
FastAPI Server (8000)
├── Validator Service
├── Drift Detector
├── Remediation Engine
└── Observability Bridge (OpenTelemetry)
↓
PostgreSQL (audit logs, policy versions)
↓
GitHub API (read configs, create PRs)
↓
Kubernetes API (read deployed state)


## Component Descriptions

### 1. Validator Service

**Purpose**: Accept deployment manifest, apply security rules, return pass/fail + violations.

**Input**: 
```json
{
  "namespace": "default",
  "deployment": {
    "apiVersion": "apps/v1",
    "kind": "Deployment",
    "metadata": {...},
    "spec": {...}
  },
  "policies": ["rbac", "network_isolation", "secret_rotation"]
}
```

**Output**:
```json
{
  "validation_id": "val-uuid",
  "status": "failed",
  "violations": [
    {
      "rule_id": "rbac-001",
      "severity": "critical",
      "message": "ServiceAccount has cluster-admin role",
      "remediation": "Remove cluster-admin, use namespace-scoped role"
    }
  ],
  "passed_rules": ["network_isolation", "secret_rotation"],
  "latency_ms": 45
}
```

**Tech**: Python + OPA (Open Policy Agent)

### 2. Drift Detector

**Purpose**: Compare deployed state (Kubernetes) against desired state (Git).

**Algorithm**:
1. Fetch deployed manifest from Kubernetes API
2. Fetch desired manifest from Git (GitHub repo)
3. Deep diff (ignore metadata, focus on spec)
4. Detect changes in: image, resources, env vars, replicas, RBAC, network policy
5. Return drift report

**Output**:
```json
{
  "drift_detected": true,
  "changes": [
    {
      "field": "spec.template.spec.containers[0].image",
      "current": "model:v1.0",
      "desired": "model:v1.1",
      "type": "version_mismatch"
    }
  ],
  "latency_ms": 120,
  "confidence": 0.99
}
```

**Tech**: Python + PyGithub + Kubernetes Python client

### 3. Remediation Engine

**Purpose**: When drift detected, generate GitHub PR with fixes.

**Workflow**:
1. Analyze drift report
2. Generate corrected manifest
3. Create new branch
4. Commit corrected manifest
5. Open PR with description
6. Return PR URL

**Output**:
```json
{
  "remediation_id": "rem-uuid",
  "pr_url": "https://github.com/org/repo/pull/42",
  "status": "proposed",
  "changes_summary": "Updated image from v1.0 to v1.1"
}
```

**Tech**: Python + PyGithub

### 4. Observability Bridge

**Purpose**: Emit structured metrics, traces, logs on every operation.

**Signals**:
- **Metrics** (Prometheus): aurora_validation_duration_ms, aurora_validation_failures_total, aurora_drift_detected_total
- **Traces** (OpenTelemetry): Full request path tracing
- **Logs** (structured JSON): Timestamp, level, service, component, trace_id, message

**Tech**: OpenTelemetry Python SDK

## API Contract

### POST /v1/validate
Validate deployment manifest against security policies.

### POST /v1/detect-drift
Compare deployed state against Git source of truth.

### POST /v1/remediate
Generate GitHub PR with configuration fixes.

## Threat Model

**Threats**:
1. Unvalidated manifest input → Mitigation: Input validation at API boundary
2. Git repository compromise → Mitigation: Sign commits, verify ownership
3. Kubernetes API access → Mitigation: Pod runs with minimal RBAC
4. Data exposure in logs → Mitigation: Structured logging with redaction
5. Unreviewed remediation PRs → Mitigation: User approval required

## Failure Modes & Recovery

| Failure | Impact | Recovery |
|---------|--------|----------|
| Validator crashes | Deployments blocked | Health check fails, alert, manual bypass |
| Drift detector timeout | Detection fails | Retry with exponential backoff, fail open |
| PR creation fails | Config not fixed | Log error, emit alert |
| PostgreSQL unavailable | Audit logs not persisted | In-memory cache, replay on recovery |
| GitHub token revoked | Can't create PRs | Fail open, request new token |

## Deployment Topology (MVP)

GCP GKE Cluster (or k3s)
├── aurora-core namespace
│ ├── FastAPI Pod (3 replicas)
│ ├── PostgreSQL StatefulSet
│ ├── Prometheus (scrape /metrics)
│ └── Jaeger (OTEL traces)
│
└── External Services
├── GitHub (API)
└── GCP Secret Manager


## Scalability Notes

- Single-node k3s MVP: ~100 validations/sec
- Production k3s (3 nodes): ~10,000 validations/sec with p99 < 500ms
- Cost: GCP n1-standard-2 (3 nodes) ~ $300/month

## Security Baseline

- Pod Security Standard: restricted
- Network Policy: deny-all default
- RBAC: minimal permissions
- Secrets: GitHub token via Secret Manager
- Artifact signing: Cosign
- SBOM: every build

## Observability Baseline

- Metrics: Prometheus scrape every 30s
- Traces: OpenTelemetry to Jaeger (100% sampling MVP, <10% production)
- Logs: Structured JSON to stdout
- Alerting: Prometheus + AlertManager (p99 > 500ms, error rate > 1%)

## Open Questions (Post-MVP)

- Multi-cloud policy inheritance? (RFC-0003)
- Should remediation PRs be signed? (ADR in implementation)
- How to version policies for rollback? (RFC-0003)
