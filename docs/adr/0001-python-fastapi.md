# ADR-0001: Why Python + FastAPI

**Status:** Accepted
**Date:** 2026-07-28

## Decision

Use Python 3.12 + FastAPI for Aurora Core MVP.

## Rationale

1. **FastAPI Production-Ready**: Built-in OpenAPI, async native, validation layer, dependency injection
2. **Ecosystem**: PyGithub (GitHub), kubernetes client (K8s API), SQLAlchemy (DB), OpenTelemetry (observability)
3. **Policy Evaluation**: Open Policy Agent (OPA) has Python libraries, Rego is the standard policy language
4. **Team Fluency**: Easier onboarding than Go, stronger type checking than Node

## Alternatives Considered

- **Go**: Faster runtime, but weaker policy ecosystem, harder to do dynamic validation
- **Node.js**: Popular, but runtime overhead for long-lived processes
- **Rust**: Overkill for MVP, steep learning curve

## Consequences

- Slower than Go, but correctness + observability > speed
- Requires Python 3.12+ (EOL 2029)
- Async learning curve for developers unfamiliar with asyncio

## Mitigation

- Async patterns documented in code comments
- Type hints enforced (mypy strict mode)
- Performance benchmarked before v1.0 release
