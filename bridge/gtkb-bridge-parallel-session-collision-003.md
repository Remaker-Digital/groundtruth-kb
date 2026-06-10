REVISED

# Implementation Proposal - Bridge Work-Intent Registry Foundation Module (WI-3274)

bridge_kind: prime_proposal
Document: gtkb-bridge-parallel-session-collision
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS-BRIDGE-TOOLING-ENHANCEMENTS-PARALLEL-BATCH
Project: PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS
Work Item: WI-3274

target_paths: ["scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_bridge_work_intent_registry.py", ".gtkb-state/work-intent/.gitkeep"]

This REVISED proposal (`-003`) addresses the `-002` NO-GO on WI-3274. It scopes the work as a **foundation-only work-intent registry module**: a tested, file-locked registry primitive with acquire-then-refresh live-state revalidation, with NO bridge-writer / AXIS-2 / startup-visibility integration in this thread. Integration is deferred to an explicit follow-up work item (see `## Follow-Up Work Item` below).

## Revision Notes

The `-002` NO-GO raised four findings. All four are addressed in `-003`:

- **F1 (P1) - proposed scope did not implement the claimed collision protection.** Addressed by choosing NO-GO recommended-action option (a): this proposal is re-scoped and re-titled as a **foundation-only module**. The "prevents concurrent Prime Builder sessions from writing the same bridge thread version" claim and the corresponding acceptance criteria are REMOVED. The module is an unintegrated primitive; no bridge writer is required to call it in this thread. The `## Follow-Up Work Item` section names an explicit successor work item for the bridge-writer / AXIS-2 / startup-visibility integration that WI-3274's description recommends. The honest acceptance claim for `-003` is: "a correct, tested work-intent registry primitive that a future integration WI can wire into bridge writers."
- **F2 (P1) - lock API did not specify an under-lock version revalidation step.** Addressed. The module now exposes a `revalidate_thread_version(thread_slug, project_root)` helper AND the `## Proposed Scope` documents the acquire-then-refresh contract that an integrator MUST follow: after `acquire()` succeeds and while the lock is held, re-read live `bridge/INDEX.md`, recompute the next version, and assert `bridge/<slug>-NNN.md` is absent, before writing. A two-session stale-next-version regression test is added (`test_stale_next_version_detected_under_lock`). Because `-003` is foundation-only, the revalidation helper is a tested primitive; the integrator (follow-up WI) is responsible for calling it in the correct order.
- **F3 (P2) - test placement and command were ambiguous.** Addressed. `target_paths` now lists exactly one test file, `platform_tests/scripts/test_bridge_work_intent_registry.py` (the repo-native script-test lane per `pyproject.toml` `testpaths`). The duplicate `tests/scripts/...` path is removed and the verification command runs the same single file.
- **F4 (P2) - applicability preflight reported missing advisory specs.** Addressed. `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` are now cited in `## Specification Links` below.

## Claim

Add a lightweight, file-locked work-intent registry module at `scripts/bridge_work_intent_registry.py`. The module provides acquire / release / current-holder primitives keyed by bridge thread slug, plus a live-state revalidation helper. It is a **foundation primitive only**: this thread wires it into NO caller. The registry stores per-thread session-ownership records at `.gtkb-state/work-intent/<thread-slug>.json` with atomic writes and TTL-based stale-lock recovery. A successor work item integrates the module into the bridge-propose helper, the AXIS-2 surface, and the session-startup payload.

## In-Root Placement Evidence

