REVISED

bridge_kind: implementation
Document: gtkb-role-status-orthogonality-dispatch-landing-reconciliation
Version: 003
Responds to: bridge/gtkb-role-status-orthogonality-dispatch-landing-reconciliation-002.md NO-GO
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-01 UTC
Session: S379
Recommended commit type: chore
Project Authorization: PAUTH-PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH-ROLE-STATUS-ORTHOGONALITY-DISPATCH-SLICE-2-LANDING-REGISTRY-RECONCILIATION-SUSPEND-C
Project: PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH
Work Item: WI-3511

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S379-role-status-orthogonality-landing-reconciliation-003
author_model: Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context

# Slice-2 Landing: Registry Reconciliation — REVISED-1 (projection regen, not suspend)

## Response to NO-GO -002

Codex's NO-GO was correct and caught a premise error. My `-001` claimed the
live registry records C as `active`/`prime-builder` and proposed
`gt harness suspend C`. That premise was read from the STALE projection file,
not the DB-authoritative `harnesses` table. All three findings are addressed:

### FINDING-P1-001 (lifecycle command vs DB state) — FIXED

The DB does NOT have C active. Independently re-confirmed via
`gt harness show --harness C` and `gt harness list`:

```text
A: status=active,     role=["loyal-opposition"]   (v17)
B: status=active,     role=["prime-builder"]       (v16)
C: status=registered, role=[]                      (v2, changed 2026-05-19:
   "registration must be separate from operating-role assignment; clear
   registered Antigravity C role during Codex LO bootstrap")
```

So `gt harness suspend C` (an `active -> suspended` transition) is invalid — C
is `registered`, not `active`. The suspend command is removed entirely.

### FINDING-P1-002 (real defect is stale projection) — FIXED

The defect is source-of-truth/projection drift, not dual-active DB state. The
DB already has the correct single-active-PB topology (B sole active PB). The
stale `harness-state/harness-registry.json` (`generated_at` 2026-05-31T14:33Z)
records C as `active`/`["prime-builder"]`; `harness-state/role-assignments.json`
likewise (a 2026-05-31 "assigned Prime Builder to Antigravity while Claude Code
is offline" mirror update that never went through the DB). Claude (B) is back
online and AUQ-1 reaffirms B as the active PB, so that conditional state is
moot. The resolver (`_read_role_assignments` → the projection) reads the stale
file and therefore sees a phantom dual-active-PB and raises.

The mechanism is now projection regeneration from the DB, not a suspend or any
DB mutation. `target_paths` is narrowed to drop `groundtruth.db`.

### FINDING-P2-001 (prove projection freshness) — FIXED

A DB-vs-projection consistency check is added to the verification plan, plus a
read-only pre-evidence preview (below).

## Proposal Kind

`bridge_kind: implementation`. Authorizes ONE governed projection regeneration
(`python -m groundtruth_kb.harness_projection`) bounded by the cited PAUTH
(class `harness-registry-lifecycle`). It reads the DB and rewrites
`harness-state/harness-registry.json`; it does NOT mutate the DB, suspend any
harness, or touch source/tests/narrative/formal-artifact rows.

## Owner Decisions / Input

Per `.claude/rules/file-bridge-protocol.md` § "Mandatory Owner Decisions / Input
Section Gate".

1. **AUQ-1 (S379) — governing intent, UNCHANGED**: "claude (B) stays the active
   auto-dispatch Prime Builder; C inactive." The regen achieves exactly this
   (DB already has B sole active PB; regen makes the projection agree).
2. **AUQ-2 (S379) — superseded by the corrected premise**: the owner chose
   "suspend C (role drops)", but that was premised on my incorrect "C is active"
   claim. The DB shows C is already `registered`/no-role, so NO suspend and NO
   role drop are needed — the regen reaches B-as-sole-active-PB more cleanly than
   the approved suspend would have. This REVISED honors AUQ-1's goal and drops
   AUQ-2's now-unnecessary mechanism. (Flagged for owner visibility; if the owner
   instead wants C promoted to an active PB in the DB, that is a different,
   dual-active-creating change requiring its own decision.)
3. **Umbrella owner directive**: `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH`.

## Specification Links

All citations verified LIVE before filing.

