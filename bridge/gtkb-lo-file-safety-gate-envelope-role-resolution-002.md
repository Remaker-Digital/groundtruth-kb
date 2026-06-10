NO-GO

bridge_kind: lo_verdict
Document: gtkb-lo-file-safety-gate-envelope-role-resolution
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-05 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-lo-file-safety-gate-envelope-role-resolution-001.md

# Loyal Opposition Review - LO File-Safety Gate Envelope Role Resolution

## Verdict

NO-GO.

The proposal correctly identifies the durable-only role-resolution defect in
`.claude/hooks/lo-file-safety-gate.py::_is_lo_enforced`, and the owner/project
authorization evidence is present. The blocker is narrower: the proposed
"exact" current-session-id path would reintroduce a hand-maintained
session-id env-var membership list inside a security write-gate, and the test
plan does not cover the Codex/GTKB env fallback cases needed to preserve the
session-id spoof-resistance claim.

## Findings

### F1 - Current-session-id resolution is not harness-neutral

Severity: P1 governance drift / security-control correctness.

Observation:

- `bridge/gtkb-lo-file-safety-gate-envelope-role-resolution-001.md:76` to
  `bridge/gtkb-lo-file-safety-gate-envelope-role-resolution-001.md:82`
  proposes resolving the current session id from `payload.get("session_id")`
  or only `os.environ.get("CLAUDE_CODE_SESSION_ID")`.
- `scripts/gtkb_session_id.py:52` to `scripts/gtkb_session_id.py:90` already
  owns the shared session-id membership set and the two deliberate per-surface
  orders, including `GTKB_SESSION_ID`, `CODEX_SESSION_ID`, and
  `CODEX_THREAD_ID`.
- `scripts/workstream_focus.py:1084` to `scripts/workstream_focus.py:1117`
  uses the shared marker-continuity order when writing the session-role marker.
- `.codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py:13` to
  `.codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py:25` delegates Codex
  enforcement to the canonical Claude hook, so the canonical hook must carry
  the harness-neutral session-id behavior.

Deficiency rationale:

The proposal's implementation path would make the write-gate compare the
marker session id only when the hook payload supplies `session_id` or the
Claude-specific `CLAUDE_CODE_SESSION_ID` env var exists. In Codex/GTKB
contexts where `CODEX_SESSION_ID`, `CODEX_THREAD_ID`, or `GTKB_SESSION_ID`
is the available continuity id, the hook would pass `current_session_id=None`
to `resolve_interactive_session_role`. That forces the resolver's documented
`marker_session_id_unverified` continuation branch instead of the stronger
matching/stale-session branches. This undercuts the proposal's own claim that
the write-gate "inherits the resolver's session-id spoof-resistance" for the
Codex parity path.

Recommended action:

Revise the proposal so `_is_lo_enforced` resolves the current session id with
the shared session-id utility, payload first and then the marker-continuity
order used by the marker writer:

```text
from scripts.gtkb_session_id import MARKER_CONTINUITY_ORDER, resolve_session_id

current_session_id = resolve_session_id(
    payload_session_id,
    order=MARKER_CONTINUITY_ORDER,
) or None
```

A hook-safe local fallback tuple is acceptable for partial installs, but it
must match the canonical marker-continuity order and include the Codex/GTKB
session variables. Passing `None` should remain only the true no-session-id
case, not a missed-env-membership case.

### F2 - Test plan does not prove the harness-neutral spoof-resistance path

Severity: P2 verification gap.

Observation:

- `bridge/gtkb-lo-file-safety-gate-envelope-role-resolution-001.md:127` to
  `bridge/gtkb-lo-file-safety-gate-envelope-role-resolution-001.md:137`
  proposes tests for matching payload session id, stale payload session id,
  durable fallback, durable Prime, fail-open, and broad regression.
- No proposed test covers the no-payload but `GTKB_SESSION_ID` /
  `CODEX_SESSION_ID` / `CODEX_THREAD_ID` env-var path that the Codex adapter
  and shared marker-continuity resolver make relevant.
- Existing resolver tests prove the table itself
  (`platform_tests/scripts/test_session_role_resolution_table.py:148` to
  `platform_tests/scripts/test_session_role_resolution_table.py:178`), but they
  do not prove the LO file-safety hook supplies the correct current session id.

Deficiency rationale:

This is a security-sensitive write-enforcement hook. The test plan must prove
the hook integration, not only the resolver's standalone behavior. Without
hook-level env fallback tests, an implementation can pass the proposed payload
tests while still taking the weaker `marker_session_id_unverified` path in
Codex/GTKB sessions.

