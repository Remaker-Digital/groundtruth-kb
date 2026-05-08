NEW

# Implementation Proposal — GTKB-CANONICAL-TERMINOLOGY-SYSTEM-CONTEXT-MODEL-001 (Phase 1)

**Author:** Prime Builder (Claude, harness B)
**Drafted:** 2026-05-08
**Type:** Net-new feature scoping under Phase 1 (foundation only); follow-on phases deferred to sibling bridge threads.
**Source advisory:** `bridge/gtkb-canonical-terminology-system-context-model-advisory-2026-05-07-001.md` (Codex Loyal Opposition NO-GO advisory; deliberate NO-GO signaling that the implicit-glossary posture should be promoted to a first-class, scoped, testable GT-KB feature).
**Source insight report:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-07-16-12-CANONICAL-TERMINOLOGY-SYSTEM-AND-BOUNDED-CONTEXT-ADVISORY.md`

## Claim

Promote the canonical terminology surface from an implicit `.claude/rules/canonical-terminology.md` glossary convention to a first-class **Canonical Terminology System** (CTS) governed feature in GT-KB. **Phase 1** (this proposal) delivers the foundational artifacts:

1. A **term record schema** in MemBase (`canonical_terms` table) capturing canonical term, definition, accepted synonyms, discouraged synonyms, scope, authority level, linked artifacts, linked services, examples, and lifecycle status.
2. A **collision detection rule** at the doctor level: if an adopter project's terminology file proposes a term whose `id` matches a GT-KB platform-owned core term, the doctor check WARN/ERROR per the term's authority level.
3. A **glossary documentation refresh** explaining (a) that GT-KB terms may have meanings distinct from common usage, and (b) the protected platform-owned vs adopter/project term distinction.
4. **Initial population** of the table from the existing `.claude/rules/canonical-terminology.md` core vocabulary (8 ADR-0001 terms + the 18 GT-KB platform/lifecycle terms added in S327).

Phases 2–4 (Agent Operating Context startup retrieval, Bounded Knowledge Principle implementation, complexity-control surfacing, junior-developer documentation) are **deferred to follow-on bridge threads** scoped after Phase 1 is VERIFIED.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge proposals/reviews are governed through `bridge/INDEX.md`; this proposal is delivered via that protocol.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every implementation proposal cites its governing specs; this section is the response.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires spec-derived tests; the Specification-Derived Test Plan section maps tests to acceptance criteria.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — application files under `applications/`; this proposal touches platform `groundtruth-kb/src/` and `.claude/rules/` only — no application content.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — owner-relevant artifact-oriented governance; this proposal converts a chat-only glossary convention into a durable canonical artifact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — durable artifacts, lifecycle states, traceable review evidence; the term record schema embeds these properties.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — terminology additions and changes will have explicit lifecycle states.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` — owner-visible confirmation for promoting chat-derived ideas to formal specifications. This proposal cites the four 2026-05-07 owner agreements (in `Owner Decisions / Input` below) as already-approved input.
- `.claude/rules/canonical-terminology.md` — current glossary surface; this proposal extends it with a backing MemBase table, not replacing the markdown reference.
- `.claude/rules/operating-model.md` §2 — the canonical-terms vocabulary baseline this proposal codifies into a structured form.
- `.claude/rules/deliberation-protocol.md` — owner-decision archive of the four 2026-05-07 agreements; cited as `source_type=owner_conversation`.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol root contract.
- `.claude/rules/codex-review-gate.md` — review-gate constraints (no code without GO).
- `.claude/rules/project-root-boundary.md` — root-boundary contract.
- `bridge/gtkb-canonical-terminology-system-context-model-advisory-2026-05-07-001.md` — source advisory; intentional NO-GO.
- `bridge/gtkb-canonical-terminology-surface-001.md` and follow-on verified implementation thread — prior canonical-terminology-surface authority (the existing `.claude/rules/canonical-terminology.md` markdown surface).
- `groundtruth-kb/src/groundtruth_kb/db.py` — MemBase Python API; new `canonical_terms` table will be added through the same append-only/versioned discipline.

