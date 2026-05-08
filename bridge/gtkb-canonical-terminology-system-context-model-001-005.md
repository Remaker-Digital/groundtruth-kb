REVISED

# Implementation Proposal — GTKB-CANONICAL-TERMINOLOGY-SYSTEM-CONTEXT-MODEL-001 (Phase 1, Revised-2)

**Author:** Prime Builder (Claude, harness B)
**Drafted:** 2026-05-08
**Type:** Revision addressing Codex NO-GO at `bridge/gtkb-canonical-terminology-system-context-model-001-004.md` (single F1 finding: collision-key model still partitions accepted vs discouraged in different namespaces, and omits `forbidden_uses`).
**Predecessors:** `-001` NEW, `-002` NO-GO, `-003` REVISED, `-004` NO-GO.
**Source advisory:** `bridge/gtkb-canonical-terminology-system-context-model-advisory-2026-05-07-001.md`

## Claim

This `-005` revises the collision-key model per Codex `-004`'s required correction. The four prior findings Codex acknowledged as resolved in `-004` are preserved unchanged:

- ✅ Authority model inverted (markdown stays canonical for Phase 1; table is backing registry).
- ✅ Doctor integration via `_check_canonical_terminology()` rather than a standalone script.
- ✅ Idempotent, dry-run-capable, content-hash-anchored, append-only seed plan.
- ✅ Package tests under `groundtruth-kb/tests/` with explicit justification for the one root `tests/scripts/` doctor-integration test.

The single new fix in `-005`:

- **Unified text-surface collision key.** The detector now uses a single `("text", normalized_value)` namespace for all lexical surfaces (`canonical_term`, `accepted_synonyms`, `discouraged_synonyms`, `forbidden_uses`). Field-of-origin metadata is preserved per term so the post-detection classifier can label the collision (e.g., "term A's `accepted_synonym` matches term B's `discouraged_synonym`"). This makes the previously-claimed `T-collision-3` test executable — accepted-vs-discouraged and accepted-vs-forbidden cross-field text reuse now collide as the spec requires.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge proposals/reviews are governed through `bridge/INDEX.md`; this proposal is delivered via that protocol.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every implementation proposal cites its governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires spec-derived tests; mapping below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — application files under `applications/`; this proposal touches platform code only.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable artifact-oriented governance.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — durable artifacts, lifecycle states, traceable evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — terminology additions and changes have explicit lifecycle states.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` — owner-visible confirmation for chat-derived specs.
- `SPEC-TERMINOLOGY-DOCTOR-CHECK` — current doctor-check spec (cited at `groundtruth-kb/src/groundtruth_kb/project/doctor.py:1460`).
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
- `bridge/gtkb-canonical-terminology-system-context-model-001-001.md` — original NEW.
- `bridge/gtkb-canonical-terminology-system-context-model-001-002.md` — Codex NO-GO (5 findings; addressed in -003).
- `bridge/gtkb-canonical-terminology-system-context-model-001-003.md` — superseded REVISED-1.
- `bridge/gtkb-canonical-terminology-system-context-model-001-004.md` — Codex NO-GO (single F1 finding; addressed in this -005).
- `groundtruth-kb/templates/rules/canonical-terminology-policy.toml` — scaffold template; Phase 1 does NOT change this.
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` — `_check_canonical_terminology()` at line 1459; `run_doctor()` at line 2408.
- `groundtruth-kb/src/groundtruth_kb/db.py` — MemBase Python API.
- `DELIB-S334-CANONICAL-TERMINOLOGY-SYSTEM-OWNER-DECISION` — owner decision naming the feature.
- `DELIB-S334-AGENT-OPERATING-CONTEXT-OWNER-DECISION` — owner decision (Phase 2 scope).
- `DELIB-S334-BOUNDED-KNOWLEDGE-COMPLEXITY-OWNER-DECISION` — owner decision (Phase 3 scope).
- `DELIB-0722` — prior verified bridge thread for canonical terminology surface.
- `DELIB-1017` — prior GO for GT-KB IDP terminology formalization.

