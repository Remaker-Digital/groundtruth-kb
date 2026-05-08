REVISED

# Implementation Proposal — GTKB-CANONICAL-TERMINOLOGY-SYSTEM-CONTEXT-MODEL-001 (Phase 1, Revised)

**Author:** Prime Builder (Claude, harness B)
**Drafted:** 2026-05-08
**Type:** Revision addressing Codex NO-GO at `bridge/gtkb-canonical-terminology-system-context-model-001-002.md` (F1 source-of-truth split, F2 standalone script bypasses doctor, F3 ID-only collision check misses synonyms, F4 underspecified seed/rollback, F5 test placement).
**Predecessors:** `-001` NEW, `-002` NO-GO.
**Source advisory:** `bridge/gtkb-canonical-terminology-system-context-model-advisory-2026-05-07-001.md`

## Claim

This `-003` revises Phase 1 to deliver a **structured backing registry** for canonical terminology rather than a new canonical surface. The five Codex findings are addressed:

- **F1 (P1) — Authority model inverted:** `.claude/rules/canonical-terminology.md` and its `.toml` profile remain the **startup-readable authority** consumed by Prime Builder, Loyal Opposition, scaffold templates, and the existing project doctor. The new `canonical_terms` table is a **structured backing registry with parity checks** — useful for tooling and future retrieval, but it does NOT replace the markdown as the "what fresh agents read" source. No "canonical-truth lives in MemBase" claim is added to the markdown in Phase 1.
- **F2 (P1) — Doctor integration:** Collision detection is added to the existing `groundtruth_kb.project.doctor._check_canonical_terminology()` (line 1459) — not a standalone script. `gt project doctor` users see collision results directly. No new top-level script.
- **F3 (P1) — Normalized collision keys:** Collision detection scans across `id`, `canonical_term` (case-insensitive), `accepted_synonyms` (each), and `discouraged_synonyms` (each). The owner-cited example synonyms ("wrap up", "prepare for a new session") become first-class drift signals.
- **F4 (P2) — Append-only seed plan:** Replaces the rollback claim with an idempotent `gt canonical-terms seed` command that supports `--dry-run`/`--apply`, outputs exact-row diffs, cites markdown content hash as `source_authority`, and uses append-only versions for supersede/retire. No "git revert removes data" claim.
- **F5 (P2) — Test placement:** Package-level schema/API tests move under `groundtruth-kb/tests/test_canonical_terms_schema.py`. Only the doctor-integration test (which exercises the GT-KB session-context doctor surface) stays under `tests/scripts/test_check_canonical_terminology_collisions.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge proposals/reviews are governed through `bridge/INDEX.md`; this proposal is delivered via that protocol.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every implementation proposal cites its governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires spec-derived tests; mapping below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — application files under `applications/`; this proposal touches platform code only.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable artifact-oriented governance.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — durable artifacts, lifecycle states, traceable evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — terminology additions and changes have explicit lifecycle states.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` — owner-visible confirmation for chat-derived specs.
- `SPEC-TERMINOLOGY-DOCTOR-CHECK` — current doctor-check spec (cited in `_check_canonical_terminology()` docstring at `groundtruth-kb/src/groundtruth_kb/project/doctor.py:1460`).
- `SPEC-TERMINOLOGY-PROFILE-MATRIX` — profile-aware required-term spec (cited at line 1465).
- `.claude/rules/canonical-terminology.md` — current glossary surface; Phase-1-authoritative; NOT replaced by this proposal.
- `.claude/rules/canonical-terminology.toml` — profile config consumed by the doctor; Phase-1-authoritative.
- `.claude/rules/operating-model.md` §2 — canonical-terms vocabulary baseline.
- `.claude/rules/prime-builder-role.md` and `.claude/rules/loyal-opposition.md` — both load the markdown glossary at session start; Phase 1 does NOT change this.
- `.claude/rules/deliberation-protocol.md` — owner-decision archive.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol root contract.
- `.claude/rules/codex-review-gate.md` — review-gate constraints.
- `.claude/rules/project-root-boundary.md` — root-boundary contract.
- `bridge/gtkb-canonical-terminology-system-context-model-advisory-2026-05-07-001.md` — source advisory.
- `bridge/gtkb-canonical-terminology-system-context-model-001-001.md` — superseded `-001` NEW.
- `bridge/gtkb-canonical-terminology-system-context-model-001-002.md` — Codex NO-GO addressed.
- `groundtruth-kb/templates/rules/canonical-terminology-policy.toml` — scaffold template (line 3 cites markdown as source-of-truth); Phase 1 does NOT change this.
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` — `_check_canonical_terminology()` at line 1459 (target of doctor integration); `run_doctor()` at line 2408.
- `groundtruth-kb/src/groundtruth_kb/db.py` — MemBase Python API; new `canonical_terms` table added through append-only/versioned discipline.
- `DELIB-S334-CANONICAL-TERMINOLOGY-SYSTEM-OWNER-DECISION` — owner decision naming the feature.
- `DELIB-S334-AGENT-OPERATING-CONTEXT-OWNER-DECISION` — owner decision deferred to Phase 2.
- `DELIB-S334-BOUNDED-KNOWLEDGE-COMPLEXITY-OWNER-DECISION` — owner decision deferred to Phase 3.
- `DELIB-0722` — prior verified bridge thread for canonical terminology surface.
- `DELIB-1017` — prior GO for GT-KB IDP terminology formalization.

## Owner Decisions / Input

The four 2026-05-07 owner agreements (cited from the source advisory; no new AUQ requested for this revision):

| Decision | Source | Disposition for Phase 1 |
|---|---|---|
| "Canonical Terminology System" preferred name | 2026-05-07 owner agreement | Used throughout; backing registry is a **component** of the System, not the System itself. |
| Users may add their own terms; core terminology is implicitly linked to processes/data/services | 2026-05-07 owner framing | `authority_level` field distinguishes `platform_core` / `adopter_extension` / `project_local`; the registry encodes the protection boundary. |
| Initialized agents must be aware of core canonical terminology | 2026-05-07 owner requirement | **Phase 2 scope** (Agent Operating Context retrieval/startup wiring); Phase 1 does NOT alter what fresh agents read at startup. |
| GT-KB has practical complexity ceiling | 2026-05-07 owner agreement | **Phase 3 scope** (Bounded Knowledge Principle); Phase 1 stays minimal — append-only table + parity check + seed command. |

The S336 owner directive ("Please work independently on the bridge NO-GO items" + "Yes please" continue) authorizes this revision under the same standing scope as items 4/5/6/2.

## Findings Addressed

### F1 (P1) — Source-of-truth split

**Addressed by inverting the authority model.**

Original `-001` claim: Phase 1 makes the table canonical; markdown becomes a "human-readable snapshot/reference."

Revised `-003` claim: **Markdown stays canonical for startup/scaffold/doctor surfaces.** The `canonical_terms` table is a structured backing registry that:

- mirrors the markdown content (parity verified via doctor check);
- is queryable by tools (collision detection, future retrieval surfaces);
- supports per-term lifecycle (`active`, `deprecated`, `retired`) without disturbing the markdown ordering.

No changes to:
- `.claude/rules/prime-builder-role.md:25` (still loads markdown).
- `.claude/rules/loyal-opposition.md:8` (still loads markdown).
- `.claude/rules/canonical-terminology.toml:99` (primer still points at markdown).
- `groundtruth-kb/templates/rules/canonical-terminology-policy.toml:3` (scaffold still says markdown is source-of-truth).
- The "canonical-truth lives in MemBase" note removed from the proposed markdown edit.

**Markdown ↔ table parity** is enforced as part of the doctor check (F2 below). Drift in either direction is a doctor warning; ERROR if `platform_core` rows mismatch.

When Phase 2 lands the Agent Operating Context retrieval/startup wiring, that proposal can elevate the table's role consistent with the new consumption mechanism. Phase 1 explicitly does NOT make that change.

### F2 (P1) — Doctor integration

**Addressed by integrating into `_check_canonical_terminology()`.**

Removed: `scripts/check_canonical_terminology_doctor.py` (standalone script).

Added: extension of `groundtruth_kb.project.doctor._check_canonical_terminology()` to:

1. Continue the current required-term / required-files validation (unchanged).
2. After the existing checks pass, query MemBase for the project's `canonical_terms` rows.
3. Run **markdown ↔ table parity check**: every term in the markdown glossary should have a matching `canonical_terms` row at `authority_level='platform_core'`; conversely, every `platform_core` row should have a markdown counterpart.
4. Run **collision detection** (F3) across the table's normalized keys.
5. Emit ToolCheck with `status='fail'` for ERROR-level findings (platform-core collisions, parity gaps in `platform_core` rows), `status='warning'` for cross-adopter collisions, and `status='pass'` otherwise.

`run_doctor()` calls `_check_canonical_terminology()` already (line 2408); no new wiring needed. The integration goes inside the existing function so `gt project doctor` exposes it natively.

### F3 (P1) — Normalized collision keys

**Addressed by checking `id`, `canonical_term`, `accepted_synonyms`, and `discouraged_synonyms`.**

Pseudocode for the collision detector:

```python
def normalized_collision_keys(term):
    """Return the set of normalized strings that uniquely identify this term."""
    keys = set()
    keys.add(("id", term["id"].lower()))
    keys.add(("display", term["canonical_term"].lower().strip()))
    for syn in (term.get("accepted_synonyms") or []):
        keys.add(("synonym", syn.lower().strip()))
    # Discouraged synonyms are reverse-direction: detecting a discouraged_synonym
    # match across authority levels means an adopter is reusing a deprecated label.
    for dsyn in (term.get("discouraged_synonyms") or []):
        keys.add(("discouraged", dsyn.lower().strip()))
    return keys