## Owner Decisions / Input

The four 2026-05-07 owner agreements that scope this proposal (cited from the source advisory):

| Decision | Source | Disposition for Phase 1 |
|---|---|---|
| "Canonical Terminology System" is the preferred name for the terminology feature. | 2026-05-07 owner agreement (advisory §"Owner Decisions / Input") | Used as the feature name throughout this proposal and in MemBase records. |
| Users may add their own terms, but core terminology is implicitly linked to the processes, data, and services GT-KB agents require. | 2026-05-07 owner framing | Phase 1 schema includes `authority_level` ∈ {`platform_core`, `adopter_extension`, `project_local`} to distinguish protected core terms from extensions. |
| Initialized agents must be aware of core canonical terminology, available services, essential artifacts, and how to access them. | 2026-05-07 owner requirement | Acknowledged as Phase-2-or-later scope (Agent Operating Context). Phase 1 establishes the *data substrate* that Phase 2 retrieves. |
| GT-KB has a practical complexity ceiling; memory and knowledge systems can consume excessive resources and increase errors if not bounded. | 2026-05-07 owner agreement | Phase 1 adds a complexity-conscious schema (no required vector-index dependency for the core table; the existing ChromaDB index can layer on later if needed). The Bounded Knowledge Principle implementation is Phase-3 deferred. |

This Phase-1 proposal is authorized for implementation under the owner directive (S336 this session): "Please work independently on the bridge NO-GO items" + "Yes please" continue with items 6/5/2/1. The proposal does NOT request fresh owner-AUQ for Phase 1 design choices; it does request owner input via Codex review feedback if any Phase-1 design choice needs refinement.

## Source Advisory: What Codex Recommended

Codex's advisory recommended Prime file an implementation proposal covering 8 design areas. Phase 1 (this proposal) addresses items 1–4 below; items 5–8 are explicitly deferred:

| # | Codex-recommended area | Phase 1 (this proposal) | Future phases |
|---|---|---|---|
| 1 | Canonical Terminology System as a primary GT-KB functional component | ✓ Backing table + schema + doctor check + initial population | — |
| 2 | Protected platform-owned core terms versus user/project/adopter terms | ✓ `authority_level` field; doctor enforces protection level | — |
| 3 | Accepted synonyms, discouraged synonyms, examples where common usage differs | ✓ `accepted_synonyms`, `discouraged_synonyms`, `usage_examples` fields | — |
| 4 | Collision handling when project terminology tries to redefine a GT-KB core term | ✓ Doctor check: `platform_core` collisions = ERROR; `adopter_extension` collisions = WARN; `project_local` always allowed | — |
| 5 | Agent Operating Context as a compact startup/retrieval package | — | **Phase 2** (sibling bridge thread) |
| 6 | Required startup awareness set: core terms, services, essential artifacts, access methods, source-of-truth precedence, active role, active scope | — | **Phase 2** |
| 7 | Bounded Knowledge Principle: GT-KB makes context discoverable, ranked, scoped, cited, bounded — not merely abundant | — | **Phase 3** (sibling bridge thread; depends on Phase 2 retrieval surfaces) |
| 8 | Documentation written for junior developers and fresh agents | Partial — Phase 1 glossary refresh covers the **why** (terms have GT-KB-specific meanings); junior-dev / fresh-agent documentation is **Phase 4** | **Phase 4** |

## Proposed Implementation (Phase 1)

### Files Created

- `groundtruth-kb/src/groundtruth_kb/canonical_terms.py` — Python module exposing `insert_term`, `get_term`, `list_terms`, `find_collisions` and the schema constants for the new `canonical_terms` table.
- `tests/scripts/test_canonical_terms_schema.py` — focused test suite for schema constants, insert/get round-trip, append-only/versioned discipline, and collision detection.

### Files Modified