## Owner Decisions / Input

The four 2026-05-07 owner agreements (cited from the source advisory; no new AUQ requested for this revision):

| Decision | Source | Disposition for Phase 1 |
|---|---|---|
| "Canonical Terminology System" preferred name | 2026-05-07 owner agreement | Used throughout. |
| Users may add terms; core terminology is implicitly linked to processes/data/services | 2026-05-07 owner framing | `authority_level` field distinguishes `platform_core` / `adopter_extension` / `project_local`. |
| Initialized agents must be aware of core canonical terminology | 2026-05-07 owner requirement | **Phase 2 scope.** Phase 1 unchanged. |
| GT-KB has practical complexity ceiling | 2026-05-07 owner agreement | **Phase 3 scope.** Phase 1 stays minimal. |

The S336 owner directive ("Please work independently on the bridge NO-GO items" + "Yes please" continue + "Please proceed with filing -005") authorizes this revision under the same standing scope as the other items in this session.

## Findings Addressed

### F1 (P1) — Collision-key model still partitions accepted vs discouraged surfaces; omits `forbidden_uses`

**Addressed by adopting a unified text-surface key with field-of-origin metadata.**

Codex's `-004` evidence:

```python
keys.add(("synonym", syn.lower().strip()))         # accepted_synonyms
keys.add(("discouraged", dsyn.lower().strip()))    # discouraged_synonyms
```

That partitioned by field type before collision detection — so the same string in `accepted_synonyms` of term A and `discouraged_synonyms` of term B never collided. The proposal's own `T-collision-3` (which says accepted-vs-discouraged collisions must trigger WARN) was unsatisfiable. `forbidden_uses` was also missing entirely.

Revised `-005` collision-key model:

```python
def normalized_text_keys(term):
    """Return the set of (kind, normalized_text) keys for this term's
    structural-uniqueness identifier and lexical-surface texts.

    Structural keys (id) are kept namespaced because they identify the term,
    not its surface text. Lexical-surface keys all share the ('text', value)
    namespace so that cross-field text reuse is detected — accepted-vs-discouraged,
    accepted-vs-forbidden, discouraged-vs-canonical_term, etc.
    """
    keys = set()
    # Structural identifier (term-uniqueness key; stays namespaced).
    keys.add(("id", term["id"].lower().strip()))
    # Lexical surfaces (unified text namespace; cross-field reuse detected).
    if term.get("canonical_term"):
        keys.add(("text", term["canonical_term"].lower().strip()))
    for syn in (term.get("accepted_synonyms") or []):
        if syn:
            keys.add(("text", syn.lower().strip()))
    for dsyn in (term.get("discouraged_synonyms") or []):
        if dsyn:
            keys.add(("text", dsyn.lower().strip()))
    for fuse in (term.get("forbidden_uses") or []):
        if fuse:
            keys.add(("text", fuse.lower().strip()))
    return keys


def text_surface_origin(term):
    """Return {normalized_text: list-of-(field, raw_value)} so the collision
    classifier can label the field-of-origin per side after detection."""
    origins = defaultdict(list)
    if term.get("canonical_term"):
        origins[term["canonical_term"].lower().strip()].append(("canonical_term", term["canonical_term"]))
    for syn in (term.get("accepted_synonyms") or []):
        if syn:
            origins[syn.lower().strip()].append(("accepted_synonym", syn))
    for dsyn in (term.get("discouraged_synonyms") or []):
        if dsyn:
            origins[dsyn.lower().strip()].append(("discouraged_synonym", dsyn))
    for fuse in (term.get("forbidden_uses") or []):
        if fuse:
            origins[fuse.lower().strip()].append(("forbidden_use", fuse))
    return origins


def detect_collisions(terms):
    """Two-pass detector: collect → classify → classify-by-authority."""
    by_key = defaultdict(list)        # {(kind, value): [terms]}
    text_origin = {}                  # {term_id: {normalized_text: [(field, raw)]}}
    for term in terms:
        text_origin[term["id"]] = text_surface_origin(term)
        for key in normalized_text_keys(term):
            by_key[key].append(term)

    errors = []     # platform_core ↔ non-platform_core collisions
    warnings = []   # cross-scope, cross-adopter, cross-field collisions

    for key, instances in by_key.items():
        if len(instances) < 2:
            continue
        kind, value = key
        levels = {t["authority_level"] for t in instances}
        scopes = {t["scope"] for t in instances}
        # For text-surface collisions, look up per-term field-of-origin to
        # classify (e.g., "accepted-vs-discouraged" cross-field reuse).
        if kind == "text":
            origin_pairs = [
                (t["id"], text_origin[t["id"]].get(value, []))
                for t in instances
            ]
        else:
            origin_pairs = [(t["id"], [("id", t["id"])]) for t in instances]

        if "platform_core" in levels and len(levels) > 1:
            errors.append({
                "key": key,
                "instances": instances,
                "origin_pairs": origin_pairs,
                "classification": "platform_core_redefinition",
            })
        elif len(scopes) > 1:
            warnings.append({
                "key": key,
                "instances": instances,
                "origin_pairs": origin_pairs,
                "classification": "cross_scope_overlap",
            })
        elif kind == "text":
            # Same-scope text reuse across heterogeneous fields (e.g., one
            # term's accepted_synonym matches another's discouraged_synonym
            # in the same scope). Surface as WARN per T-collision-3.
            field_kinds_per_instance = [
                {f for (f, _) in origin_pairs[i][1]} for i in range(len(instances))
            ]
            if len(set().union(*field_kinds_per_instance)) > 1:
                warnings.append({
                    "key": key,
                    "instances": instances,
                    "origin_pairs": origin_pairs,
                    "classification": "cross_field_text_reuse",
                })
    return errors, warnings
```

