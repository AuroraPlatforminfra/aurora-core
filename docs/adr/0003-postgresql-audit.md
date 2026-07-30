# ADR-0003: Why PostgreSQL for Audit Logs + Policy Versions

**Status:** Accepted
**Date:** 2026-07-28

## Decision

Use PostgreSQL for persistent storage of audit logs, policy versions, and remediation history.

## Rationale

1. **Auditability**: Transactions guarantee no data loss, full ACID compliance
2. **Queryability**: SQL enables complex audit queries, not just key-value lookups
3. **Versioning**: Native support for versioning policies with rollback capability
4. **Production Proven**: Used by enterprises for mission-critical data

## Alternatives Considered

- **NoSQL (DynamoDB, Firestore)**: Weaker transactional guarantees, harder to audit
- **File-based (Git commits only)**: Works for small scale, breaks at production scale
- **In-memory (Redis)**: No persistence, loss on restart

## Consequences

- Operational overhead (backups, replication, upgrades)
- Fixed schema (requires migrations), but more type-safe than schemaless
- PostgreSQL StatefulSet adds complexity to K8s deployment

## Mitigation

- Automated backups via cloud provider (GCP Cloud SQL)
- Flyway or Alembic for schema migrations
- Read replicas for high-availability