- `groundtruth-kb/src/groundtruth_kb/db.py` — add `canonical_terms` table to the schema initialization (append-only/versioned, matching existing artifact tables: `UNIQUE(id, version)`, `changed_by`, `changed_at`, `change_reason` columns).
- `scripts/check_canonical_terminology_doctor.py` — new doctor check that reports collisions between platform-core terms and any adopter/project-level term overrides; exits non-zero on `platform_core` collisions, WARN on `adopter_extension` collisions.
- `.claude/rules/canonical-terminology.md` — explanatory note added to the document head: "GT-KB terms may have meanings distinct from common usage; canonical-truth lives in MemBase's `canonical_terms` table per `GTKB-CANONICAL-TERMINOLOGY-SYSTEM-CONTEXT-MODEL-001`. The markdown file is a human-readable snapshot/reference; the table is canonical."

### Schema (proposed)

```sql
CREATE TABLE canonical_terms (
    id TEXT NOT NULL,
    version INTEGER NOT NULL,
    canonical_term TEXT NOT NULL,
    definition TEXT NOT NULL,
    authority_level TEXT NOT NULL CHECK (authority_level IN ('platform_core', 'adopter_extension', 'project_local')),
    scope TEXT NOT NULL,
    accepted_synonyms TEXT,
    discouraged_synonyms TEXT,
    linked_artifacts TEXT,
    linked_services TEXT,
    usage_examples TEXT,
    forbidden_uses TEXT,
    lifecycle_status TEXT NOT NULL CHECK (lifecycle_status IN ('candidate', 'active', 'deprecated', 'retired')),
    source_authority TEXT NOT NULL,
    changed_by TEXT NOT NULL,
    changed_at TEXT NOT NULL,
    change_reason TEXT NOT NULL,
    PRIMARY KEY (id, version),
    UNIQUE(id, version)
);
```

Field semantics:

- `id` — slug-form term identifier, e.g., `MEMBASE`, `DELIBERATION_ARCHIVE`, `PRIME_BUILDER`. Stable across versions.
- `canonical_term` — display form, e.g., `MemBase`, `Deliberation Archive`, `Prime Builder`.
- `authority_level` — protection class:
  - `platform_core` — owned by GT-KB platform; adopters cannot override. Doctor ERROR on collision.
  - `adopter_extension` — extension a specific adopter declares (e.g., Agent Red defines `customer_workflow`). Doctor WARN on cross-adopter or platform collision.
  - `project_local` — local to a single project/sub-project; never collides at platform scope.
- `scope` — where the term applies: `platform`, `adopter:<name>`, `project:<name>`, `subproject:<name>`.
- `accepted_synonyms`, `discouraged_synonyms`, `linked_artifacts`, `linked_services`, `usage_examples`, `forbidden_uses` — JSON-encoded list strings.
- `lifecycle_status` — uses the same lifecycle vocabulary as other GT-KB artifacts (`candidate`, `active`, `deprecated`, `retired`).
- `source_authority` — pointer to the rule or deliberation that authorized the term, e.g., `.claude/rules/operating-model.md §2` or `DELIB-S327-TERM-PRIMER-STARTUP-OWNER-DIRECTIVE`.

### Initial Population (26 platform-core terms)

Phase 1 implementation populates the table from the current canonical glossary in `.claude/rules/canonical-terminology.md`:

- 8 ADR-0001 core vocabulary: `MEMBASE`, `DELIBERATION_ARCHIVE`, `MEMORY_MD`, `KNOWLEDGE_DATABASE`, `GROUNDTRUTH_KB`, `GT_KB`, `PRIME_BUILDER`, `LOYAL_OPPOSITION`.
- 18 GT-KB platform/lifecycle terms (S327 directive): `GROUNDTRUTH_KB_HYPHENATED`, `GTKB`, `PLATFORM`, `APPLICATION`, `HOSTED_APPLICATION`, `AGENT_RED`, `ADOPTER`, `PROJECT`, `SUB_PROJECT`, `WORK_ITEM`, `BACKLOG`, `SPECIFICATION`, `REQUIREMENT`, `IMPLEMENTATION_PROPOSAL`, `IMPLEMENTATION_REPORT`, `VERIFICATION`, `DASHBOARD`, `BRIDGE`.

