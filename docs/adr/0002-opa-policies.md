# ADR-0002: Why Open Policy Agent (OPA) for Policy Engine

**Status:** Accepted
**Date:** 2026-07-28

## Decision

Use Open Policy Agent (OPA) + Rego language for policy evaluation in Aurora Core.

## Rationale

1. **Industry Standard**: Kubernetes, Terraform, Docker, Vault all use OPA
2. **Declarative**: Policies are data queries, not imperative code
3. **Testable**: Easy to unit test policies in isolation
4. **No Vendor Lock-In**: OPA is open-source, vendor-neutral
5. **Composition**: Policies can be composed and reused

## Example Policy (Rego)

```rego
package aurora.rbac

deny[msg] {
    input.kind == "ServiceAccount"
    roles := input.roleBindings[_]
    roles.name == "cluster-admin"
    msg := "ServiceAccount cannot have cluster-admin role"
}

deny[msg] {
    input.kind == "Deployment"
    not input.securityContext.runAsNonRoot
    msg := "Deployment must run as non-root user"
}
```

## Alternatives Considered

- **Custom DSL**: Too much engineering, reinventing OPA
- **Kubernetes Admission Controllers**: Built into K8s, but not reusable across platforms
- **CEL (Common Expression Language)**: Lighter than Rego, but less mature ecosystem

## Consequences

- OPA adds ~50MB to Docker image (acceptable)
- Learning curve for Rego, but well-documented
- Policy evaluation adds ~50-100ms per request

## Mitigation

- Rego policies documented with examples
- Policy library open-sourced for community contribution
- Benchmarking ensures latency is within SLA
