NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-2026-05-29-orphan-wi-backfill-slice-2-implementation-POST-IMPL
author_model: claude-opus-4-7
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder

Project Authorization: PAUTH-WI-3450-ORPHAN-BACKFILL-DRIVER-001
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3450

# Orphan-WI Membership Backfill Slice 2 — Post-Implementation Report (WI-3450)

bridge_kind: implementation_report

Document: gtkb-orphan-wi-membership-backfill-slice-2-implementation
Version: 005 (post-implementation report; responds to Codex GO at -004)
Date: 2026-05-29 UTC
Recommended commit type: feat

## Summary

Implemented the orphan-WI membership resolution driver per the GO'd REVISED-1 proposal at `-003`, authorized by Codex GO at `-004`. Two new files landed within the GO's authorized scope: `scripts/resolve_orphan_wi_memberships.py` (driver) and `platform_tests/scripts/test_resolve_orphan_wi_memberships.py` (10-test spec-derived suite). All 10 tests PASS. A read-only dry-run of the driver against the canonical store produced the expected plan (34 orphans, all `owner_decision`); canonical MemBase is unchanged.

The follow-on Slice 2b work item that owns the per-WI retire/exclude service was filed during implementation as **WI-3464** (under `PROJECT-GTKB-RELIABILITY-FIXES`); the proposal's "follow-on slice" reference is no longer a forward promise — it has a tracked work item.

## Owner Decisions / Input

Carried forward from `-003`:

1. **DELIB-2509** — Owner AUQ Answer: Per-WI PAUTH + Assign-Only Scope for WI-3450 Orphan Backfill Driver (2026-05-29). Authorizes `PAUTH-WI-3450-ORPHAN-BACKFILL-DRIVER-001`, the assign-only scope narrowing, and the deferral of per-WI retire/exclude to a follow-on slice. `outcome='owner_decision'`. Packet: `.groundtruth/formal-artifact-approvals/2026-05-29-DELIB-2509.json` (verified owner-approved by Codex at `-004`).
2. **PAUTH-WI-3450-ORPHAN-BACKFILL-DRIVER-001** — active per-WI authorization; classes `["source", "test_addition"]`; cites DELIB-2509. Covers the work performed by this implementation exactly.
3. **Implement-Gap-6 selection** (AskUserQuestion, this session) — owner authorization that this conversation files and implements the orphan-wi-membership-backfill Slice 2 thread.
4. **Scoping-approach selection** (AskUserQuestion, S364 2026-05-29, carried forward).

No new owner decision was required by this implementation phase.

## Specification Links

Carried forward from `-003` (Codex GO at `-004` validated this set):

- `SPEC-AUQ-POLICY-ENGINE-001` — `apply_resolution` is fail-closed; no orphan is mutated without an explicit owner-decision entry.
- `GOV-STANDING-BACKLOG-001` — assignment-only resolution; the bulk-ops clause clarification is realized by per-orphan owner-decision evidence at runtime (deferred to a separate execution session).
- `GOV-RELIABILITY-FAST-LANE-001` — explicitly cited; explains why `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (fast-lane PAUTH) is NOT the authorization for this feature-scope work. WI-3450 is `origin='new'` and the driver introduces a new CLI surface, both failing fast-lane eligibility. The authorization is `PAUTH-WI-3450-ORPHAN-BACKFILL-DRIVER-001`.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — assignment routes through `ProjectLifecycleService.add_project_item`; retire/exclude produce deferred-action records, not lifecycle transitions in this slice.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched paths under `E:\GT-KB`; no application-directory placement.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — header Project Authorization / Project / Work Item triple is live and verified.
- `GOV-ARTIFACT-APPROVAL-001` — DELIB-2509 insert was via the governed `gt deliberations record` path; packet auto-generated and Codex-verified at `-004`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this Specification Links section is the satisfaction.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — § Spec-Derived Verification Execution Evidence below maps each behavior to an actually-executed test with observed result.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` is canonical; this post-impl entry is inserted at the top of the document's version list.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable driver source + tests + DA-archived owner decisions.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — operative authority; the driver is the deterministic service; no ad-hoc `db.insert_*`; assignment routes through `add_project_item` only.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — referenced as the source of the standing PAUTH that this work was *not* authorized under.
- `DELIB-2509` — owner AUQ authorizing the PAUTH and scope narrowing.

## Spec-Derived Verification Execution Evidence

All 10 spec-derived tests from the GO'd proposal's matrix executed; all PASS.

**Pytest execution:**

```text
$ python -m pytest platform_tests/scripts/test_resolve_orphan_wi_memberships.py -q
platform_tests\scripts\test_resolve_orphan_wi_memberships.py ..........  [100%]
============================= 10 passed in 3.49s ==============================
```

**Spec-to-test execution mapping (all PASS):**

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

## Dry-Run Evidence Over Canonical (read-only; no `--apply`)

Per Codex's Implementation Constraint "do not run live canonical `--apply` over the current orphan set under this GO," this evidence is dry-run only. Per Codex's non-blocking note, output is stdout-only — no durable `.gtkb-state` write.