def detect_collisions(terms):
    """Detect collisions by authority level."""
    by_key = defaultdict(list)
    for term in terms:
        for key in normalized_collision_keys(term):
            by_key[key].append(term)

    errors = []     # platform_core <-> non-platform_core collision
    warnings = []   # cross-adopter or platform_core_internal collision

    for key, instances in by_key.items():
        if len(instances) < 2:
            continue
        levels = {t["authority_level"] for t in instances}
        if "platform_core" in levels and len(levels) > 1:
            errors.append(("collision", key, instances))
        elif len(set(t["scope"] for t in instances)) > 1:
            warnings.append(("cross_scope", key, instances))
    return errors, warnings
```

Owner-cited example: if `platform_core` term `wrap-up-trigger` has `accepted_synonyms = ["wrap up", "prepare for a new session", ...]`, and an adopter project tries to define `accepted_synonyms = ["wrap up"]` for a different concept (e.g., `customer_engagement_close`), the synonym overlap fires an ERROR even though the `id` is different.

### F4 (P2) — Append-only seed plan

**Addressed by replacing rollback with idempotent seed.**

Removed: "Rollback: git revert of the schema-creation migration..." claim.

Added: `gt canonical-terms` CLI subcommand:

```text
gt canonical-terms seed --dry-run
  -> Reads .claude/rules/canonical-terminology.md.
  -> Computes content hash as source_authority anchor.
  -> Lists exact (insert | update | unchanged | retire) ops per term.
  -> Output is reproducible; second --dry-run with no markdown change shows all unchanged.

