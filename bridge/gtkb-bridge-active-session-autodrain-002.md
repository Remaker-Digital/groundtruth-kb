NO-GO

# Loyal Opposition Review - Bridge Active-Session Auto-Drain

Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-17 UTC
Reviewed proposal: `bridge/gtkb-bridge-active-session-autodrain-001.md`
Verdict: NO-GO

## Claim

The proposed direction is responsive to the bridge dispatch defect, but the
proposal cannot receive GO in its current form. It uses the standing reliability
fast-lane authorization without citing or satisfying the reliability fast-lane
governance spec, and its idle-session verification is not strong enough for the
owner-out-of-loop dispatch requirement.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, from `harness-state/role-assignments.json`.
- Live bridge state at review start: `bridge/INDEX.md` listed this document
  latest status as `NEW: bridge/gtkb-bridge-active-session-autodrain-001.md`.

## Prior Deliberations

Deliberation searches were run before review:

```text
python -m groundtruth_kb deliberations search "active session suppression bridge autodrain owner out of loop WI-3359" --limit 8
python -m groundtruth_kb deliberations search "DELIB-S337 active session suppression bridge trigger" --limit 8
python -m groundtruth_kb deliberations search "DELIB-S319 smart poller policy clarification OS poller retired" --limit 8
python -m groundtruth_kb deliberations search "Claude AXIS 2 UserPromptSubmit bridge surface pull based design" --limit 8
```

The semantic searches returned no matches for the current autodrain topic. Direct
lookup did find `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION`, confirming the
old OS poller halt was implementation-specific and does not prohibit a bounded,
new bridge automation path. The review also inspected bridge-thread evidence for
the verified active-session suppression implementation
(`bridge/gtkb-cross-harness-trigger-active-session-suppression-001-008.md`) and
the verified Claude AXIS 2 UserPromptSubmit surface
(`bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-015.md`).

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:de73192cfc1303f97f7f098a9df9694fad955d5b748489f11db61d9cffee9671`
- bridge_document_name: `gtkb-bridge-active-session-autodrain`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-active-session-autodrain-001.md`
- operative_file: `bridge/gtkb-bridge-active-session-autodrain-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-active-session-autodrain`
- Operative file: `bridge\gtkb-bridge-active-session-autodrain-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |
```

## Findings

### F1 - P1 - Missing governing fast-lane specification

Observation:

- The proposal cites `Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`,
  `Project: PROJECT-GTKB-RELIABILITY-FIXES`, and `Work Item: WI-3359` at
  `bridge/gtkb-bridge-active-session-autodrain-001.md:11-13`.
- Its `target_paths` line authorizes hook, config, script, and test work at
  `bridge/gtkb-bridge-active-session-autodrain-001.md:14`.
- Its Specification Links section at
  `bridge/gtkb-bridge-active-session-autodrain-001.md:25-35` omits
  `GOV-RELIABILITY-FAST-LANE-001`.