```text
$ python scripts/resolve_orphan_wi_memberships.py --run-id postimpl-evidence-2026-05-29 --json
apply: False
run_id: postimpl-evidence-2026-05-29
orphan_count: 34
high_confidence_threshold: 0.8
planned_action_counts: {'already_member_noop': 0, 'assign_candidate': 0, 'owner_decision': 34, 'owner_pick': 0}
first 3 entries:
     WI-3269 | unrecoverable                       | owner_decision
     WI-3326 | unrecoverable                       | owner_decision
     WI-3327 | unrecoverable                       | owner_decision
(total 34 entries)
```

**Live state cross-check (canonical untouched by the dry-run):**

| Metric | Value |
|---|---:|
| `current_projects` row count | 158 |
| Active memberships (`status='active'`) | 462 |
| Orphan count from driver | 34 |
| Plan classifies as `owner_decision` | 34 (100%) |
| Plan classifies as `assign_candidate` | 0 |
| Plan classifies as `owner_pick` | 0 |

The 34-orphan count drifted from 30 at proposal authoring (-001) and 27 at the scoping GO (-002 of the predecessor thread), confirming the structural importance of the driver's "re-run discovery first" property that test #8 asserts.

The full live orphan set being `owner_decision` means an immediate `--apply` (with no decisions artifact) would skip all 34 — the fail-closed contract at work. The deferred canonical-execution session would resolve each orphan via per-orphan AskUserQuestion before any mutation.

## Files Changed

| Path | Change | Lines (approx) |
|---|---|---:|
| `scripts/resolve_orphan_wi_memberships.py` | new module | +311 |
| `platform_tests/scripts/test_resolve_orphan_wi_memberships.py` | new spec-derived test file (10 tests) | +361 |

`groundtruth.db` is NOT touched; no `cli.py` edit; no `.gtkb-state` durable write. Implementation matches the GO's authorized target_paths exactly.

## target_paths

Carried forward from `-003` (Codex GO at `-004` authorized this exact set):

- `scripts/resolve_orphan_wi_memberships.py` (landed)
- `platform_tests/scripts/test_resolve_orphan_wi_memberships.py` (landed)

No path mutations outside this set occurred.

## Follow-On Slice WI Filed During Implementation

Per the proposal's "Out of Scope This Slice" section, the per-WI retire service is deferred to a follow-on slice. That slice now has a tracked work item:

- **WI-3464** — "Orphan-WI backfill Slice 2b: per-WI retire/exclude service (deterministic per-WI lifecycle surface)". Filed under `PROJECT-GTKB-RELIABILITY-FIXES`, origin `new`, priority `P2`. References DELIB-2509 as the deferral source. Description enumerates the five deliverables: (1) `retire_project_work_item()` in `groundtruth_kb.project.lifecycle`; (2) `gt projects retire-item` CLI; (3) data-migration PAUTH; (4) consumer for Slice 2's `deferred_actions.json` artifact; (5) spec-derived tests.

This is a Strategic-Self-Improvement-directive capture (per CLAUDE.md), not implementation approval — Slice 2b will require its own bridge proposal and Codex GO before any code is written.

## Recommended Commit Type

`feat:` — net-new deterministic resolution driver (`scripts/resolve_orphan_wi_memberships.py`) + 10-test spec-derived regression suite. Codex `-004` independently recommended the same type.

`groundtruth.db` is `.gitignore`-excluded and was not mutated by this implementation regardless.

## Bulk-Operation Scope Clarification (Post-Execution Update)

The GOV-STANDING-BACKLOG-001 / CLAUSE-VISIBILITY-BULK-OPS clause's visibility requirement is satisfied by:

- the GO'd proposal's scope statement (assignment-only; retire/exclude deferred);
- this report's tested behavior (all 10 spec-derived tests PASS, including T6 proving retire/exclude writes a deferred-actions record rather than mutating canonical);
- the dry-run evidence (34 orphans, all `owner_decision`, would all be skipped fail-closed without owner-decision entries);
- the fail-closed contract at the code level (`apply_resolution` is the only canonical-mutation entry, and every branch is fail-closed by default).

No blind bulk write occurred or could occur under this implementation.

## Codex Verification Asks

1. Confirm the 10/10 PASS pytest result satisfies the spec-derived verification gate for all 10 GO'd test behaviors.
2. Confirm the read-only dry-run evidence (no `groundtruth.db` mutation; canonical row counts unchanged) honors the GO's "do not run live canonical `--apply`" constraint.
3. Confirm the implementation stayed within the GO'd target_paths (`scripts/resolve_orphan_wi_memberships.py` + `platform_tests/scripts/test_resolve_orphan_wi_memberships.py`); no `cli.py` edit; no public per-WI retire service introduced.
4. Confirm `apply_resolution`'s assignment-only canonical-mutation policy (retire/exclude → deferred records only) honors the GO's Implementation Constraints.
5. Confirm the WI-3464 follow-on filing is appropriate handling of the deferred Slice 2b scope (or flag if a different lifecycle is preferred).

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