All target paths are in-root under `E:\GT-KB`. `.gtkb-state/` is runtime state; the `.gitkeep` placeholder ensures the `work-intent/` directory exists. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - `bridge/INDEX.md` is canonical bridge workflow state; the revalidation helper re-reads live INDEX as the authority for the next version.
- `SPEC-AUQ-POLICY-ENGINE-001` - the registry is a deterministic coordination primitive within the bridge tooling surface.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root-only placement.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - cross-cutting constraint requiring this proposal to cite every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - cross-cutting constraint requiring the post-implementation VERIFIED step to rest on executed spec-derived tests; the verification plan maps every linked spec to a test.
- `GOV-STANDING-BACKLOG-001` - WI-3274 is a tracked standing-backlog work item; the follow-up integration WI is also tracked.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; the WI, this bridge thread, the new module, and the linked specs form the artifact graph for this work.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger discipline; the observed parallel-session collision triggered WI-3274, which triggers this implementation proposal and (separately) the follow-up integration WI.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline; this fix is captured as governed work (WI-3274) with a bridge artifact and spec-derived tests.

## Prior Deliberations

- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - records the owner decision authorizing the project grouping `PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS` that includes WI-3274.
- `DELIB-1499` - prior NO-GO on cross-harness-trigger rename-race / liveness diagnostics; relevant because it documents the bridge-automation race-risk class this module addresses.
- `DELIB-1517` - prior NO-GO on bridge-status automation; relevant because it rejected automation that did not match the real local execution surface; the foundation-only scoping of `-003` deliberately avoids that failure mode by NOT claiming integration this thread does not deliver.
- `DELIB-0573` - bridge closure-starvation root-cause report; background on bridge reliability and queue-state handling.

No prior deliberation rejected a work-intent registry primitive; this is the first proposal to add one.

## Owner Decisions / Input

This proposal depends on owner approval and is authorized by:

- 2026-05-14 UTC, S350+: owner approved the `GTKB-BRIDGE-TOOLING-ENHANCEMENTS` project authorization (AskUserQuestion answer "Authorize all 3 groups (7 WIs added)"), including WI-3274, archived in `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` (formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch2-three-project-authorizations.json`). Implementation proceeds autonomously through the bridge protocol under that project authorization; no new per-fix owner decision is required.

## Requirement Sufficiency

Existing requirements sufficient. WI-3274's description specifies the parallel-session collision symptoms and recommends option 2 (work-intent registry). This `-003` proposal implements the registry primitive only; the bridge-writer / AXIS-2 / startup-visibility integration WI-3274 also recommends is carried into the named follow-up work item below. No new or revised requirement or specification is created by this work.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a single-WI new-module change. It is not a bulk backlog operation: it performs no batch resolve, promote, or retire of work items or specifications. References to "work item", "backlog", and "standing backlog" describe the single work item WI-3274 (and its named follow-up successor) and the governed filing path only. The applicable evidence pattern is a single-WI tooling implementation proposal with formal-artifact-approval discipline preserved unchanged; the review-packet inventory is IP-1 + IP-2 in this single thread.

## Bridge INDEX Maintenance

This proposal keeps `bridge/INDEX.md` as the canonical bridge workflow state. The `-003` REVISED line is inserted at the top of the `gtkb-bridge-parallel-session-collision` document block in `bridge/INDEX.md`; no INDEX entry is removed or rewritten. The revalidation helper READS `bridge/INDEX.md` as the authority for the next version and does not mutate it.

## Proposed Scope

### IP-1: Work-intent registry foundation module

In `scripts/bridge_work_intent_registry.py`, expose:

```python
def acquire(thread_slug: str, session_id: str, ttl_seconds: int = 30) -> bool: ...
def release(thread_slug: str, session_id: str) -> None: ...
def current_holder(thread_slug: str) -> dict | None: ...
def revalidate_thread_version(thread_slug: str, project_root: Path) -> dict: ...
```

- `acquire()` writes `.gtkb-state/work-intent/<slug>.json` atomically (write-temp-then-rename) with `{session_id, acquired_at, ttl_expires_at}`. Returns `True` when the record was previously absent or expired (stale-recovery), or already held by the same `session_id` (idempotent). Returns `False` when held by a different non-expired session.
- `release()` removes the record file when it matches `session_id`; no-op otherwise.
- `current_holder()` reads the record; returns the dict, or `None` when absent or expired.
- `revalidate_thread_version()` re-reads live `bridge/INDEX.md`, finds the `Document: <thread_slug>` block, and returns `{latest_version, next_version, next_file_path, next_file_exists}` where `next_file_exists` reflects a live filesystem check of `bridge/<slug>-<next_version>.md`. This is the primitive an integrator uses to implement the acquire-then-refresh contract.

**Acquire-then-refresh contract (documented; enforced by the integrator, NOT this thread).** A future integrator that wires this module into a bridge writer MUST follow this order: (1) `acquire()` the thread lock; (2) while the lock is held, call `revalidate_thread_version()` and assert `next_file_exists is False`; (3) write `bridge/<slug>-NNN.md` and update `bridge/INDEX.md`; (4) `release()`. Step 2 closes the stale-next-version race in F2: a second session that computed `NNN` before the first session wrote sees `next_file_exists True` after acquiring and must recompute. `-003` ships this contract as documentation plus the tested `revalidate_thread_version()` primitive; it does NOT wire any caller.

### IP-2: Tests (platform_tests lane)

Tests are added under `platform_tests/scripts/test_bridge_work_intent_registry.py`, covering acquire / release / expiry / stale-recovery / atomic-write semantics and the revalidation helper on tmp-path fixtures, including the two-session stale-next-version regression case.

## Scope Boundary (What `-003` Does NOT Do)

To make the F1 re-scope explicit and reviewable:

- `-003` does NOT modify `.claude/skills/bridge-propose/helpers/write_bridge.py` or any bridge-writer path.
- `-003` does NOT add an AXIS-2 surface (`.claude/hooks/bridge-axis-2-surface.py` or equivalent).
- `-003` does NOT add a session-startup-payload visibility surface.
- `-003` does NOT add a `bridge-compliance-gate.py` hard mechanical gate.
- `-003` makes NO claim that it prevents concurrent same-thread writes; it ships an unintegrated, tested primitive plus the documented contract a successor WI will wire in.

## Follow-Up Work Item

Per the F1 recommended action (option a), the bridge-writer / AXIS-2 / startup-visibility integration that WI-3274's description recommends is carried into an explicit successor work item:

- **Title:** "Bridge work-intent registry integration: wire `bridge_work_intent_registry` into the bridge-propose helper, AXIS-2 surface, and session-startup payload (follow-up to WI-3274)."
- **Origin:** new (integration of the WI-3274 foundation primitive).
- **Project:** `PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS` (same project as WI-3274).
- **Scope:** call `acquire()` + the acquire-then-refresh contract from the bridge-propose helper; surface `current_holder()` in the AXIS-2 surface and the startup payload so a session sees another agent's active intent before drafting.

This successor WI is recorded as backlog work in MemBase `work_items` through the standard governed work-item creation path; this proposal does NOT create it (work-item creation is out of this proposal's `target_paths`). It is named here so Loyal Opposition can confirm the integration is not silently dropped, only deferred.

## Specification-Derived Verification Plan

Each linked specification maps to at least one test.

| Behavior / Spec coverage | Test | Covers |
|---|---|---|
| A fresh acquire on an unheld thread slug succeeds | `test_acquire_fresh_thread_succeeds` | `SPEC-AUQ-POLICY-ENGINE-001` |
| A second acquire by a different session while held and unexpired fails | `test_acquire_blocked_when_held_by_other` | `SPEC-AUQ-POLICY-ENGINE-001` |
| A re-acquire by the same session is idempotent (returns True) | `test_acquire_idempotent_for_same_session` | `SPEC-AUQ-POLICY-ENGINE-001` |
| An acquire after the prior holder's TTL expired recovers the stale lock | `test_acquire_recovers_after_expiry` | `SPEC-AUQ-POLICY-ENGINE-001` |
| `release()` removes the record only for the matching holder session | `test_release_succeeds_for_holder` | `SPEC-AUQ-POLICY-ENGINE-001` |
| `release()` is a no-op for a non-holder session | `test_release_noop_for_non_holder` | `SPEC-AUQ-POLICY-ENGINE-001` |
| The record file is written via atomic temp-then-rename (no torn read) | `test_acquire_atomic_via_temp_rename` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` |
| `revalidate_thread_version()` reads live `bridge/INDEX.md` and returns the correct latest/next version | `test_revalidate_returns_live_next_version` | `GOV-FILE-BRIDGE-AUTHORITY-001` |
| Two-session stale-next-version regression: session B computes `NNN`, session A writes `bridge/<slug>-NNN.md`, then `revalidate_thread_version()` for session B reports `next_file_exists True` and a recomputed higher `next_version` | `test_stale_next_version_detected_under_lock` | `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` |
| In-root placement: no target path is outside `E:\GT-KB` | covered by `target_paths` enumeration above | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` |
| Proposal cites all governing specs; this is a tracked WI | covered by `## Specification Links` and the WI-3274 metadata above | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `GOV-STANDING-BACKLOG-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` |

Verification command:

```
python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py -q --tb=short
python -m ruff check scripts/bridge_work_intent_registry.py
```

## Files Expected To Change

- `scripts/bridge_work_intent_registry.py` - new foundation module implementing IP-1 (acquire / release / current_holder / revalidate_thread_version).
- `platform_tests/scripts/test_bridge_work_intent_registry.py` - new test file holding the verification-plan tests, including the two-session stale-next-version regression case.
- `.gtkb-state/work-intent/.gitkeep` - placeholder ensuring the runtime-state directory exists.

## Acceptance Criteria

- IP-1 and IP-2 landed; all tests in the verification plan PASS via the platform test lane.
- Both bridge preflights PASS on `-003`.
- The module exposes `acquire`, `release`, `current_holder`, and `revalidate_thread_version` with the documented semantics.
- The two-session stale-next-version regression test passes, demonstrating the revalidation primitive surfaces the F2 race.
- `-003` makes NO integration changes (per `## Scope Boundary`); the successor integration WI is named in `## Follow-Up Work Item`.
- `ruff check` is clean on the new module.

## Risks / Rollback

- Risk: an NFS / network-mount filesystem may not support atomic rename. Mitigation: default Windows / local-disk paths are safe; the module documents the assumption.
- Risk: the foundation module ships with no caller, so the parallel-session race is not yet fixed. Mitigation: this is intentional and explicit per the F1 re-scope; the named follow-up WI delivers the integration; `-003` does not overclaim.
- Risk: TTL too short for a slow drafting session. Mitigation: 30 s is the default for the integrator to tune; the integration WI will choose a value appropriate to the drafting window.
- Rollback: remove `scripts/bridge_work_intent_registry.py`, its test file, and the `.gitkeep`; nothing depends on the new module because nothing calls it.

## Recommended Commit Type

`feat:` - new foundation module (net-new capability surface, unintegrated) plus tests.

## Pre-Filing Preflight

Both mandatory pre-filing preflights were run on this `-003` content after the `bridge/INDEX.md` `REVISED` entry was added; outputs are embedded in the `## Applicability Preflight` and `## Clause Applicability` sections below.

## Review Questions for Loyal Opposition

1. Is the foundation-only re-scope (option a) acceptable, with the integration deferred to the named follow-up WI?
2. Is `revalidate_thread_version()` the right shape for the acquire-then-refresh primitive, given `-003` does not itself call it from a writer?
3. Should the `.gtkb-state/work-intent/.gitkeep` placeholder be dropped in favor of the module creating the directory on first `acquire()`?

## Applicability Preflight

- packet_hash: `sha256:e5880ff8e9eaec1169be53f3706308f2f300e2626294f6b0bba07f42dd566a14`
- bridge_document_name: `gtkb-bridge-parallel-session-collision`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-parallel-session-collision-003.md`
- operative_file: `bridge/gtkb-bridge-parallel-session-collision-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-bridge-parallel-session-collision`
- Operative file: `bridge\gtkb-bridge-parallel-session-collision-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

Clause preflight exit code: 0 (pass; zero blocking gaps).

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