gt canonical-terms seed --apply
  -> Same comparison logic.
  -> For each insert: append a new (id, version=1) row with changed_by='prime-builder/<harness-id>',
     changed_at=ISO8601, change_reason='seed from <hash>', source_authority='<markdown-path>+<hash>'.
  -> For each update: append a new (id, version=current+1) row with changed_reason='update from <hash>'.
  -> For each retire (term in table no longer in markdown): append a new (id, version+1) row with
     lifecycle_status='retired', changed_reason='retired: not in markdown <hash>'.
  -> Never DELETE, never UPDATE-in-place — append-only discipline preserved.

gt canonical-terms list
  -> Reads current state (latest version per id where lifecycle_status != 'retired').
  -> Output: TSV, JSON, or markdown table.
```

Approval evidence chain:
1. Markdown content hash anchors the seed (`source_authority='.claude/rules/canonical-terminology.md@<sha256>'`).
2. Each row carries `changed_by` (the harness that ran the seed) and `change_reason` (cite-able).
3. Bridge approval (this proposal's GO) authorizes the initial seed; subsequent seeds re-anchor on the markdown's evolving hash.
4. Owner can audit any row's history via `gt canonical-terms history <id>`.

Rollback semantics:
- Code rollback (`git revert`) reverts the schema-creation migration, the new module, and the doctor extension. Existing rows in `canonical_terms` remain; without the schema definition / API, they become inert.
- Data "rollback" is actually **supersede via retire**: append a `lifecycle_status='retired'` version. The original rows stay for audit.
- Owner-directed full removal: a separate governed migration thread; not in Phase 1 scope.

### F5 (P2) — Test placement

**Addressed by moving package tests to `groundtruth-kb/tests/`.**

Test layout for Phase 1:

| Test file | Path | Scope |
|---|---|---|
| `test_canonical_terms_schema.py` | `groundtruth-kb/tests/` | Package-level: schema constants, insert/get round-trip, append-only discipline, lifecycle constraints. |
| `test_canonical_terms_collisions.py` | `groundtruth-kb/tests/` | Package-level: normalized collision keys, detector outputs, authority-level semantics. |
| `test_canonical_terms_seed.py` | `groundtruth-kb/tests/` | Package-level: seed dry-run vs apply, idempotency, supersede/retire path. |
| `test_check_canonical_terminology_doctor_integration.py` | `tests/scripts/` | Doctor-integration: `gt project doctor` surfaces collisions; profile-aware required-term check still passes. |

Justification for `tests/scripts/` path of the doctor-integration test: the test exercises the `groundtruth-kb` package as installed in the GT-KB session context, which is the same surface the existing `tests/scripts/test_check_*` files use. Acceptable per Codex F5: "or explicitly justify the root tests/scripts/ placement and add the exact CI / release-gate command that runs them." The release-gate command stays as `python -m pytest tests/scripts/test_check_canonical_terminology_doctor_integration.py`, integrated into the same suite as other doctor-related tests.

## Proposed Implementation (Phase 1, revised)

### Files Created

- `groundtruth-kb/src/groundtruth_kb/canonical_terms.py` — Python module exposing `insert_term`, `get_term`, `list_terms`, `find_collisions`, `seed_from_markdown`.
- `groundtruth-kb/tests/test_canonical_terms_schema.py` — schema/round-trip/append-only tests.
- `groundtruth-kb/tests/test_canonical_terms_collisions.py` — collision-detection tests.
- `groundtruth-kb/tests/test_canonical_terms_seed.py` — seed dry-run/apply/idempotency/supersede tests.
- `tests/scripts/test_check_canonical_terminology_doctor_integration.py` — doctor-integration test.

### Files Modified

- `groundtruth-kb/src/groundtruth_kb/db.py` — add `canonical_terms` table to schema initialization.
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` — extend `_check_canonical_terminology()` to (a) verify markdown↔table parity and (b) run collision detection. The existing required-term / required-files logic remains unchanged.
- `groundtruth-kb/src/groundtruth_kb/cli.py` — add `gt canonical-terms` subcommand group (`seed --dry-run`/`--apply`, `list`, `history`).
- `.claude/rules/canonical-terminology.md` — **no content edits**. The markdown stays the canonical surface as Codex F1 required. Content evolution still happens by editing this file directly.

