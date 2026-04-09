# GroundTruth Product Architecture

## Decision Context

On 2026-04-04, the project owner approved a three-layer product split
for the GroundTruth ecosystem.  This decision was informed by a Loyal
Opposition gap-closure proposal and a Prime Builder advisory response,
both delivered and resolved over the prime-bridge collaboration channel.

**Decision memo:** `INSIGHTS-2026-04-04-08-12-00-GROUNDTRUTH-OWNER-DECISION-MEMO.md`

The core finding: GroundTruth v0.1.x is a knowledge-database and
governance toolkit.  Teams adopting it also need project scaffolding,
environment configuration, and (optionally) infrastructure provisioning.
Those capabilities should live in separate packages with distinct
ownership boundaries, not be folded into the core toolkit.

---

## Three-Layer Architecture

### Layer 1 — `groundtruth-kb` (this package)

The stable upstream core.

| Capability | Examples |
|------------|----------|
| Knowledge database | Append-only SQLite, 9 artifact types, full version history |
| CLI | `gt init`, `gt bootstrap-desktop`, `gt assert`, `gt seed`, `gt summary`, `gt serve` |
| Governance framework | Built-in gates, pluggable gate architecture, assertion engine |
| Method documentation | 11 numbered docs describing the specification-first workflow |
| Web dashboard | Optional FastAPI UI (`[web]` extra) |
| Reference templates | CLAUDE.md, MEMORY.md, bridge inventory, hooks, rules, CI/CD workflows |

**Scope boundary:** groundtruth-kb initializes a knowledge database
(`groundtruth.toml` + `groundtruth.db`) and provides the tools to
manage specifications, tests, work items, assertions, and the method
docs/templates that tell teams how to capture operational configuration.
It includes a lightweight local bootstrap path for same-day prototype work, but
it does not scaffold full production projects, provision infrastructure,
configure dual-agent runtimes automatically, or set up cloud environments.

### Layer 2 — `groundtruth-project-kit` (planned, separate package)

The missing bootstrap and scaffolding layer.

| Capability | Description |
|------------|-------------|
| Project scaffold | Generate or retrofit a repo with rules, hooks, bridge files, report templates |
| Project manifest | Declare project name, owner, stack, cloud provider, agent topology |
| Profiles | Pre-built configurations: `local-only`, `dual-agent-webapp`, `staging-minimal` |
| Doctor | Detect installed tools, verify config, produce readiness reports |
| Upgrade | Update project-owned scaffold files when the kit version changes |

**Planned commands:** `gt project init`, `gt project doctor`, `gt project upgrade`

**Scope boundary:** groundtruth-project-kit configures local files and
validates environment readiness.  It does not create cloud resources,
external accounts, or production infrastructure without explicit opt-in.

### Layer 3 — Cloud profiles (future, gated on Phase 2 validation)

Optional infrastructure modules, separated from install.

| Capability | Description |
|------------|-------------|
| IaC generation | Terraform/Bicep for supported deployment profiles |
| Environment seeding | Test tenants, secrets placeholders, health checks |
| Post-deploy verification | Runtime checks matching production gate patterns |

**Guardrails:** No production provisioning by default.  Production
requires explicit confirmation and owner approval.  No external account
creation.  No "environment ready" verdict until runtime checks pass.

**Status:** Design phase.  Will not begin until Phase 2 (project-kit)
is validated by at least one project besides the reference implementation.

---

## Dependency Direction

```
groundtruth-project-kit  ──depends-on──►  groundtruth-kb
cloud-profiles           ──depends-on──►  groundtruth-project-kit
```

groundtruth-kb has **no dependency** on project-kit or cloud profiles.
It remains a standalone toolkit usable without either.

---

## Reference Implementation

Agent Red Customer Experience is the proving ground for the patterns
that groundtruth-project-kit will productize.  The project-kit will
extract simplified, reusable versions of:

- Message schema and bridge coordination model
- Worker lifecycle pattern (resident workers, notification-driven wake)
- Claim/resolve/negotiate protocol
- Session hook and rule file conventions
- Operational expectations (responsiveness, audit, reporting)

The current Agent Red runtime is project-shaped and carries historical
compatibility logic.  It is the behavioral reference, not the
distributable artifact.

---

## Current Status

| Package | Version | Status |
|---------|---------|--------|
| groundtruth-kb | 0.1.2 | Alpha — extracted from production system (2,000+ specs, 11,000+ tests) |
| groundtruth-project-kit | — | Design phase (Phase 1: scope clarification, Phase 2: implementation) |
| Cloud profiles | — | Not started (gated on Phase 2 validation) |

---

## Approved Phased Delivery

| Phase | Scope | Status |
|-------|-------|--------|
| Phase 1 | Clarify product boundaries, fix naming/docs | **In progress** |
| Phase 2 | Ship groundtruth-project-kit scaffold layer | Approved, not started |
| Phase 3 | Workstation doctor/bootstrap | Deferred (gate review required) |
| Phase 4 | Infrastructure bootstrap modules | Deferred (gate review required) |