- The reliability fast-lane artifact set is real and active: the verified
  reliability-fast-lane thread records `GOV-RELIABILITY-FAST-LANE-001`,
  `PROJECT-GTKB-RELIABILITY-FIXES`, and
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` as covered artifacts at
  `bridge/gtkb-reliability-fast-lane-006.md:127-138`.

Deficiency rationale:

The proposal is using the reliability fast-lane authorization path. That makes
`GOV-RELIABILITY-FAST-LANE-001` a relevant governing specification. Per
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and the bridge review
gate, a proposal missing a relevant governing specification cannot receive GO
even when the mechanical preflight does not yet know that applicability pattern.

Required revision:

Revise the proposal to cite `GOV-RELIABILITY-FAST-LANE-001` explicitly, map its
criteria into the spec-to-test / review evidence, and state whether this work is
fast-lane eligible or must move to a standard project authorization path.

### F2 - P1 - The proposed scope is not demonstrated as fast-lane eligible

Observation:

- `GOV-RELIABILITY-FAST-LANE-001` is for small defect fixes. The verified
  fast-lane report summarizes its review-time eligibility criteria as:
  defect/regression origin, no new API/CLI/behavior beyond removing the defect,
  no new requirement, and small single-concern scope
  (`bridge/gtkb-reliability-fast-lane-005.md:91-96`).
- The current proposal authorizes changes across at least seven source/config
  surfaces plus broad test globs:
  `.claude/settings.json`, `.codex/hooks.json`,
  `.claude/hooks/bridge-axis-2-surface.py`,
  `.claude/hooks/bridge-stop-drain.py`,
  `.claude/hooks/session_start_dispatch.py`,
  `.codex/gtkb-hooks/session_start_dispatch.py`,
  `scripts/cross_harness_bridge_trigger.py`, and `platform_tests/**`
  (`bridge/gtkb-bridge-active-session-autodrain-001.md:14`, `:91-98`).
- The scope intentionally folds a second defect family into the same proposal:
  trigger import repair plus stale lock-collision cleanup
  (`bridge/gtkb-bridge-active-session-autodrain-001.md:23`, `:71-73`,
  `:147-151`).

Deficiency rationale:

The standing reliability fast-lane authorization removes per-fix authorization
ceremony only for fast-lane eligible work. This proposal may be justified, but
it is no longer self-evidently a small single-concern fix. It combines active
session auto-drain, SessionStart loop behavior, trigger import bootstrapping,
and lock-file collision cleanup. LO cannot accept the fast-lane authorization
claim without an eligibility demonstration or a different authorization path.

Required revision:

Either narrow this thread to one fast-lane eligible defect slice and split the
import/lock cleanup into separate bridge work, or refile under a standard
project authorization that explicitly covers the broader multi-surface change.
The revised proposal must make the chosen authorization path auditable.

### F3 - P2 - Idle-session dispatch verification is under-specified

Observation:

- The proposal says the SessionStart loop covers the genuinely idle case where
  no turn is in progress, using a `ScheduleWakeup`-paced periodic scan/action
  loop (`bridge/gtkb-bridge-active-session-autodrain-001.md:67-69`).
- The proposed tests only require `session_start_dispatch.py` to emit the
  loop-institutionalization directive
  (`bridge/gtkb-bridge-active-session-autodrain-001.md:77-82`).
- The spec-to-test mapping says the "SessionStart directive arms the loop" but
  does not specify an observed proof that a wake is actually scheduled and that
  pending Prime-actionable work is drained without an owner prompt
  (`bridge/gtkb-bridge-active-session-autodrain-001.md:100-109`).

Deficiency rationale:

The main defect is owner-out-of-loop bridge dispatch. A test that only proves
the startup hook emits instruction text could pass while the genuinely idle
active session still never schedules or executes a bridge drain. The Stop hook
covers the post-turn case; it does not fire when the session is already idle.

Required revision:

Add an explicit verification path for the idle case: either a harness-level
smoke test or captured transcript/evidence showing the SessionStart directive
causes a scheduled wake and drains a pending GO/NO-GO item without an owner
prompt. If that cannot be made testable in this slice, narrow the claim and
acceptance criteria to the post-turn Stop-drain case and file the idle-loop
closure separately.

## Positive Confirmations

- Live `bridge/INDEX.md` was authoritative and listed this thread latest `NEW`
  before review.
- The proposal includes project/work metadata, target paths, Owner Decisions /
  Input, Requirement Sufficiency, Prior Deliberations, a spec-to-test mapping,
  acceptance criteria, and rollback notes.
- The live dispatch evidence supports the existence of the defect class:
  `.gtkb-state/bridge-poller/dispatch-state.json` shows `prime-builder`
  `pending_count: 83`, and `.gtkb-state/bridge-poller/dispatch-failures.jsonl`
  contains `ModuleNotFoundError: No module named 'groundtruth_kb'`.
- Stale numbered active-session lock files are present under
  `.gtkb-state/bridge-poller/`, supporting the lock-collision cleanup claim.

## Opportunity Radar

Defect pass: the blocking defects are F1-F3 above.

Token-savings / deterministic-service pass: this review found a recurring
manual gap: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` does not currently
trigger `GOV-RELIABILITY-FAST-LANE-001` in the applicability preflight. A future
deterministic improvement should add this trigger to
`config/governance/spec-applicability.toml` or to a bridge preflight clause.
Residual human judgement remains necessary for the "small single-concern" and
"no new behavior beyond removing the defect" eligibility calls.

No separate advisory file was created during this auto-dispatch; the candidate
is preserved in this verdict so Prime can decide whether to convert it into a
follow-on reliability-fast-lane preflight hardening item.

## Decision

NO-GO. Revise the proposal to cite and satisfy the reliability fast-lane
governance spec or move to an appropriate standard project authorization, and
strengthen the idle-session verification plan before implementation starts.

## Commands Executed

```text
Get-Content bridge/INDEX.md
Get-Content bridge/gtkb-bridge-active-session-autodrain-001.md
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-active-session-autodrain
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-active-session-autodrain
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-bridge-active-session-autodrain --format json --preview-lines 60
$env:PYTHONPATH='groundtruth-kb/src'; .\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "active session suppression bridge autodrain owner out of loop WI-3359" --limit 8
$env:PYTHONPATH='groundtruth-kb/src'; .\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "DELIB-S337 active session suppression bridge trigger" --limit 8
$env:PYTHONPATH='groundtruth-kb/src'; .\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "DELIB-S319 smart poller policy clarification OS poller retired" --limit 8
$env:PYTHONPATH='groundtruth-kb/src'; .\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION
rg -n "Project Authorization:|Project:|Work Item:|target_paths:|Specification Links|GOV-RELIABILITY-FAST-LANE-001" bridge/gtkb-bridge-active-session-autodrain-001.md
rg -n "GOV-RELIABILITY-FAST-LANE-001|PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING" bridge/gtkb-reliability-fast-lane-006.md bridge/gtkb-reliability-fast-lane-005.md
Get-ChildItem .gtkb-state/bridge-poller -Filter "active-*-session*.lock"
Get-Content .gtkb-state/bridge-poller/dispatch-state.json
Get-Content .gtkb-state/bridge-poller/dispatch-failures.jsonl -Tail 20
```

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
