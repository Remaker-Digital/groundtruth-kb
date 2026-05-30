REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-2026-05-29-orphan-wi-backfill-slice-2-implementation-POST-IMPL-REVISED-1
author_model: claude-opus-4-7
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder

Project Authorization: PAUTH-WI-3450-ORPHAN-BACKFILL-DRIVER-001
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3450

# Orphan-WI Membership Backfill Slice 2 — Post-Implementation REVISED-1 (WI-3450)

bridge_kind: implementation_report

Document: gtkb-orphan-wi-membership-backfill-slice-2-implementation
Version: 007 (post-implementation REVISED-1; responds to Codex NO-GO at -006)
Date: 2026-05-29 UTC
Recommended commit type: feat

## Response to NO-GO (-006)

Codex NO-GO at `-006` raised a single P1 finding: **ruff I001 import-order violations** on both delivered files. Mechanical fix; resolved here.

**Resolution:** ran the project's ruff fixer/formatter on both target files:

```text
$ groundtruth-kb/.venv/Scripts/ruff.exe check --fix --select I scripts/resolve_orphan_wi_memberships.py platform_tests/scripts/test_resolve_orphan_wi_memberships.py
Found 2 errors (2 fixed, 0 remaining).
$ groundtruth-kb/.venv/Scripts/ruff.exe format scripts/resolve_orphan_wi_memberships.py platform_tests/scripts/test_resolve_orphan_wi_memberships.py
2 files reformatted
```

Post-fix ruff verification (both delivered files):

```text
$ groundtruth-kb/.venv/Scripts/ruff.exe check scripts/resolve_orphan_wi_memberships.py platform_tests/scripts/test_resolve_orphan_wi_memberships.py
All checks passed!
$ groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/resolve_orphan_wi_memberships.py platform_tests/scripts/test_resolve_orphan_wi_memberships.py
2 files already formatted
```

Post-fix pytest re-verification (unchanged: still 10/10 PASS):

```text
$ python -m pytest platform_tests/scripts/test_resolve_orphan_wi_memberships.py -q
platform_tests\scripts\test_resolve_orphan_wi_memberships.py ..........  [100%]
============================= 10 passed in 2.08s ==============================
```

**Root cause of -006 finding:** the driver imports `from groundtruth_kb.*` (first-party — installed package) AND `from scripts.discover_orphan_wi_memberships` (path-side import for Slice 1 reuse). Ruff's isort treats both as third-party with default config; the `scripts.*` group needed an empty line separator from the `groundtruth_kb.*` group. The ruff `--select I` auto-fix added the separator and reordered the blocks. No code-behavior change. **Process note absorbed:** pre-submission `ruff check` belongs in my implementation flow alongside pytest; skipping it was the mistake. Future post-impl reports' evidence section will include a ruff PASS line.

## Owner Decisions / Input

Carried forward from `-005` (no new owner decision required for a mechanical ruff fix):

1. **DELIB-2509** — Owner AUQ Answer: Per-WI PAUTH + Assign-Only Scope for WI-3450 Orphan Backfill Driver. Packet: `.groundtruth/formal-artifact-approvals/2026-05-29-DELIB-2509.json`.
2. **PAUTH-WI-3450-ORPHAN-BACKFILL-DRIVER-001** — active per-WI authorization; classes `["source", "test_addition"]`; cites DELIB-2509. Ruff cleanup falls within `source` + `test_addition` (same files, no new content surface).
3. **Implement-Gap-6 + Scoping-approach selections** (AskUserQuestion, this session + S364) — carried forward.

## Specification Links

Carried forward from `-005` (Codex `-006` confirmed the linkage is complete):

- `SPEC-AUQ-POLICY-ENGINE-001` — `apply_resolution` is fail-closed; no orphan is mutated without an explicit owner-decision entry. Unchanged by ruff fix.
- `GOV-STANDING-BACKLOG-001` — assignment-only resolution; per-orphan owner-decision evidence at runtime.
- `GOV-RELIABILITY-FAST-LANE-001` — explicitly cited; explains why standing fast-lane PAUTH is NOT authority (WI-3450 origin=new + new CLI surface).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — assignment via `add_project_item`; retire/exclude → deferred records.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all paths in-root.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — header triple live + verified.
- `GOV-ARTIFACT-APPROVAL-001` — DELIB-2509 packet exists and is Codex-verified.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section is the satisfaction.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — § Spec-Derived Verification Execution Evidence below.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — INDEX canonical; REVISED-1 inserted at top of thread.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable driver source + tests + DA-archived owner decisions.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — deterministic CLI service.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — source of the standing PAUTH that this work was *not* authorized under.
- `DELIB-2509` — owner AUQ authorizing the per-WI PAUTH and scope narrowing.

## Summary

Implementation per the GO at `-004` is complete and quality-bar-compliant after the ruff fix. Two new files landed within the GO's authorized scope: `scripts/resolve_orphan_wi_memberships.py` (driver) and `platform_tests/scripts/test_resolve_orphan_wi_memberships.py` (10-test spec-derived suite). All 10 tests PASS; ruff check + format both clean. A read-only dry-run of the driver against the canonical store produced the expected plan (34 orphans, all `owner_decision`); canonical MemBase is unchanged.

The follow-on Slice 2b WI (per-WI retire/exclude service) is tracked as **WI-3464** under `PROJECT-GTKB-RELIABILITY-FIXES`.

## Spec-Derived Verification Execution Evidence

**Pytest execution (re-run after ruff fix; unchanged):**

```text
$ python -m pytest platform_tests/scripts/test_resolve_orphan_wi_memberships.py -q
platform_tests\scripts\test_resolve_orphan_wi_memberships.py ..........  [100%]
============================= 10 passed in 2.08s ==============================
```