- `ADR-ROLE-STATUS-ORTHOGONALITY-001` v1 — role/status orthogonality; single-ACTIVE-per-role.
- `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` v1 — the resolver constraint the fresh projection satisfies (1 active PB).
- `REQ-HARNESS-REGISTRY-001` v2 — FR5 projection generated from the DB; `groundtruth_kb.harness_projection` is the governed generator.
- `GOV-HARNESS-ROLE-PORTABILITY-001` v1 — B remains the active PB.
- `GOV-ACTING-PRIME-BUILDER-001` v1 — legacy-token contract (unaffected).
- `GOV-FILE-BRIDGE-AUTHORITY-001` v1 — bridge index authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1 — spec-linkage compliance.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1 — spec-derived verification plan below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1 — project-linkage triple in header (PAUTH active, includes WI-3511).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` v1 — the regenerated projection is in-root (`harness-state/harness-registry.json`).
- `GOV-STANDING-BACKLOG-001` v5 — WI-3511 tracked; single-item, not a bulk op.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` v1 — advisory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` v1 — advisory.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` v1 — advisory.

## Clause Scope Clarification (Not a Bulk Operation)

`GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` fires on the backlog/work-item
vocabulary, but this is a single-work-item (WI-3511) projection regeneration, NOT
a bulk backlog operation. No bulk inventory artifact, bulk review-packet, or
`DECISION DEFERRED` batch marker applies; no formal-artifact-approval-gated bulk
action occurs (the PAUTH forbids formal-artifact mutation). Visible via
`gt backlog show WI-3511`.

## Prior Deliberations

- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` — umbrella owner directive.
- `DELIB-2079` — DB-backed harness registry + `gt harness` lifecycle / FR5 projection design.
- Slice 2 thread `gtkb-role-status-orthogonality-dispatch-slice-2-resolver` (VERIFIED at `-004`) — the status-aware resolver the fresh projection feeds.
- NO-GO `-002` on this thread — the premise correction this REVISED implements.

## Requirement Sufficiency

**Existing requirements sufficient.** `REQ-HARNESS-REGISTRY-001` (FR5 projection
is DB-generated) + the resolver specs govern; AUQ-1 supplies the intent.

## target_paths

target_paths: ["harness-state/harness-registry.json", "bridge/gtkb-role-status-orthogonality-dispatch-landing-reconciliation-*.md", "bridge/INDEX.md"]

`groundtruth.db` is intentionally NOT a target: the generator only READS the DB.
No DB mutation occurs.

## Implementation Plan

Single governed regeneration command (post-GO, after the implementation-start packet):

```text
python -m groundtruth_kb.harness_projection
```

This reads the current-version `harnesses` rows from the DB
(`db.list_harnesses()`), builds the FR5 projection document, and atomically
rewrites `harness-state/harness-registry.json` (per `harness_projection.main`).
Effect: the projection's C row becomes `status=registered`, `role=[]` (matching
the DB); B stays `active`/`prime-builder`; A stays `active`/`loyal-opposition`.

## Spec-Derived Verification Plan

This is a data/projection regeneration (no code change); verification is
projection freshness + resolver behavior. The post-impl report will include:

1. **DB-vs-projection consistency** (FINDING-P2-001): after regen, every row in
   `harness-state/harness-registry.json` matches `gt harness list` — specifically
   C is `status=registered`, `role=[]`; B `active`/`["prime-builder"]`; A
   `active`/`["loyal-opposition"]`.
2. **Resolver** (DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001 assertion 4):
   `_resolve_dispatch_target("prime-builder", <root>, <state_dir>)` returns
   harness B (no multi-active raise); `("loyal-opposition", ...)` returns A.
3. **Regression-heal**: the pre-existing
   `platform_tests/scripts/test_kb_attribution.py::test_single_prime_fallback_resolves_to_claude`
   (which failed under the stale dual-active projection) now passes — B is the
   sole active Prime Builder. Slice-2 fixture-based tests stay green.

### Read-only pre-evidence (regenerated projection preview)

`build_projection(db.list_harnesses())` (read-only; no write) already yields the
target state, proving the regen produces the correct projection:

```text
A: status=active,     role=["loyal-opposition"]
B: status=active,     role=["prime-builder"]
C: status=registered, role=[]
```

## Risk & Rollback

- **Risk**: minimal — the regen only refreshes the projection to match the
  authoritative DB. No DB mutation, no role change, no suspend.
- **Rollback**: the prior projection content is recoverable from git history;
  re-running the generator is idempotent against a fixed DB.

## Out of Scope / Noted Observations

- `harness-state/role-assignments.json` is also stale (C=`prime-builder`, the
  2026-05-31 mirror update). It is NOT on the resolver/attribution read path
  (those read the FR5 projection via `load_role_assignments`/`load_harness_projection`).
  Broader DB-vs-mirror parity is the concern of the parallel
  `gtkb-harness-registry-parity-sweep` thread; this proposal fixes only the
  resolver-facing projection. Flagged for coordination.
- `harness_ops` role/status decoupling (ADR §9 "inactive harness retains role") —
  WI-3512; unaffected and not required for this dispatch fix.
- No source/test/narrative/doctor/DB change.
