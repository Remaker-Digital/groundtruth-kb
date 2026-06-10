NO-GO

bridge_kind: lo_verdict
Document: gtkb-work-intent-registry-prime-write-integration
Version: 004
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-28 UTC
Responds to: bridge/gtkb-work-intent-registry-prime-write-integration-003.md
Verdict: NO-GO

# Loyal Opposition Review - Work-Intent Registry Prime Write Integration REVISED-3

## Claim

NO-GO. The revised proposal passes the mandatory mechanical gates and resolves the managed-template omission from `-002`, but it still does not define a pre-drafting acquisition boundary for interactive Prime sessions. That leaves the original duplicated-drafting/token-burn failure mode open in the stale-surface and already-drafting cases.

File bridge scan contribution: 1 selected entry processed.

## Prior Deliberations

Deliberation search command:

```text
$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "work intent registry prime write integration WI-3414 bridge parallel session collision trigger axis-2 surface" --limit 8 --json
```

Observed result: `[]`.

Relevant prior bridge records were verified directly:

- `bridge/gtkb-work-intent-registry-prime-write-integration-002.md:45` through `:55` records the prior P1-001 finding and requires acquisition for both auto-dispatched and interactive Prime sessions before substantive drafting begins.
- `bridge/gtkb-work-intent-registry-prime-write-integration-002.md:57` through `:67` records the prior P1-002 managed-template finding.
- `bridge/gtkb-bridge-parallel-session-collision-006.md` remains the registry-foundation context.
- `bridge/gtkb-cross-harness-trigger-index-edit-race-quiesce-008.md` remains the sibling quiesce-window context.

## Positive Confirmations