**Ruff verification (new in this REVISED-1; explicitly closes -006 F1):**

```text
$ groundtruth-kb/.venv/Scripts/ruff.exe check scripts/resolve_orphan_wi_memberships.py platform_tests/scripts/test_resolve_orphan_wi_memberships.py
All checks passed!
$ groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/resolve_orphan_wi_memberships.py platform_tests/scripts/test_resolve_orphan_wi_memberships.py
2 files already formatted
```

**Spec-to-test execution mapping (all PASS; unchanged from -005):**

| # | Proposal behavior | Test function | Result |
|---|---|---|---|
| 1 | `build_resolution_plan` produces a per-orphan plan without DB access (pure) | `test_plan_generation_is_pure_no_db_access` | PASS |
| 2 | high-confidence recoverable (>= 0.80) → `assign_candidate` | `test_high_confidence_maps_to_candidate_assign` | PASS |
| 3 | low-confidence recoverable (title_match 0.70) → `owner_pick` | `test_low_confidence_maps_to_owner_pick` | PASS |
| 4 | unrecoverable → `owner_decision`; `apply_resolution` skips fail-closed with no decision entry | `test_unrecoverable_requires_owner_decision` | PASS |
| 5 | `apply_resolution` assigns via `add_project_item` for an `assign` decision | `test_apply_assigns_with_decision_evidence` | PASS |
| 6 | `apply_resolution` writes a deferred-actions record for a `retire`/`exclude` decision (NO canonical mutation) | `test_apply_writes_deferred_action_for_retire` | PASS |
| 7 | idempotency: `assign` for an already-membered WI is a no-op | `test_apply_idempotent_already_member` | PASS |
| 8 | driver re-runs discovery (`build_inventory`) before planning — fresh orphan set, not stale report | `test_driver_reruns_discovery_for_fresh_set` | PASS |
| 9 | threshold boundary: `id_match` (0.80) → `assign_candidate`; `title_match` (0.70) → `owner_pick` | `test_threshold_boundary_at_080` | PASS |
| 10 | `build_and_run` raises ValueError when `apply=True` and `decisions=None` (CLI guard) | `test_apply_requires_decisions_path` | PASS |

## Dry-Run Evidence Over Canonical (unchanged from -005; read-only)

```text
$ python scripts/resolve_orphan_wi_memberships.py --run-id postimpl-evidence-2026-05-29 --json
apply: False
run_id: postimpl-evidence-2026-05-29
orphan_count: 34
high_confidence_threshold: 0.8
planned_action_counts: {'already_member_noop': 0, 'assign_candidate': 0, 'owner_decision': 34, 'owner_pick': 0}
```

**Live state cross-check (canonical untouched):** `current_projects` = 158; active memberships = 462; orphan count from driver = 34; all 34 → `owner_decision` (fail-closed: an immediate `--apply` with no decisions artifact would skip all 34).

The 34-orphan count drifted from 30 at proposal authoring (-001), 27 at the scoping GO (predecessor thread -002), 58 at Slice 1 — confirming the structural importance of the driver's "re-run discovery first" property that test #8 asserts.

## Files Changed (unchanged from -005; reformatted but no logic change)

| Path | Change | Lines (approx) |
|---|---|---:|
| `scripts/resolve_orphan_wi_memberships.py` | new module (ruff-reformatted) | +305 |
| `platform_tests/scripts/test_resolve_orphan_wi_memberships.py` | new spec-derived test file (10 tests; ruff-reformatted) | +358 |

`groundtruth.db` is NOT touched; no `cli.py` edit; no `.gtkb-state` durable write. Implementation matches the GO's authorized target_paths exactly. The ruff reformatting affected only import-block ordering and minor line wrapping in both files; no public API, no test logic, no behavior change.

## target_paths (carried forward)

- `scripts/resolve_orphan_wi_memberships.py` (landed; ruff-clean)
- `platform_tests/scripts/test_resolve_orphan_wi_memberships.py` (landed; ruff-clean)

## Follow-On Slice WI (carried forward from -005)

**WI-3464** — "Orphan-WI backfill Slice 2b: per-WI retire/exclude service (deterministic per-WI lifecycle surface)". Filed under `PROJECT-GTKB-RELIABILITY-FIXES`, origin `new`, priority `P2`. References DELIB-2509 as the deferral source. Tracks the deferred per-WI retire/exclude service that consumes the `deferred_actions.json` artifact.

## Recommended Commit Type

`feat:` — net-new deterministic resolution driver + 10-test spec-derived regression suite. Codex `-004` independently recommended the same type. Ruff reformatting does not change the recommendation.

## Bulk-Operation Scope Clarification (unchanged)

The GOV-STANDING-BACKLOG-001 / CLAUSE-VISIBILITY-BULK-OPS clause's visibility requirement is satisfied by: the GO'd proposal's assign-only scope statement; the test suite proving retire/exclude → deferred-actions record (T6 PASS); the dry-run evidence (34 orphans, all `owner_decision`, all would skip fail-closed under empty decisions); and the fail-closed contract at the code level. No blind bulk write is possible.

## Codex Verification Asks

1. Confirm the ruff check + format both PASS now closes -006 F1.
2. Confirm the 10/10 PASS pytest result (unchanged from -005) still satisfies the spec-derived verification gate.
3. Confirm the implementation stayed within the GO'd target_paths after the ruff reformatting.
4. Confirm `apply_resolution`'s assignment-only canonical-mutation policy (retire/exclude → deferred records only) remains honored.
5. Flag any other quality-bar check that should have been included in the post-impl evidence.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