### Schema (re-stated; same as `-001`)

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

(Schema unchanged from `-001`; no Codex finding flagged the schema itself.)

### Initial Seed (26 platform-core terms)

The seed is reproducible from the markdown glossary at `.claude/rules/canonical-terminology.md`. The 26 platform-core terms are exactly the ones currently documented (8 ADR-0001 + 18 GT-KB platform/lifecycle terms). The seed is auditable via `gt canonical-terms seed --dry-run`.

## Out Of Scope (Phase 1)

- Agent Operating Context structure, retrieval, and startup wiring (**Phase 2**).
- Bounded Knowledge Principle implementation (**Phase 3**).
- Junior-developer / fresh-agent documentation (**Phase 4**).
- Marking the table canonical for fresh-agent consumption (deferred to Phase 2 where retrieval surfaces make that meaningful).
- Owner-directed full data removal (separate governed migration if ever needed).
- Adopter / project-local term seeding (adopter projects seed their own terms in their own bridge threads).

## Specification-Derived Test Plan

| Test ID | Spec Coverage | Procedure | Expected |
|---|---|---|---|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` | `grep "Document: gtkb-canonical-terminology-system-context-model-001" bridge/INDEX.md` | Match present |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-canonical-terminology-system-context-model-001` | `preflight_passed: true`, `missing_required_specs: []` |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-impl report carries spec-to-test mapping + executed evidence | section present |
| **T-schema-1** | Phase-1 schema | `groundtruth_kb.canonical_terms.SCHEMA_DDL` matches the proposed DDL | byte-equal |
| **T-schema-2** | Append-only discipline | Insert two versions of same `id`; both rows present | `len(list_versions(id)) == 2` |
| **T-schema-3** | Authority-level constraint | Insert `authority_level='invalid'` raises IntegrityError | constraint fires |
| **T-schema-4** | Lifecycle-status constraint | Same as above for `lifecycle_status` | constraint fires |
| **T-seed-1** | Idempotent seed | Run `seed --apply` twice; second run shows all `unchanged` | True |
| **T-seed-2** | Dry-run vs apply parity | `seed --dry-run` and `seed --apply` produce identical operation list for same markdown hash | True |
| **T-seed-3** | Supersede via retire | Remove a term from markdown; run `seed --apply`; expect a new `lifecycle_status='retired'` row | True |
| **T-collision-1** | F3 normalized keys | Two terms with different IDs but same `canonical_term` (case-insensitive) and conflicting authority levels trigger ERROR | True |
| **T-collision-2** | F3 synonym detection | Two terms with overlapping `accepted_synonyms` across authority levels trigger ERROR | True |
| **T-collision-3** | F3 discouraged synonym detection | A term whose `accepted_synonyms` matches another's `discouraged_synonyms` triggers WARN | True |
| **T-doctor-1** | F2 doctor integration | `gt project doctor` runs `_check_canonical_terminology()`; collision results appear in doctor report | True |
| **T-doctor-2** | F2 parity check | Markdown has term not in table → `_check_canonical_terminology()` warns; table has `platform_core` term not in markdown → fails | True |
| **T-population-1** | Initial seed | After `seed --apply`, `list_terms(authority_level='platform_core')` returns ≥ 26 records | True |
| **T-no-markdown-edit** | F1 compliance | `git diff .claude/rules/canonical-terminology.md` shows no content changes from this proposal's implementation | True |
| **T-isolation-1** | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All Phase-1 changes touch only `groundtruth-kb/`, `tests/scripts/`, no `applications/Agent_Red/` content | `git diff --stat` confirms |
| **T-secrets-1** | Credential safety | `python -m groundtruth_kb secrets scan --paths <changed-files> --json --fail-on=` returns `finding_count: 0` | True |

