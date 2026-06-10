NEW

# GTKB Spec Lifecycle Schema Migration (scoping)

**Status:** NEW
**Date:** 2026-04-29
**Author:** Prime Builder (Claude, current session)
**Trigger:** Codex Loyal Opposition advisory at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/SPEC-LIFECYCLE-SCHEMA-ADVISORY-2026-04-29-15-50.md`. Owner directive 2026-04-29 to "replace flawed specification lifecycle fields before Prime Builder formulates an implementation proposal", plus owner addition that the proposal "should include a `parent` attribute that specifies whether the spec applies to the GT-KB platform, the application under development or *all*".

bridge_kind: prime_proposal
work_item_ids: [GTKB-SPEC-LIFECYCLE-SCHEMA-MIGRATION]
spec_ids: [SPEC-PROJECT-DASHBOARD-KPI-LINK-001]
target_project: groundtruth-kb
implementation_scope: schema_migration
requires_review: true
requires_verification: true

---

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate. Codex MUST NO-GO this proposal if any relevant specification is missing.

**Owner directives this bridge serves:**
- Codex advisory `SPEC-LIFECYCLE-SCHEMA-ADVISORY-2026-04-29-15-50.md` (Loyal Opposition source document; will be archived as a deliberation post-GO).
- Owner addition 2026-04-29 (this session): proposal must include `parent` attribute (`gtkb` / `application` / `all`) on every spec.

**Governance specs / records that constrain this work:**
- `GOV-ARTIFACT-APPROVAL-001`, `ADR-ARTIFACT-FORMALIZATION-GATE-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001` — schema migration adds new write-paths (`mark_spec_implementation_verified`, `retire_spec`); each implementation slice must declare which formal-artifact-approval path applies.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the date-field migration interacts with bridge `VERIFIED` evidence (per advisory §Live Data Impact: "Existing `verified` specs can map to `implementation_verified_at` from their first `verified` version timestamp"); the bridge's role as truth source must be preserved.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (DELIB-0874) — date-bearing lifecycle facts are themselves artifacts; aligns with artifact-oriented direction.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the new write-path API (one method per state transition: verify, retire, link-source) is a deterministic-services move (CLI/service surface for what was previously inferred from string parsing).
- `GOV-AGENT-RED-GTKB-CONFORMANCE-001` — the `parent` attribute makes Agent Red ↔ GT-KB scope distinction explicit at the artifact level.

**Adjacent / parallel work:**
- `bridge/active-workspace-declaration-architecture-2026-04-29-001.md` (NO-GO at -002 from Codex). The `parent` attribute is the spec-level analog of the workspace-declaration concept. **This proposal does NOT depend on the active-workspace bridge reaching GO** — they can ship in parallel — but Slice 1's `parent` design must remain consistent with whatever the active-workspace architecture eventually settles on for the workspace-identity vocabulary.
- `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-006.md` (GO). The triad audit utility committed at `73c41ee4` (`scripts/audit_gtkb_triad_completeness.py`) is part of the spec-coverage observational program; this migration changes the audit's `TERMINAL_SPEC_STATUSES = {"implemented", "verified"}` definition.

**Rule files that constrain this work:**
- `.claude/rules/project-root-boundary.md` — all migration artifacts under `E:\GT-KB`; upstream changes route to `E:\GT-KB\groundtruth-kb\` (in-root).
- `.claude/rules/file-bridge-protocol.md` — Mandatory Root Boundary Gate, Mandatory Specification Linkage Gate, Mandatory Specification-Derived Verification Gate satisfied here at scoping; per-slice implementation bridges will repeat for their scope.
- `.claude/rules/codex-review-gate.md` — codifies that Codex MUST NO-GO any unlinked proposal.

**Test derivation statement** (per file-bridge-protocol Mandatory Specification-Derived Verification Gate):

This is a SCOPING bridge; it proposes no tests itself. Each subsequent slice's implementation bridge will declare tests derived from the advisory's 10 acceptance criteria (advisory §Acceptance Criteria) plus the `parent` attribute's own assertions. Mapping table:

| Slice | Advisory acceptance criteria covered | Parent attribute coverage |
|-------|--------------------------------------|---------------------------|
| 1 (schema) | Foundation for #1, #6, #7, #10; introduces columns/table | Add `parent` column with CHECK constraint over enum |
| 2 (API + gates) | #2, #3, #4 (LO-gated verify, owner-gated retire, source-link API) | `parent` required on `insert_spec`; immutable on `update_spec` (separate `set_spec_parent` op) |
| 3 (read paths) | #5, #9 (date-derived lifecycle counts; triad audit uses dates) | Read paths surface `parent`; counts available per-parent |
| 4 (write paths + intake) | #6 (priority absent from spec paths) | Intake flows assign `parent` per workspace; backfill rules documented |
| 5 (UI/CLI/docs) | #6, #7 + UI-side coverage | UI filters by `parent`; CLI surfaces per-parent |
| 6 (cleanup) | Final closure of all 10 + #8 multi-source linkage proven | Old `status`/`priority`/`authority`/`provisional_until` removed from spec API |

Per-slice implementation bridges will detail exact test files, fixtures, and assertions before each slice receives GO.

---

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`:

- **`DELIB-0636`** (S279): Lifecycle Metrics Proposal Review. Original justification for the `specified → implemented → verified` lifecycle metric. Superseded by this proposal per owner directive.
- **`DELIB-0791`** (verified): `gtkb-f1-implementation` bridge thread. Lifecycle column additions.
- **`DELIB-0808`**: `gtkb-spec-pipeline-f1` bridge thread. Spec pipeline foundation.
- **`DELIB-1196`** + **`DELIB-1245`**: later imports of the F1 threads.
- **`DELIB-0707`** (owner conversation): owner required existing specs to be migrated to enriched schema using implementation as reference. Migration rule lineage.
- **`DELIB-1403`** (owner correction): Loyal Opposition requests owner approval/rejection or re-authorization instead of approving/rejecting specs itself. Reinforces that retirement requires owner approval (advisory acceptance criterion #4).
- **No prior deliberation reverses this approach.** The previous lifecycle-status model is being replaced by owner directive; prior deliberations explain why the old model exists but do not block the replacement.

---

## 1. Problem Statement (carried from advisory §Advisory Claim)

The current spec `status` model conflates four orthogonal concerns: existence, implementation, verification, and retirement. `priority`, `authority`, and `provisional_until` encode planning and provenance concepts in the wrong place. The owner-defined target model uses two nullable date fields (`implementation_verified_at`, `retired_at`) plus a relationship table for deliberation sources, with `priority` removed (it belongs on backlog/work-items only).

**Plus owner addition (this session):** every spec must carry a `parent` attribute identifying whether it applies to the GT-KB platform, the application under development, or *all*. This makes the workspace-identity classification explicit at the artifact level — currently the classification is inferred from id prefix, section, or context, producing the same kind of ambiguity the active-workspace-declaration architecture aims to resolve at the workspace level.

**Live data scope (per advisory §Live Data Impact):** 2,181 current specifications in `groundtruth.db`; 1,588 `implemented`, 339 `verified`, 202 `retired`, 52 `specified`; 76 with `authority='stated'`; 365 with non-null `priority`. All affected by the migration; backfill rules must be documented before any data is rewritten.

---

## 2. Recovery Program Structure (Six Slices)

This bridge is a **scoping proposal**. On GO, six implementation bridges follow. Slices ordered by dependency. Each implementation bridge files its own NEW → GO → implement → post-impl → VERIFIED cycle.

### 2.1 Slice 1 — Schema additions (new columns + source-link table + `parent`)

**Thread name (proposed):** `gtkb-spec-lifecycle-schema-slice-1-additions-2026-04-29`

**Deliverable:** add new columns/tables to `current_specifications` schema while leaving old columns in place (compatibility window). Old columns marked deprecated in API docs but readable/writable for back-compat.

**New columns on `specifications` (and `current_specifications` view):**
- `implementation_verified_at TEXT` (nullable; ISO8601 timestamp; only LO can set per Slice 2 gate)
- `retired_at TEXT` (nullable; ISO8601 timestamp; requires owner approval evidence per Slice 2 gate)
- `parent TEXT NOT NULL CHECK (parent IN ('gtkb', 'application', 'all'))` — per owner addition. **No default**: every insert must pass `parent`; backfill applies a one-time migration rule per §3.

**New table:**
```sql
CREATE TABLE specification_deliberation_sources (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    spec_id TEXT NOT NULL,
    spec_version INTEGER NOT NULL,
    deliberation_id TEXT NOT NULL,
    source_role TEXT,
    added_at TEXT NOT NULL,
    added_by TEXT NOT NULL,
    UNIQUE(spec_id, spec_version, deliberation_id)
);
```

**Files touched (Slice 1):**
- `groundtruth-kb/src/groundtruth_kb/db.py` — schema additions + migration script.
- `groundtruth-kb/tests/test_db.py` — schema-shape tests; existing tests unchanged.

**Why first:** every later slice depends on these columns/table existing.

**Does NOT deliver:** API write-paths for the new columns (Slice 2); read-path queries (Slice 3); UI/CLI updates (Slice 5); old-column removal (Slice 6).

### 2.2 Slice 2 — API additions + lifecycle gates

**Thread name (proposed):** `gtkb-spec-lifecycle-schema-slice-2-api-gates-2026-04-29`

**Deliverable:** new write-path methods + actor/evidence-gated permissions. Old `update_spec(status=...)` paths still work during compat window but emit deprecation warnings.

**New API methods on `KnowledgeDB`:**
- `mark_spec_implementation_verified(spec_id, verified_at, verified_by, evidence_ref)` — gate: `verified_by` must indicate Loyal Opposition actor (`changed_by` patterns matching `loyal-opposition/*` or explicit LO actor evidence); `evidence_ref` must point to a bridge `VERIFIED` file or equivalent.
- `retire_spec(spec_id, retired_at, owner_approval_ref, retired_by)` — gate: `owner_approval_ref` must point to a deliberation with `outcome=owner_decision` and `source_type=owner_conversation` (or equivalent owner-approval packet).
- `link_spec_deliberation_source(spec_id, spec_version, deliberation_id, source_role)` — adds row to `specification_deliberation_sources`; idempotent on `UNIQUE(spec_id, spec_version, deliberation_id)`.
- `set_spec_parent(spec_id, parent, changed_by, change_reason)` — separate operation because `parent` is significant enough to require explicit change rationale; not allowed via generic `update_spec`. **Initial value set at `insert_spec`.**

**New gates in `gates.py` and `gates_transport.py`:**
- Replace `pre_promote(current_status, target_status, ...)` for specs with date-setting gates (LO authority for verification; owner approval for retirement).
- Old promotion gates remain for compat; new gates take precedence when both columns are present.

**Files touched (Slice 2):**
- `groundtruth-kb/src/groundtruth_kb/db.py` — new methods.
- `groundtruth-kb/src/groundtruth_kb/gates.py` + `gates_transport.py` — new gates.
- `groundtruth-kb/tests/test_db.py` + `test_gates.py` + `test_gates_transport.py` — coverage for gates and authority enforcement.

**Why second:** depends on Slice 1 columns; later slices read these new write paths.

### 2.3 Slice 3 — Read-path migration (lifecycle queries + audits)

**Thread name (proposed):** `gtkb-spec-lifecycle-schema-slice-3-read-paths-2026-04-29`

**Deliverable:** all derived-lifecycle queries use new date columns. Old status-string reads still work during compat window but emit deprecation warnings.

**Lifecycle derivation rules:**
- `active/unverified`: `implementation_verified_at IS NULL AND retired_at IS NULL`
- `implemented`: `implementation_verified_at IS NOT NULL AND retired_at IS NULL`
- `retired`: `retired_at IS NOT NULL`

**Files touched (Slice 3):**
- `groundtruth-kb/src/groundtruth_kb/db.py` — `list_specs()`, `get_provisional_specs()`, `_row_to_dict()`, lifecycle metrics.
- `groundtruth-kb/src/groundtruth_kb/reconciliation.py` — remove authority-conflict + provisional-replacement logic; replace with deliberation-source coverage + retirement-approval checks.
- `groundtruth-kb/src/groundtruth_kb/impact.py` — replace authority distribution with source/evidence coverage; add per-`parent` distribution.
- `scripts/audit_gtkb_triad_completeness.py` (already committed at `73c41ee4`) — change `TERMINAL_SPEC_STATUSES = {"implemented", "verified"}` to date-derived (`implementation_verified_at IS NOT NULL`); add `parent`-aware bucketing.
- `tests/scripts/test_audit_gtkb_triad_completeness.py` — fixture rewrite for new schema.
- `groundtruth-kb/tests/test_lifecycle_metrics.py`, `test_reconciliation.py` — coverage for new derivations.

**Why third:** API write-paths (Slice 2) must exist for these reads to be testable end-to-end.

### 2.4 Slice 4 — Write-path migration (intake + scaffold + skill + seed)

**Thread name (proposed):** `gtkb-spec-lifecycle-schema-slice-4-write-paths-2026-04-29`

**Deliverable:** spec creation paths no longer set lifecycle status; `parent` is required input; deliberation provenance lands in `specification_deliberation_sources`.

**Files touched (Slice 4):**
- `groundtruth-kb/src/groundtruth_kb/intake.py` — `capture_requirement`, `confirm_intake`, `reject_intake` no longer set `status='specified'`; `parent` parameter required.
- `groundtruth-kb/src/groundtruth_kb/spec_scaffold.py` + `adr_scaffold.py` — generated specs omit `status` and `authority`; `parent` defaulted from generation context (e.g., ADR-* default `parent='all'` because architecture decisions cross workspaces; SPEC-INTAKE-* default `parent` from intake context).
- `groundtruth-kb/templates/skills/spec-intake/SKILL.md` + `helpers/spec_intake.py` — intake flow asks for `parent` (or infers from active-workspace state if active-workspace bridge has GO'd by then).
- `groundtruth-kb/src/groundtruth_kb/seed.py` — seed examples use new schema.
- `groundtruth-kb/tests/test_intake.py` + `test_spec_scaffold.py` — coverage.

**Backfill rules (one-time migration script, run at Slice 4 deployment):**
- Specs with id prefix `GTKB-*` OR section LIKE `gtkb-*` → `parent='gtkb'`
- Specs with id prefix `AR-*`, `SHOPIFY-*`, `CUSTOMER-*` OR section LIKE `agent-red-*` / `customer-*` / `shopify-*` → `parent='application'`
- Specs with `type='governance'` OR `type='protected_behavior'` OR id prefix `GOV-*` / `ADR-*` / `DCL-*` → `parent='all'`
- Specs with `type='requirement'` and `section='membase-effective-use'` (the SPEC-INTAKE-* specs) → `parent='all'` (infrastructure for both workspaces)
- Specs with `id LIKE 'SPEC-INTAKE-*'` → `parent='all'` (intake mechanics apply to both workspaces)
- All other specs → flag for owner-review backfill (write to a triage list; do NOT auto-classify)

`implementation_verified_at` backfill: only for specs with current `status='verified'` AND existing bridge `VERIFIED` evidence (queried from `bridge/INDEX.md` and the bridge files); use the first `verified` version's `changed_at` timestamp. Specs at `status='verified'` without bridge VERIFIED evidence stay null; the migration script flags them for owner review.

`retired_at` backfill: only for specs at current `status='retired'` AND with a deliberation having `outcome=owner_decision` referencing the spec id. Otherwise the migration script flags them for owner backfill (do NOT silently trust the retired status string).

**Why fourth:** depends on Slices 1-3 being available so the backfill script can write to the new columns and the intake flow can use the new write APIs and read paths.

### 2.5 Slice 5 — UI/CLI/docs migration

**Thread name (proposed):** `gtkb-spec-lifecycle-schema-slice-5-ui-cli-docs-2026-04-29`

**Deliverable:** all surfaces use new schema; old status-based filters/cards removed.

**Files touched (Slice 5):**
- `groundtruth-kb/src/groundtruth_kb/web/app.py` + `templates/{dashboard,specs,spec_detail,pipeline}.html` — replace status filters with date-derived lifecycle filters; add `parent` filter; show `implementation_verified_at`, `retired_at`, deliberation source coverage; remove spec-priority filters/columns.
- `groundtruth-kb/src/groundtruth_kb/dashboard.py` — same pattern.
- `groundtruth-kb/src/groundtruth_kb/cli.py` — replace `gt kb status` spec status counts with active/unverified/implementation-verified/retired counts; remove `--authority`; add `--parent` filter.
- `groundtruth-kb/docs/reference/cli.md`, `start-here.md`, `method/01-overview.md`, `method/02-specifications.md`, `method/05-governance.md`, `method/10-tooling.md`, `user-journey.md`, `changelog.md`, `bootstrap.md` — documentation updates.
- `groundtruth-kb/docs/tutorials/first-spec.md`, `day-in-the-life.md`, `evidence.md` — example updates showing new schema + `parent`.

**Why fifth:** depends on backend (Slices 1-4) being in place; UI/CLI/docs reflect what's already working.

### 2.6 Slice 6 — Old-column removal (cleanup; final closure)

**Thread name (proposed):** `gtkb-spec-lifecycle-schema-slice-6-cleanup-2026-04-29`

**Deliverable:** old `status`, `priority`, `authority`, `provisional_until` removed from active spec API surface (still readable from older versions for audit trail; not writable). All read/write paths use new model. Final regression test pass.

**Files touched (Slice 6):**
- `groundtruth-kb/src/groundtruth_kb/db.py` — remove old columns from active write API; preserve in legacy-version read paths.
- All test files — remove deprecation-warning assertions; ensure no test references old columns.
- All docs — remove references to old `status`, `priority`, `authority` semantics for specs (preserve historical mention in changelog).

**Why last:** can only happen after every read/write path uses the new model.

---

## 3. Backfill Strategy Detail (per advisory §Live Data Impact)

The migration script (Slice 4 deliverable) operates in three phases:

**Phase 3.1 — Schema backfill (one-time)**
- Add columns/table per Slice 1.
- Backfill `parent` per §2.4 rules. Flag ambiguous specs for owner review (write to `memory/triage-spec-parent-backfill.md`).
- Backfill `implementation_verified_at` per §2.4 rules (verified-only with bridge evidence). Flag ambiguous for owner review.
- Backfill `retired_at` per §2.4 rules (retired-only with owner-decision evidence). Flag ambiguous for owner review.

**Phase 3.2 — Compat window (Slices 1-5 active simultaneously)**
- Old columns remain readable/writable; new columns take precedence in derived queries.
- Deprecation warnings on old API paths.
- Tests verify both old and new paths produce consistent results.

**Phase 3.3 — Cleanup (Slice 6)**
- Old columns removed from active API.
- Old-column data preserved in version-history rows (append-only schema means no destructive deletion).

---

## 4. Acceptance Criteria (per advisory §Acceptance Criteria + parent-attribute additions)

Each implementation slice's bridge will declare which acceptance criteria its tests cover. Combined acceptance for the program:

1. (advisory) New spec exists with both lifecycle dates null and is treated as active/unverified.
2. (advisory) Setting `implementation_verified_at` requires Loyal Opposition actor/evidence.
3. (advisory) A spec with `implementation_verified_at` set is treated as implemented.
4. (advisory) Setting `retired_at` requires explicit owner approval evidence.
5. (advisory) A retired spec is excluded from active/unverified and active implemented counts.
6. (advisory) Spec `priority` is absent from spec create/update/list UI/API paths and remains available only on backlog/work-item artifacts.
7. (advisory) `authority` and `provisional_until` no longer influence reconciliation, scaffolding, impact analysis, or CLI behavior.
8. (advisory) Multiple deliberation sources can be linked to one spec version.
9. (advisory) The triad audit uses `implementation_verified_at`, not string status, as the implementation-complete signal.
10. (advisory) Existing work-item status, bridge status, dashboard health status, and task priority semantics remain unchanged.
11. **(parent-attribute, owner-added)** Every spec has `parent IN ('gtkb', 'application', 'all')`; CHECK constraint enforces.
12. **(parent-attribute)** `insert_spec(parent=...)` requires the value; `update_spec` cannot change `parent`; only `set_spec_parent(spec_id, parent, changed_by, change_reason)` can change it.
13. **(parent-attribute)** `list_specs(parent=...)` filters by parent; `gt kb status --parent=...` and dashboard `--parent` filters work.
14. **(parent-attribute)** Backfill rules per §2.4 produce zero silent misclassifications: every spec is either rule-classified per §2.4 or flagged for owner review at `memory/triage-spec-parent-backfill.md`.

---

## 5. Sequencing and Concurrency

**Internal slice ordering:** Slice 1 → Slice 2 → Slice 3 → Slice 4 → Slice 5 → Slice 6. Each slice's implementation bridge waits for the previous slice to reach VERIFIED.

**External sequencing constraints:**
- Slice 4 backfill rules MAY be informed by the active-workspace-declaration architecture's eventual GO state (specifically the `gtkb` / `application` / `all` vocabulary). If active-workspace bridge is at NO-GO indefinitely, this proposal proceeds with the local vocabulary; if active-workspace lands a different vocabulary, Slice 4 reconciles. **Not a hard blocker.**
- Slice 3's audit-utility update (`scripts/audit_gtkb_triad_completeness.py`) must update fixtures in lockstep with the schema changes; coordinate with the `gtkb-platform-spec-coverage-architecture-2026-04-29` thread (currently GO at -006).

**Parallel safety:**
- Compatibility window (Phase 3.2) means Slices 1-5 can ship without breaking older code paths.
- Slice 6 (cleanup) is the only slice that's truly destructive (removes old API surface); requires all other slices VERIFIED first.

**No bridge protocol changes proposed.** This program uses the standard NEW → GO → implement → post-impl → VERIFIED flow per slice.

---

## 6. Project Root Boundary

Per `.claude/rules/project-root-boundary.md`:
- All migration artifacts under `E:\GT-KB`.
- Upstream (`groundtruth-kb/`) work routes to `E:\GT-KB\groundtruth-kb\` (in-root).
- Adopter applications consume via `gt project upgrade`; no external `groundtruth-kb` checkout is used as live dependency.
- This bridge does not introduce, propose, or rely on any path under `E:\Claude-Playground` or any home-directory mirror.

---

## 7. Files Touched (this bridge — scoping only)

**New:** none (this is a scoping/planning proposal).

**Modified:** `memory/work_list.md` — on GO, add a row (likely row 21) for `GTKB-SPEC-LIFECYCLE-SCHEMA-MIGRATION` citing this bridge ID and the proposed slice thread names listed in §2.

**Not touched:** `groundtruth-kb/src/**`, `scripts/**`, `tests/**`, `docs/**`, `groundtruth-kb/templates/**` — all implementation defers to per-slice bridges.

---

## 8. Verification Matrix (this scoping bridge)

| Risk | Verification at scoping VERIFIED |
|------|-----------------------------------|
| Slice ordering creates an unbuildable dependency chain | Codex review walks the §2/§5 slice gates and confirms each gate's prereq is achievable from prior-slice outputs alone. |
| Backfill rules silently misclassify production specs | §2.4 explicitly defaults to "flag for owner review" rather than auto-classify when rules are ambiguous. Codex review confirms no rule covers spec ids that would conflict (e.g., `GOV-*` specs marked `parent='all'` is correct because they're cross-workspace). |
| `parent` vocabulary diverges from active-workspace bridge's eventual settlement | §5 explicitly notes the vocabulary alignment is desirable but not blocking; Slice 4 reconciliation pathway exists if vocabularies later differ. |
| Compat window is too short / cleanup happens before all paths migrated | §2.6 requires all other slices VERIFIED first before Slice 6 starts. Codex review confirms gate. |
| Old column removal at Slice 6 breaks audit trail | §3.3 specifies append-only schema means version-history rows preserve old-column values; only the active write API drops them. |
| `parent` attribute applied beyond specs (scope creep) | §1 + §10 explicitly limit `parent` to specs only; advisory §Risks similarly warned about `status`-word scope creep beyond specs. |
| Schema migration without deprecation window breaks existing tests | §2 (Slice 2) keeps old API paths working with deprecation warnings; tests for both old and new paths during compat window per §3.2. |

---

## 9. Out of Scope

- Changes to work-item `status`, bridge `status`, dashboard health `status`, HTTP health `status`, runtime `status`, or any non-spec `status` semantics. Per advisory §Risks, the `status` word is heavily used outside specs; this migration is spec-only.
- Adding `parent` attribute to work items, bridge files, tests, or any non-spec artifact. Spec-only per §10.
- Changes to bridge protocol itself (NEW → GO → REVISED → VERIFIED stays).
- Changes to the work-item `priority` semantics (preserved as-is per advisory §Required Prime changes).
- Retroactive owner approval for `retired` specs lacking deliberation evidence (Slice 4 flags for owner review; actual approval is a separate owner action).
- Implementation of any §2 slice (those are six separate bridges on GO).
- Active-workspace-declaration architecture integration beyond vocabulary alignment (separate bridge thread).
- Multi-language support (English-only, consistent with prior umbrella scoping).

---

## 10. `parent` Attribute Detailed Design (per owner addition)

**Vocabulary:** `parent IN ('gtkb', 'application', 'all')`. Three values exhaustive of the workspace model.

**Semantics:**
- `gtkb`: spec applies to the GT-KB platform implementation/governance. Examples: `GTKB-DORA-001b`, `GOV-FILE-BRIDGE-AUTHORITY-001`, `SPEC-PROJECT-DASHBOARD-KPI-LINK-001`.
- `application`: spec applies to the application under development (currently Agent Red Customer Experience). Examples: `AR-DASH-001`, customer-flow specs, Shopify-integration specs.
- `all`: spec applies to both. Examples: `SPEC-INTAKE-c9e997` (intake mechanics work in both workspaces), `GOV-ARTIFACT-APPROVAL-001` (formal-artifact governance applies to both), `ADR-WORKSPACE-DECLARATION-OVER-DETECTION-001` (architecture decisions span both).

**Schema:**
```sql
parent TEXT NOT NULL CHECK (parent IN ('gtkb', 'application', 'all'))
```

**API contract:**
- `insert_spec(id, ..., parent)` — required parameter, no default. Insertion fails if missing.
- `update_spec(...)` — does NOT accept `parent` parameter. Cannot be silently changed.
- `set_spec_parent(spec_id, parent, changed_by, change_reason)` — explicit operation; creates a new spec version with the new parent value (per append-only schema).
- `list_specs(parent=None)` — optional filter; `None` returns all parents.

**Backfill heuristics (one-time, Slice 4):**
- See §2.4 for the full ruleset.
- Ambiguous specs flagged at `memory/triage-spec-parent-backfill.md` (a NEW operational file; not formal canonical state).

**Active-workspace alignment:** the `parent` vocabulary maps to the active-workspace-declaration architecture's workspace-state vocabulary. If the active-workspace bridge eventually GO's with a different vocabulary, Slice 4 reconciles via a one-time vocabulary mapping migration. Both vocabularies remaining `gtkb` / `application` is the simplest and recommended path.

**Why this aligns with owner's "default GT-KB" workspace directive:** the `parent` attribute makes spec-level workspace attribution explicit. When workspace inference is suppressed (per active-workspace bridge), `parent` is the spec-level declaration that prevents "is this an Agent Red spec or a GT-KB spec?" ambiguity. They're complementary mechanisms.

---

## 11. Open Questions for Loyal Opposition Review

1. **`parent` value for legacy specs without clear classification.** §2.4 backfill rules cover most cases, but ~365 specs with non-null `priority` (per advisory §Live Data Impact) plus older specs may not match any rule. Default to "flag for owner review" or default to a most-restrictive value like `parent='all'`?

2. **`set_spec_parent` operation as separate API vs `update_spec` extension.** §10 proposes a separate op because parent change is significant. Codex may prefer either path; what's the preferred change-rationale-required pattern in the existing codebase?

3. **Deprecation warning channel.** Phase 3.2 emits deprecation warnings on old API paths. Where: Python warnings, log lines, dashboard banner, all? Tests need to assert warnings without breaking on warning-as-error config.

4. **Backfill triage file format.** §2.4 + §3.1 reference `memory/triage-spec-parent-backfill.md` and similar files. Should these be markdown, JSON, or KB rows in a new `triage_*` table?

5. **Migration script invocation surface.** Run via `gt schema migrate spec-lifecycle` CLI? Standalone script under `scripts/migrations/`? Both? CLI offers discoverability; script offers reproducibility.

6. **`parent='all'` semantics.** Does an `all` spec count once in metrics, or once per workspace it applies to? §4 acceptance criterion #13 needs to be unambiguous about this.

7. **Slice 6 (removal) timing.** Old columns can stay forever as a "compat layer" or be removed after a fixed deprecation window. Codex preference?

---

## 12. Decision Needed From Owner

Two decisions, neither blocking for this scoping bridge but blocking for the first implementation bridge (Slice 1):

1. **`parent` vocabulary lock-in.** This proposal uses `gtkb` / `application` / `all`. Owner confirmation that this matches the active-workspace-declaration architecture's intended vocabulary (currently NO-GO with substantive findings). If the eventual settled vocabulary uses different values, Slice 4 reconciles via vocabulary migration — but locking in now prevents that overhead.

2. **Compat window length.** Slices 1-5 keep old columns operational with deprecation warnings. Owner preference: explicit removal date for Slice 6, or "remove when all callers migrated"?

All other design choices surface in per-slice implementation bridges, not here.

---

## 13. Aligns With

- Codex advisory `SPEC-LIFECYCLE-SCHEMA-ADVISORY-2026-04-29-15-50.md` (substance source).
- Owner addition 2026-04-29: `parent` attribute requirement.
- DELIB-0874 artifact-oriented governance (date-bearing facts ARE artifacts).
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE (dedicated APIs per state transition).
- GOV-AGENT-RED-GTKB-CONFORMANCE-001 (`parent` makes workspace attribution explicit at artifact level).
- `bridge/active-workspace-declaration-architecture-2026-04-29-001` (aligned in spirit; not blocked on its GO).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