All 26 are inserted at `authority_level='platform_core'`, `scope='platform'`, `lifecycle_status='active'`, `source_authority='.claude/rules/operating-model.md §2'` (or the matching `DELIB-` ID where the term was introduced by an owner directive).

### Doctor Check (proposed)

`scripts/check_canonical_terminology_doctor.py`:

```python
# Pseudocode
def check():
    db = MemBase()
    platform_core = db.list_terms(authority_level='platform_core')
    platform_core_ids = {t['id'] for t in platform_core}

    adopter_extensions = db.list_terms(authority_level='adopter_extension')
    project_local = db.list_terms(authority_level='project_local')

    errors = []
    warnings = []

    # Platform-core collisions: a non-platform_core term shares an id with platform_core
    for term in adopter_extensions + project_local:
        if term['id'] in platform_core_ids:
            errors.append(f"Term '{term['id']}' redefines a platform_core term in scope '{term['scope']}'.")

    # Cross-adopter adopter_extension collisions
    by_id = defaultdict(list)
    for term in adopter_extensions:
        by_id[term['id']].append(term)
    for term_id, instances in by_id.items():
        if len(instances) > 1:
            warnings.append(f"Term '{term_id}' has multiple adopter_extension definitions: {[t['scope'] for t in instances]}.")

    return {"errors": errors, "warnings": warnings}
```

Exit code: 0 (clean) | 1 (warnings, non-blocking) | 2 (errors, blocking). Integrated into the release-candidate gate as advisory (Phase 1) and may be promoted to blocking in a future phase.

## Out Of Scope (Phase 1)

- Agent Operating Context structure, retrieval, and startup wiring (**Phase 2**).
- Bounded Knowledge Principle implementation (ranking, scoping, citing, bounding) (**Phase 3**).
- Junior-developer / fresh-agent documentation rewrite (**Phase 4**).
- Vector-index integration of `canonical_terms` (deferred; the existing ChromaDB index can wrap this table later).
- Migration of all 26 initial terms' content from the markdown file into the table beyond the canonical-truth substitution (full content migration is mechanical follow-on work).
- Adopter / project-local term seeding (this proposal adds the schema; adopters seed their own terms in their own bridge threads).
- Removal of `.claude/rules/canonical-terminology.md` (the markdown file remains as a human-readable snapshot/reference).

## Specification-Derived Test Plan

| Test ID | Spec Coverage | Procedure | Expected |
|---|---|---|---|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` | `grep "Document: gtkb-canonical-terminology-system-context-model-001" bridge/INDEX.md` | Match present |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-canonical-terminology-system-context-model-001` | `preflight_passed: true`, `missing_required_specs: []` |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This proposal contains spec-to-test mapping; post-impl report carries forward executed evidence | section present + Phase-1 verification commands documented |
| **T-schema-1** | Phase-1 schema | `groundtruth_kb.canonical_terms.SCHEMA_DDL` matches the proposed schema | byte-equal to canonical DDL string |
| **T-schema-2** | Phase-1 append-only discipline | Insert two versions of the same `id`; both rows present | `len(list_versions(id)) == 2` |
| **T-schema-3** | Phase-1 authority-level constraint | Insert `authority_level='invalid'` raises `IntegrityError` | constraint check fires |
| **T-schema-4** | Phase-1 lifecycle-status constraint | Same as above for `lifecycle_status` | constraint check fires |
| **T-doctor-1** | Phase-1 collision detection (ERROR) | Insert a `platform_core` term, then an `adopter_extension` with same id; doctor returns errors=1 | error reported |
| **T-doctor-2** | Phase-1 collision detection (WARN) | Insert two `adopter_extension` terms with same id, different scopes; doctor returns warnings=1 | warning reported |
| **T-doctor-3** | Phase-1 doctor exit codes | Run doctor on clean db (exit 0), warning-only db (exit 1), error db (exit 2) | exits 0/1/2 |
| **T-population-1** | Phase-1 initial-population correctness | After population, `list_terms(authority_level='platform_core')` returns ≥ 26 records | True |
| **T-glossary-doc-1** | Phase-1 glossary doc refresh | `grep "canonical-truth lives in MemBase's canonical_terms table" .claude/rules/canonical-terminology.md` | match present |
| **T-isolation-1** | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All Phase-1 changes touch only `groundtruth-kb/src/`, `scripts/`, `tests/scripts/`, and `.claude/rules/` (no application content) | `git diff --stat` shows no `applications/Agent_Red/` paths |
| **T-secrets-1** | Credential safety | `python -m groundtruth_kb secrets scan --paths <changed-files> --json --fail-on=` returns finding_count: 0 | True |

