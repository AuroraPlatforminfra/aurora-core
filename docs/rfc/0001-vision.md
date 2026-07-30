# RFC-0001: Aurora Vision

**Status:** Accepted
**Date:** 2026-07-28
**Author:** Edwin Jonathan
**Reviewers:** TBD

## Problem

African AI teams deploying production models face three critical infrastructure gaps:

1. **No Policy Engine**: Cannot enforce security baseline at deployment time. Models deployed with overprivileged RBAC, plaintext secrets, no network isolation.
2. **No Drift Detection**: Configuration diverges from source of truth over time. Manual fixes, undocumented state, impossible to audit.
3. **No Auto-Remediation**: When drift is detected, no automated path to fix. Manual PRs, delayed resolution, high toil.

**Data Point**: Upwork contract work (past 6 months) shows 60% of DevOps failures in African startups are configuration drift in Kubernetes, not application bugs.

## Motivation

Kubernetes operators should be able to:
- Define security policies as code
- Detect when deployed workloads violate those policies
- Automatically propose fixes as Git commits
- Track all changes in audit trail

This should work the same way across AWS, GCP, Azure, and on-prem Kubernetes.

No vendor lock-in. No proprietary DSL. Standard protocols (GitHub, Kubernetes, OpenTelemetry).

## What Aurora Is

Infrastructure for production AI systems. Not another model. Not another agent. Not a prompt framework.

Infrastructure.

Analogies:
- Kubernetes became infrastructure for containers.
- Terraform became infrastructure for cloud.
- Aurora aims to become infrastructure for production AI operations.

## What Aurora Is Not

- A chatbot or AI wrapper (no LLM dependency)
- An orchestration framework (uses Kubernetes as orchestration)
- A model training platform (assumes model exists, focuses on deployment)
- A managed service (open-source, self-hosted, cloud-agnostic)
- A compliance tool (compliance is one policy, not the only one)

## Core Thesis

**Production safety cannot be bolted on. It must be architected in.**

Every deployment decision creates a policy decision. Every policy decision must be:
- Auditable (who changed what, when, why)
- Enforceable (validators block bad configs before they ship)
- Observable (metrics, traces, logs on every validation)
- Remedial (automatic fixes when drift detected)

## MVP Scope

Single end-to-end vertical slice: **Model Deployment Validator + Auto-Remediation**

Input: Kubernetes manifest for fine-tuned model

Process:
1. Validate security baseline (RBAC, network policy, secret rotation)
2. Compare deployed config against Git source of truth
3. Detect drift
4. Generate fix as GitHub PR
5. Emit structured observability

Output: Decision (approved/remediation-proposed) + metrics

## Platform Roadmap (Post-MVP)

v0.1: Model Deployment Validator (MVP, deadline-driven)
v0.2: Policy Engine (general-purpose validators)
v0.3: Inference Gateway (request admission + routing)
v1.0: Multi-cloud runtime (AWS/GCP/Azure/on-prem)
v1.1: Cost intelligence (optimize spending without losing safety)
v1.2: Compliance engine (SOC2, ISO 27001, regulatory)
v2.0: Distributed observability (cross-cluster, cross-cloud)


Each layer must be independently usable.

## Success Metrics

**By deadline (18 days):**
- Working validator API (OpenAPI spec, production code)
- Drift detection proven (Git + K8s comparison)
- Auto-remediation functional (generates valid PRs)
- Kubernetes integration (CRD + operator)
- Observability baseline (Prometheus metrics, structured logs)
- Security baseline (signed artifacts, SBOM, threat model)

**By month 2:**
- Deployed on GCP (self-hosted k3s or GKE)
- End-to-end demo (model deployment → break config → auto-fix)
- Documentation (architecture, threat model, deployment guide)
- Landing page (engineering-first, no marketing)

**By month 3:**
- General policy engine (not just validators)
- Multi-cloud support (AWS, Azure)
- Community contributions (open RFCs for post-MVP features)

## Rejected Ideas

- Using Helm for policy enforcement (too limited, not Kubernetes-native)
- Building a DSL for policies (OPA exists, use it)
- Managed SaaS first (MVP must be self-hosted, proves architecture)
- AI-driven policy generation (policies must be explicit, auditable)
- Closed-source licensing (open-source attracts engineers, engineers attract everything else)

## References

- [Open Policy Agent](https://www.openpolicyagent.org/)
- [Kubernetes Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [RBAC in Kubernetes](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [GitOps Principles](https://www.gitops.tech/)
- [OpenTelemetry](https://opentelemetry.io/)