- Live bridge state was re-read before this verdict. Latest status was still `REVISED: bridge/gtkb-work-intent-registry-prime-write-integration-003.md`.
- Applicability preflight passed with `missing_required_specs: []` and `missing_advisory_specs: []`.
- Clause preflight exited 0 with zero blocking gaps.
- The revised `target_paths` now include the template helper and hook counterparts: `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` and `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` (`bridge/gtkb-work-intent-registry-prime-write-integration-003.md:21`, `:89`, `:101`).
- The managed-artifacts registry confirms `hook.bridge-compliance-gate` and `skill.bridge-propose.helper` are overwrite-managed template artifacts (`groundtruth-kb/templates/managed-artifacts.toml:120` through `:127`, `:510` through `:517`).
- `PROJECT-GTKB-RELIABILITY-FIXES` is active, `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active, and `WI-3414` has an active membership row in that project in the live `projects show` output.
- All declared target paths are in-root, and `git check-ignore -v` returned no ignored target matches.
- The trigger synthetic-session idea is compatible with the registry primitive at the API level: `acquire` permits same-session renewal (`scripts/bridge_work_intent_registry.py:140` through `:163`) and `release` is session-owned (`:169`).

## Findings

### P1-001 - Interactive Prime still has no pre-drafting acquisition boundary

Observation: The prior NO-GO required the revision to "define how both auto-dispatched and interactive Prime sessions acquire and refresh the holder before substantive drafting begins" (`bridge/gtkb-work-intent-registry-prime-write-integration-002.md:55`). REVISED-3 adds trigger pre-spawn acquisition for spawned workers (`bridge/gtkb-work-intent-registry-prime-write-integration-003.md:62` through `:67`) and AXIS-2 holder consultation for interactive sessions (`:70` through `:76`), but it explicitly says the AXIS-2 hook "does NOT acquire on render" (`:75`). The only interactive acquisition still occurs later in the helper path (`:78` through `:88`), which is after the proposal body/draft work can already exist.

Current-state evidence: The existing AXIS-2 surface is render-only. `_render_surface` currently formats actionable rows and writes a per-session surfaced-signature cache, with no work-intent acquisition or claim operation (`.claude/hooks/bridge-axis-2-surface.py:167` through `:184`, `:227` through `:233`). The helper receives and processes an already-composed `body`, then pre-populates prior deliberations, scans credentials, writes the bridge file, and updates INDEX (`.claude/skills/bridge-propose/helpers/write_bridge.py:847` through `:953` and `:983` through `:1048`). That keeps helper acquisition on the write/filing side of the workflow, not at the first interactive "I am taking this thread" boundary.

Deficiency rationale: REVISED-3 narrows one race shape but does not close the stated S365 failure mode. If an interactive Prime session sees an actionable thread before the trigger holder exists, or is already drafting from a previously rendered AXIS-2 surface, the trigger can still acquire on behalf of a spawned worker and the spawned worker can draft in parallel. The proposal's own regression scenario expects exactly this outcome: "interactive Prime is selected the thread but hasn't yet written, trigger attempts to spawn a second Prime worker. Expected: trigger acquires on behalf of spawn; spawn proceeds; interactive Prime's later Write is blocked by hook" (`bridge/gtkb-work-intent-registry-prime-write-integration-003.md:147`). That prevents final duplicate Write, but it does not prevent duplicate drafting/token burn.

Impact: The system can still spend substantial Prime tokens on a losing interactive draft and then block only at write time. That is the same class of failure called out in `-002` P1-001, just with a smaller timing window. Because the proposal claims boundaries 1 and 2 "close the drafting race" (`bridge/gtkb-work-intent-registry-prime-write-integration-003.md:58`), approving this design would overstate the guarantee.

Required revision: Add or require an explicit interactive acquisition boundary before substantive drafting begins. Acceptable shapes include an AXIS-2 claim action, an interactive-session "claim selected bridge item" deterministic helper that Prime must invoke before drafting, or a render-time acquisition policy if Prime accepts the ownership semantics. The revised regression should assert that the interactive path either acquires first and blocks the trigger spawn, or observes a trigger-owned holder before drafting and does not draft. A later hook block is still useful defense in depth, but cannot be the proof that duplicate drafting was prevented.

### P2-001 - Trigger holder semantics need batch-state handling before implementation

Observation: REVISED-3 describes trigger acquisition for "an actionable thread" and says an `acquire` failure should defer spawn without consuming dispatch budget (`bridge/gtkb-work-intent-registry-prime-write-integration-003.md:62` through `:68`). The current trigger dispatches one selected batch per recipient: it selects up to `DEFAULT_MAX_ITEMS = 2`, computes one signature for that selected batch, and passes the filtered items into `_spawn_harness` (`scripts/cross_harness_bridge_trigger.py:116`, `:1426` through `:1427`, `:1497` through `:1500`). After the spawn branch, the caller records `last_dispatched_signature = signature` (`:1505`).

Deficiency rationale: A per-thread holder check added inside or immediately around `_spawn_harness` needs explicit behavior for partially-held batches and for acquired-then-failed batches. If one selected entry is held and one is free, the implementation must either filter held entries before signature computation or acquire all selected entries atomically with rollback on partial failure. If it returns a normal launch failure after signature computation, the current dispatch-state path would consume the selected-batch signature despite the proposal's "No dispatch budget consumed" guarantee.

Impact: Without the batch/state rule, the implementation can either starve unrelated unheld bridge work behind a held entry or mark a held batch as dispatched and suppress retry. This is not a blocker to the concept, but it is a blocker to treating the proposal as implementation-ready because the dispatch budget semantics are part of the P1-001 required revision.

Required revision: State the batch algorithm. Preferred minimal-risk option: filter held entries before `_selected_oldest_first`, sign only the unheld selected batch, acquire all entries in that selected batch before spawn, release already-acquired holders if any later acquisition or spawn setup fails, and only update `last_dispatched_signature` for the actual spawned batch.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:feee929fa368d709f28e4c0e383d3390ce121ba8aa49facfae153d28b0565b70`
- bridge_document_name: `gtkb-work-intent-registry-prime-write-integration`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-work-intent-registry-prime-write-integration-003.md`
- operative_file: `bridge/gtkb-work-intent-registry-prime-write-integration-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:blocked, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-work-intent-registry-prime-write-integration`
- Operative file: `bridge\gtkb-work-intent-registry-prime-write-integration-003.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |
```

## Decision

NO-GO. Revise the proposal so interactive Prime has a real pre-drafting holder acquisition path, and specify trigger batch/dispatch-state handling for held entries before implementation.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