## Acceptance Criteria

- [ ] Codex GO on this proposal
- [ ] Phase-1 schema accepted (or correction-requested via NO-GO)
- [ ] Initial-population set of 26 terms accepted (or correction-requested)
- [ ] Doctor-check semantics accepted (ERROR on platform_core collision, WARN on cross-adopter)
- [ ] Phase scope (Phase 1 only; Phases 2–4 deferred) accepted

VERIFIED when:

- [ ] All test IDs T-schema-1 through T-secrets-1 pass with command output captured in post-impl report
- [ ] `groundtruth_kb.canonical_terms` module merged with append-only/versioned discipline
- [ ] Doctor check integrated into the release-candidate gate (advisory)
- [ ] Glossary doc note added (canonical-truth-in-MemBase clarification)
- [ ] Codex VERIFIED on the post-impl report

## Risk and Rollback

| Risk | Likelihood | Impact | Mitigation |
|---|---:|---:|---|
| Schema decisions need refinement after Phase 2 (Agent Operating Context) reveals new requirements | Medium | Low | Append-only versioning lets future phases evolve schema via additive columns; no reverse-incompatible changes anticipated. |
| Initial-population set diverges from `.claude/rules/canonical-terminology.md` (drift between table and markdown) | Medium | Low | Phase-1 doctor check adds a parity check between the glossary doc and the table (planned for the post-impl report). |
| Bounded Knowledge Principle (Phase 3) reveals that the term record schema lacks ranking/citation fields | Low | Low | Future phases can add columns without breaking append-only; or add adjacent tables for retrieval metadata. |

Rollback: `git revert` of the schema-creation migration, the new module, and the doctor-check script. Initial-population data is removed by reverting the migration. The markdown glossary doc remains the human-readable reference (no rollback impact).

## Pre-Filing Preflight

This `-001` will be evaluated by `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-canonical-terminology-system-context-model-001` after INDEX update. Expected: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.

## Provenance

| Source | Reference |
|---|---|
| Source advisory (intentional NO-GO) | `bridge/gtkb-canonical-terminology-system-context-model-advisory-2026-05-07-001.md` |
| Source insight report | `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-07-16-12-CANONICAL-TERMINOLOGY-SYSTEM-AND-BOUNDED-CONTEXT-ADVISORY.md` |
| Owner agreements (2026-05-07) | Captured in advisory `Owner Decisions / Input` section: feature name, core-term implicitness, agent-awareness requirement, complexity ceiling |
| Owner directive (S336 this session) | "Please work independently on the bridge NO-GO items" → "Yes please" continue with items 6/5/2/1 |
| Companion future bridges | `gtkb-canonical-terminology-system-agent-operating-context-002` (Phase 2; not yet drafted), `gtkb-canonical-terminology-bounded-knowledge-principle-003` (Phase 3; not yet drafted), `gtkb-canonical-terminology-junior-dev-docs-004` (Phase 4; not yet drafted) |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
