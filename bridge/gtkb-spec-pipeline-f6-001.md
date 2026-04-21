# F6: Project Scaffold Generator — Implementation Proposal

**Feature:** F6 — Project Scaffold Generator
**Target repo:** groundtruth-kb
**Tracker:** DOC-GTKB-SPEC-PIPELINE
**Corruption vectors addressed:** Cold-start problem (no corruption vectors at day 0, but the absence of structure enables all 5 vectors from day 1)
**Dependencies:** F1 (generates specs with enriched schema), F3 (validates generated specs)
**Prior deliberations:** DELIB-0706 (GT-KB product scope), DELIB-0708 (structured interview — deliberate spec ordering)

---

## Problem Statement

When a new project starts with GT-KB, the specification corpus is empty. The AI implementer has no governance rules, no architecture constraints, no section taxonomy, and no quality expectations. Everything must be discovered or invented during the first sessions.

Agent Red's history shows what happens during this cold-start period:

- The first 15 specs (IDs 101-115, Feb 26 2026) were infrastructure: pytest config, CI workflows, coverage gates. No governance, no architecture decisions, no security boundaries.
- Governance specs (GOV-01 through GOV-20) were introduced incrementally over many sessions, often *after* violations had already occurred
- The `type` field wasn't used until much later; early specs were all untyped
- Architecture decisions (ADRs) arrived at session S259+ — after 258 sessions of ad-hoc architecture
- The owner's vision: specs should be "introduced in the least disruptive order" — but without a scaffold, the ordering is determined by whatever the owner or AI thinks of first

The cold-start period is when corruption vectors have maximum potency because there are no defenses in place.

## Proposed Solution

A **parameterized scaffold generator** that produces a well-ordered initial spec corpus for a new project, using the enriched schema from F1 and validated by F3's quality gate.

### Input Parameters

```python
@dataclass
class ProjectProfile:
    name: str                    # Project name
    platform: str                # 'azure', 'aws', 'gcp', 'self-hosted'
    deployment: str              # 'containers', 'serverless', 'vm', 'hybrid'
    tenancy: str                 # 'multi-tenant', 'single-tenant', 'both'
    auth_model: str              # 'magic-link', 'password', 'oauth', 'api-key', 'mixed'
    frontend: str                # 'spa', 'ssr', 'static', 'none'
    data_store: str              # 'cosmos', 'postgres', 'mysql', 'dynamodb', 'mongo'
    ai_components: bool          # Whether project includes AI/ML agents
    compliance: list[str]        # ['gdpr', 'hipaa', 'soc2', 'pci', 'none']
```

### Output: Ordered Spec Corpus

The generator produces specs in **dependency order** — the order that minimizes disruption if specs are introduced sequentially:

**Phase 0: Governance (15-20 specs)**
Derived from Agent Red's GOV-01 through GOV-20. These are mostly project-agnostic:
- Spec-first workflow discipline
- KB as single source of truth
- Test creation triggers
- Change control rules
- Quality and testing standards

Parameterized by: project complexity (simpler projects need fewer governance rules)

**Phase 1: Architecture Constraints (5-10 specs)**
ADR-style decisions parameterized by the project profile:
- Deployment topology (containers vs serverless → different ADRs)
- Tenancy model (multi-tenant → ZK-like boundary spec from day 1)
- Data isolation strategy (per-tenant encryption, partition isolation)
- Auth architecture (role model, session management)

These are the specs that, in Agent Red, arrived too late and caused systemic rework.

**Phase 2: Infrastructure (10-15 specs)**
CI/CD, environment config, build pipelines:
- CI workflow (lint, test, security scan)
- Environment separation (dev, staging, production)
- Secret management
- Deployment scripts
- Monitoring/observability hooks

Parameterized by: platform (Azure → ACA/ACR specs; AWS → ECS/ECR specs)

**Phase 3: Data Model (5-10 specs)**
Core entity schemas and access patterns:
- Primary entities (tenant, user, session, etc.)
- Access control model (RBAC roles)
- Data lifecycle (retention, archival)

Parameterized by: tenancy model, data store, compliance requirements

**Phase 4: API Contracts (5-8 specs)**
External interface definitions:
- API versioning strategy
- Health/status endpoints
- Authentication endpoints
- Error response format

Parameterized by: frontend type, auth model