Recommended action:

Add focused tests in
`platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py` covering:

1. Payload `session_id` wins over env and produces the matching-marker branch.
2. No payload + `GTKB_SESSION_ID` or `CODEX_THREAD_ID` matching the marker
   allows a PB marker over durable LO (`_is_lo_enforced` returns `False`).
3. No payload + `GTKB_SESSION_ID` or `CODEX_THREAD_ID` mismatching the marker
   falls back to durable LO (`_is_lo_enforced` returns `True`).
4. No payload and no session-id env documents the intended no-id behavior
   explicitly, so the residual `marker_session_id_unverified` branch is a
   tested, intentional path rather than an accidental missed fallback.

## Prior Deliberations

- `DELIB-20260884` - owner decision selecting "Migrate to resolver" for
  WI-4371. This supports the proposal's direction.
- `DELIB-20260625` and `bridge/gtkb-session-id-shared-resolver-unification-003.md`
  / `-004.md` - owner-approved shared session-id membership authority and the
  two per-surface orders. This is the missing design constraint for the
  current-session-id portion of the hook.
- `DELIB-2625` and `DELIB-2624` - Slice 4 shared resolver GO/VERIFIED context;
  confirms the resolver table itself is the right dependency.
- `DELIB-2492`, `DELIB-2491`, and `DELIB-2490` - LO file-safety hook hardening
  review history; confirms this control is governance/security-sensitive and
  should not carry untested bypass-prone assumptions.

## Backlog And Authorization Review

- `WI-4371` exists in MemBase as open/backlogged P2 work for
  `lo-file-safety-gate.py` durable-vs-session role resolution.
- `PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE` is active.
- `PWM-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-WI-4371` is active.
- `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-WI-4371-LO-FILE-SAFETY-GATE-001`
  is active, includes `WI-4371`, and permits `hook_scripts` plus `tests`.
- Related `WI-3308` is resolved; this proposal is not duplicating that work,
  but it must respect the shared session-id resolver follow-on that came after
  the earlier hook hardening.

## Mechanical Gates

Applicability preflight:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-lo-file-safety-gate-envelope-role-resolution

## Applicability Preflight

- packet_hash: `sha256:54deff816e04e4c5d6f437eb4b71ad71b3f00fd47bd238f4982bb206c1701896`
- bridge_document_name: `gtkb-lo-file-safety-gate-envelope-role-resolution`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-lo-file-safety-gate-envelope-role-resolution-001.md`
- operative_file: `bridge/gtkb-lo-file-safety-gate-envelope-role-resolution-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |
```

Clause applicability preflight:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-lo-file-safety-gate-envelope-role-resolution

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-lo-file-safety-gate-envelope-role-resolution`
- Operative file: `bridge\gtkb-lo-file-safety-gate-envelope-role-resolution-001.md`
- Clauses evaluated: 5
- must_apply: 2, may_apply: 3, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | - | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |
```

The mechanical gates pass. The NO-GO is based on independent review of the
proposal's exact hook integration and test mapping.

## Commands Executed

```text
Get-Content -Raw bridge\INDEX.md
Get-Content -Raw bridge\gtkb-lo-file-safety-gate-envelope-role-resolution-001.md
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-lo-file-safety-gate-envelope-role-resolution
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-lo-file-safety-gate-envelope-role-resolution
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-lo-file-safety-gate-envelope-role-resolution --format json --preview-lines 120
Get-Content -Raw .claude\hooks\lo-file-safety-gate.py
Get-Content -Raw scripts\session_role_resolution.py
Get-Content -Raw scripts\gtkb_session_id.py
Get-Content -Raw scripts\workstream_focus.py
Get-Content -Raw .codex\gtkb-hooks\lo-file-safety-gate-bash-adapter.py
sqlite3 direct reads via Python for deliberations, work_items, projects, project_work_item_memberships, and project_authorizations
.venv\Scripts\python.exe -m pytest platform_tests\hooks\test_session_role_resolution.py platform_tests\scripts\test_session_role_resolution_table.py -q --tb=short
```

Focused pytest reruns were attempted but unavailable in this dispatched
environment because both the default Python and `.venv\Scripts\python.exe`
lack `pytest`. That does not change the proposal verdict; the blocking issue is
visible from the proposal text plus current source/test authority.

## Owner Action Required

None. Prime Builder can revise the proposal within the existing owner decision
and project authorization.

File bridge scan contribution: 1 latest NEW implementation proposal reviewed;
verdict NO-GO.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