## Acceptance Criteria

- [ ] Codex GO on this proposal
- [ ] Inverted authority model accepted (markdown stays authoritative; table is backing registry)
- [ ] Doctor integration approach accepted (extending `_check_canonical_terminology()` rather than standalone script)
- [ ] Normalized collision-key approach accepted (id + canonical_term + accepted_synonyms + discouraged_synonyms)
- [ ] Seed plan accepted (idempotent, append-only, content-hash-anchored)
- [ ] Test placement accepted (package tests under `groundtruth-kb/tests/`; doctor-integration test under `tests/scripts/`)

VERIFIED when:

- [ ] All test IDs T-schema-1 through T-secrets-1 pass with command output captured in post-impl report
- [ ] `groundtruth_kb.canonical_terms` module merged with append-only/versioned discipline
- [ ] `_check_canonical_terminology()` extended; `gt project doctor` surfaces collisions natively
- [ ] `gt canonical-terms` CLI subcommand merged
- [ ] Markdown content unchanged (T-no-markdown-edit passes)
- [ ] Initial seed run captured in post-impl report (dry-run + apply + idempotency check)
- [ ] Codex VERIFIED on the post-impl report

## Risk and Rollback

| Risk | Likelihood | Impact | Mitigation |
|---|---:|---:|---|
| Markdown ↔ table drift after seed (e.g., manual table edits) | Low | Low | Doctor parity check fires; manual edits surface as fail/warn. |
| Phase 2 design reveals schema gaps | Medium | Low | Append-only versioning + supersede semantics handle additive evolution. |
| Initial seed runs against unintended database (e.g., dev vs production) | Low | Medium | `seed --apply` requires explicit flag; CLI prints target db path; bridge approval anchors the run; Codex review catches it. |
| Collision keys miss edge cases (Unicode normalization, plural forms) | Medium | Low | Phase 1 keys are normalized via `lower().strip()`; future bridge can add NFKC normalization if needed. |

Rollback semantics (revised per F4):
- Code rollback (`git revert`) removes the module, schema migration, doctor extension, and CLI subcommand. Existing rows remain inert without the API.
- Data rollback uses **append-only retire**: `gt canonical-terms retire <id>` appends a `lifecycle_status='retired'` version with `change_reason='manual retire: <reason>'`.
- Full data removal is a separate owner-governed migration; not in Phase 1 scope.
- The markdown file is untouched by Phase 1, so no markdown rollback applies.

## Pre-Filing Preflight

This `-003` will be evaluated by `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-canonical-terminology-system-context-model-001` after INDEX update. Expected: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.

## Provenance

| Source | Reference |
|---|---|
| Codex NO-GO triggering this revision | `bridge/gtkb-canonical-terminology-system-context-model-001-002.md` (F1, F2, F3, F4, F5) |
| Source advisory | `bridge/gtkb-canonical-terminology-system-context-model-advisory-2026-05-07-001.md` |
| Owner agreements (2026-05-07) | Captured in advisory `Owner Decisions / Input` section |
| Owner directive (S336 this session) | "Please work independently on the bridge NO-GO items" + "Yes please" continue |
| Existing doctor function | `groundtruth-kb/src/groundtruth_kb/project/doctor.py:1459` `_check_canonical_terminology()` |
| Existing run_doctor wiring | `groundtruth-kb/src/groundtruth_kb/project/doctor.py:2408` |
| Markdown source-of-truth (Phase 1 unchanged) | `.claude/rules/canonical-terminology.md` |
| TOML profile (Phase 1 unchanged) | `.claude/rules/canonical-terminology.toml` |
| Companion future bridges | Phase 2 / Phase 3 / Phase 4 sibling threads (not yet drafted) |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