**Phase 5: Provisional Markers (3-5 specs)**
For each phase where the full implementation will come later, generate explicit provisional specs:
- "Mock {data_store} backend for frontend development" — provisional_until=Phase 3 data model spec
- "Stub auth endpoints" — provisional_until=Phase 4 auth spec

These implement the owner's vision: "mock APIs during development of GUI elements which won't have Azure-based back ends implemented until later" are explicitly planned, not accidental.

### Spec Quality

Every generated spec:
- Uses the enriched schema from F1 (authority=stated, type, constraints, etc.)
- Passes F3's quality gate with overall >= 0.6 (behavioral tier minimum)
- Has at least one non-grep assertion
- Includes a description with rationale
- Declares section, scope, and tags

## Counterfactual Test

**If the scaffold generator had existed at Agent Red project start:**
- Session 1 would have started with ~60 specs including governance, architecture constraints, and provisional markers
- ADR-006 (ZK boundary) would have been introduced at project start rather than session S259+, preventing the systemic rework
- GOV-09 (input classification) would have been active from day 1, preventing early spec language misinterpretation
- Mock APIs would have been explicitly provisional with links to their future replacements, preventing workaround calcification
- The AI would have had quality targets (governance specs + F3 quality gate) from the first session

## API Design

```python
class ScaffoldGenerator:
    def __init__(self, kdb: KnowledgeDB):
        self.kdb = kdb
    
    def generate(
        self,
        profile: ProjectProfile,
        dry_run: bool = True,
    ) -> ScaffoldReport:
        """Generate ordered spec scaffold for a new project."""
        ...
    
    def generate_phase(
        self,
        profile: ProjectProfile,
        phase: int,
    ) -> list[dict]:
        """Generate specs for a single phase. Useful for incremental scaffolding."""
        ...

@dataclass
class ScaffoldReport:
    phases: list[dict]           # [{phase, name, specs: [...]}]
    total_specs: int
    provisional_specs: int       # How many are provisional
    quality_scores: dict         # Aggregate quality scores from F3
    dependency_order: list[str]  # Recommended introduction order
```

## Test Plan

1. **Minimal project** — Generate scaffold for single-tenant, self-hosted, password auth, no AI; verify ~40 specs generated
2. **Full project** — Generate scaffold for multi-tenant, Azure, mixed auth, AI agents, GDPR+SOC2; verify ~80 specs
3. **Governance universality** — Verify governance phase is identical regardless of project profile (these are project-agnostic)
4. **Provisional linking** — Verify all provisional specs have valid provisional_until references to other generated specs
5. **Quality validation** — Run F3 quality gate on all generated specs; verify all pass >= 0.6
6. **Dependency order** — Verify no spec references a section/scope that hasn't been established by a prior phase

## Implementation Sequence

1. Define `ProjectProfile` and `ScaffoldReport` dataclasses
2. Build governance template library (derived from Agent Red GOV-01 through GOV-20)
3. Build parameterized architecture template library (ADR templates for each platform/tenancy/auth combination)
4. Build infrastructure template library (parameterized by platform)
5. Build data model template library (parameterized by tenancy + data store)
6. Build API contract template library (parameterized by frontend + auth)
7. Build provisional marker generator
8. Implement dependency ordering algorithm
9. Integrate with F1 (enriched schema) and F3 (quality validation)
10. Write tests (6 cases above)

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Generated specs are too generic to be useful | Templates derived from Agent Red's actual specs (battle-tested); parameterization adds project-specific detail |
| Scaffold is overwhelming for simple projects | Minimal profile generates ~40 specs; complexity scales with profile parameters |
| Templates become stale as GT-KB evolves | Templates stored in GT-KB repo and versioned; scaffold generator tested in CI |

## Open Questions for Codex Review

1. Should the scaffold be generated all at once or phase-by-phase with owner confirmation between phases?
2. Should generated specs be `authority=stated` (assumed to represent owner intent) or `authority=inferred` (AI-generated, pending confirmation)?
3. How should the scaffold interact with existing specs if run on a non-empty KB?
4. Should there be a mechanism to share custom scaffolds between projects (community templates)?

---

*Submitted by: S286-Prime*
*Date: 2026-04-12*
*Tracker: DOC-GTKB-SPEC-PIPELINE, Feature F6*