Owner-cited example from the source advisory ("wrap up", "prepare for a new session" as drift controls):

- Suppose `platform_core` term `wrap-up-trigger` has `accepted_synonyms = ["wrap up", "prepare for a new session"]`.
- An adopter project tries to define `customer_engagement_close` with `discouraged_synonyms = ["wrap up"]` (intending to discourage that phrase in their own scope, not realizing it overlaps the platform's accepted synonym).
- The unified `("text", "wrap up")` key collects both terms' instances.
- Classifier: `platform_core_redefinition` (because levels = {platform_core, adopter_extension}); reported as ERROR with origin metadata showing `wrap-up-trigger.accepted_synonym` vs `customer_engagement_close.discouraged_synonym`.

Same example with both terms inside a single adopter scope:

- Two adopter terms in the same scope share `("text", "wrap up")` via different field origins.
- Classifier: `cross_field_text_reuse`; reported as WARN per `T-collision-3`.

`forbidden_uses` collisions follow the same model (e.g., one term's `accepted_synonym` matches another's `forbidden_use` triggers a cross-field WARN; if it crosses authority levels, it escalates to ERROR via `platform_core_redefinition`).

### Findings preserved unchanged from `-003` (which `-004` accepted)

- **Authority model inverted (formerly F1):** Markdown/TOML stay startup-readable authoritative; the `canonical_terms` table is a structured backing registry with parity checks. No "table is canonical" claim in the markdown.
- **Doctor integration (formerly F2):** Collision detection extends `groundtruth_kb.project.doctor._check_canonical_terminology()`. No standalone script.
- **Append-only seed (formerly F4):** `gt canonical-terms seed --dry-run`/`--apply`; idempotent; content-hash-anchored; supersede-via-retire. No "git revert removes data" claim.
- **Test placement (formerly F5):** Package tests under `groundtruth-kb/tests/`; doctor-integration test under `tests/scripts/` (justified as exercising the GT-KB session-context surface).

## Proposed Implementation (Phase 1, revised-2)

### Files Created (unchanged from `-003`)

- `groundtruth-kb/src/groundtruth_kb/canonical_terms.py` — module exposing `insert_term`, `get_term`, `list_terms`, `find_collisions`, `seed_from_markdown`. The `find_collisions` function implements the unified text-surface model above.
- `groundtruth-kb/tests/test_canonical_terms_schema.py` — schema/round-trip/append-only tests.
- `groundtruth-kb/tests/test_canonical_terms_collisions.py` — collision-detection tests (now exercising T-collision-1 through T-collision-4 below).
- `groundtruth-kb/tests/test_canonical_terms_seed.py` — seed dry-run/apply/idempotency/supersede tests.
- `tests/scripts/test_check_canonical_terminology_doctor_integration.py` — doctor-integration test.

### Files Modified (unchanged from `-003`)

- `groundtruth-kb/src/groundtruth_kb/db.py` — add `canonical_terms` table to schema initialization.
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` — extend `_check_canonical_terminology()` to verify markdown↔table parity and run collision detection (new model from this revision).
- `groundtruth-kb/src/groundtruth_kb/cli.py` — add `gt canonical-terms` subcommand group.
- `.claude/rules/canonical-terminology.md` — **no content edits.**

### Schema (unchanged from `-001`/`-003`)

The schema already includes `forbidden_uses TEXT` per `-001`'s DDL, so no schema change is needed for `-005`. The detector now consumes that field; the table column was always present.

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

### Initial Seed (unchanged from `-003`)

26 platform-core terms reproducibly seeded from `.claude/rules/canonical-terminology.md`; auditable via `gt canonical-terms seed --dry-run`.

## Out Of Scope (unchanged from `-003`)

- Agent Operating Context structure, retrieval, and startup wiring (Phase 2).
- Bounded Knowledge Principle implementation (Phase 3).
- Junior-developer / fresh-agent documentation (Phase 4).
- Marking the table canonical for fresh-agent consumption (deferred to Phase 2).
- Owner-directed full data removal (separate governed migration).
- Adopter / project-local term seeding.

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
| **T-seed-1** | Idempotent seed | Run `seed --apply` twice; second shows all `unchanged` | True |
| **T-seed-2** | Dry-run vs apply parity | `seed --dry-run` and `seed --apply` produce identical operation list | True |
| **T-seed-3** | Supersede via retire | Remove a term from markdown; `seed --apply` appends `retired` row | True |
| **T-collision-1** | F1 unified text key — id collision across authority levels | Two terms with same `id`, different `authority_level` | ERROR |
| **T-collision-2** | F1 unified text key — display-term collision across authority levels | Two terms with different IDs but same `canonical_term` (case-insensitive); levels include `platform_core` and `adopter_extension` | ERROR |
| **T-collision-3** | F1 cross-field text reuse — accepted vs discouraged synonyms | Two same-scope terms; A.`accepted_synonyms = ["wrap up"]`, B.`discouraged_synonyms = ["wrap up"]` | WARN, classification `cross_field_text_reuse`, origin metadata pairs `(A, accepted_synonym)` and `(B, discouraged_synonym)` |
| **T-collision-4** | F1 cross-field text reuse — accepted vs forbidden uses (NEW) | A.`accepted_synonyms = ["customer signal"]`, B.`forbidden_uses = ["customer signal"]`, same scope | WARN, classification `cross_field_text_reuse`, origin metadata pairs `(A, accepted_synonym)` and `(B, forbidden_use)` |
| **T-collision-5** | F1 cross-authority text reuse — synonym overlap | A `platform_core` `accepted_synonyms = ["wrap up"]`, B `adopter_extension` `accepted_synonyms = ["wrap up"]` | ERROR, classification `platform_core_redefinition` |
| **T-doctor-1** | Doctor integration | `gt project doctor` exposes collision results | True |
| **T-doctor-2** | Parity check | Markdown ↔ table mismatch surfaces in doctor output | True |
| **T-population-1** | Initial seed | After `seed --apply`, `list_terms(authority_level='platform_core')` returns ≥ 26 records | True |
| **T-no-markdown-edit** | Authority-model preservation | `git diff .claude/rules/canonical-terminology.md` shows no content changes from this proposal's implementation | True |
| **T-isolation-1** | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Phase-1 changes touch only `groundtruth-kb/`, `tests/scripts/`, no `applications/Agent_Red/` content | `git diff --stat` confirms |
| **T-secrets-1** | Credential safety | `python -m groundtruth_kb secrets scan --paths <changed-files> --json --fail-on=` returns `finding_count: 0` | True |

T-collision-3 and T-collision-4 are the previously unsatisfiable tests Codex flagged; both are now executable under the unified text-surface key model. T-collision-5 is added to make the platform_core-redefinition path explicit.

## Acceptance Criteria

- [ ] Codex GO on this proposal
- [ ] Unified text-surface collision-key model accepted
- [ ] Field-of-origin metadata for post-detection classification accepted
- [ ] `forbidden_uses` inclusion in collision detection accepted
- [ ] T-collision-1 through T-collision-5 acceptance criteria accepted

VERIFIED when:

- [ ] All test IDs pass with command output captured in post-impl report
- [ ] `groundtruth_kb.canonical_terms` module merged with the unified text-surface detector
- [ ] `_check_canonical_terminology()` extended; `gt project doctor` surfaces collisions natively
- [ ] `gt canonical-terms` CLI subcommand merged
- [ ] Markdown content unchanged
- [ ] Initial seed run captured (dry-run + apply + idempotency check)
- [ ] Codex VERIFIED on the post-impl report

## Risk and Rollback

| Risk | Likelihood | Impact | Mitigation |
|---|---:|---:|---|
| Unified text key creates false positives in benign cases (e.g., a term legitimately appears in another term's `usage_examples`) | Low | Low | `usage_examples` is excluded from the surface set; only fields the owner elevated as drift controls participate. |
| Unicode normalization edge cases (e.g., NFC vs NFKC) | Medium | Low | Phase 1 uses `lower().strip()`; future bridge can add NFKC if needed. |
| Phase 2 reveals additional fields that should participate in collision detection | Medium | Low | Append a new field to the surface set; no schema change needed. |
| Initial seed runs against unintended database | Low | Medium | `seed --apply` requires explicit flag; CLI prints target db path; bridge approval anchors the run. |

Rollback semantics (carried forward from `-003`):
- Code rollback (`git revert`) removes the module, schema migration, doctor extension, and CLI subcommand.
- Data rollback uses append-only retire (`gt canonical-terms retire <id>`).
- Full data removal is a separate owner-governed migration.

## Pre-Filing Preflight

This `-005` will be evaluated by `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-canonical-terminology-system-context-model-001` after INDEX update. Expected: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.

## Provenance

| Source | Reference |
|---|---|
| Codex NO-GO triggering this revision | `bridge/gtkb-canonical-terminology-system-context-model-001-004.md` (single F1 finding on collision-key partitioning + missing forbidden_uses) |
| Codex acknowledged-resolved findings (preserved) | `-002` F1 (authority model), F2 (doctor integration), F4 (seed plan), F5 (test placement) — addressed in `-003`, accepted in `-004` |
| Source advisory | `bridge/gtkb-canonical-terminology-system-context-model-advisory-2026-05-07-001.md` |
| Owner agreements (2026-05-07) | Captured in advisory `Owner Decisions / Input` section |
| Owner directive (S336 this session) | "Please work independently on the bridge NO-GO items" → "Yes please" continue → "Please proceed with filing -005" |
| Existing doctor function | `groundtruth-kb/src/groundtruth_kb/project/doctor.py:1459` `_check_canonical_terminology()` |
| Markdown source-of-truth (Phase 1 unchanged) | `.claude/rules/canonical-terminology.md` |
| Companion future bridges | Phase 2 / Phase 3 / Phase 4 sibling threads (not yet drafted) |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
