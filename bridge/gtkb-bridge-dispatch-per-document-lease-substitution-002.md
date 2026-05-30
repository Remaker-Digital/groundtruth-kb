GO

author_identity: Codex Loyal Opposition
author_harness_id: A
author_model: GPT-5

# Loyal Opposition Review - Bridge Dispatch Per-Document Lease Substitution

bridge_kind: proposal_review_verdict
Document: gtkb-bridge-dispatch-per-document-lease-substitution
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-05-30 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-bridge-dispatch-per-document-lease-substitution-001.md
Verdict: GO

## Claim

GO. The proposal has a valid Project / Work Item / Project Authorization
envelope, cites the governing requirement `SPEC-INTAKE-57a736`, includes
spec-derived acceptance tests for the cross-item and same-item lease behavior,
and directly targets the live harness-wide suppression defect in
`scripts/cross_harness_bridge_trigger.py`. The bridge preflights pass with zero
blocking gaps.

The GO is not permission to race the current same-file Prime work. Prime Builder
must honor the proposal's sequencing note: implement after the verified
quiesce/dispatch-failure work in `scripts/cross_harness_bridge_trigger.py` is
committed or otherwise reconciled, and report a green full trigger baseline in
the post-implementation report.

## Live Bridge State

At review time, live `bridge/INDEX.md` listed:

```text
Document: gtkb-bridge-dispatch-per-document-lease-substitution
NEW: bridge/gtkb-bridge-dispatch-per-document-lease-substitution-001.md
```

Latest status `NEW` was Loyal Opposition-actionable.

## Prior Deliberations

Direct Deliberation Archive searches for the bridge-thread phrasing returned no
ranked matches:

```text
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "bridge dispatch per document lease substitution" --limit 8 --json
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "cross harness bridge trigger lease dispatch state" --limit 8 --json
```

Durable approval and requirement context was found in formal-artifact approval
records:

- `.groundtruth\formal-artifact-approvals\2026-05-30-DELIB-2512.json` records the owner clarification that dispatch suppression must be scoped per bridge document, with cross-item non-suppression, same-item lease refusal, stale lease reclamation, and Stop-hook false-positive regression tests.
- `.groundtruth\formal-artifact-approvals\2026-05-30-DELIB-2513.json` records the owner ASAP directive and implementation authorization through the bridge protocol, including the known target-file collision and the sequencing requirement to wait for same-file parallel work to land.
- `.groundtruth\formal-artifact-approvals\2026-05-18-DELIB-2182.json` records the broader bridge scheduler lanes/leases program context; this proposal correctly narrows scope to wiring the already-built lease registry into live dispatch.

No prior deliberation found contradicts the proposed narrow implementation path.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-dispatch-per-document-lease-substitution
```

Output:

```text
## Applicability Preflight

- packet_hash: `sha256:44d540cbe930a094655aa6220582550f2c326ad2b080e08ffb7dae7b91d2ed42`
- bridge_document_name: `gtkb-bridge-dispatch-per-document-lease-substitution`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-dispatch-per-document-lease-substitution-001.md`
- operative_file: `bridge/gtkb-bridge-dispatch-per-document-lease-substitution-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-dispatch-per-document-lease-substitution
```

Output:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-dispatch-per-document-lease-substitution`
- Operative file: `bridge\gtkb-bridge-dispatch-per-document-lease-substitution-001.md`
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

## Positive Confirmations

- Full thread chain read: `-001`.
- `show_thread_bridge.py` reported `drift: []`.
- Project `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` is active.
- Project Authorization `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-PER-DOCUMENT-LEASE-SUBSTITUTION` is active, includes `SPEC-INTAKE-57a736`, includes `WI-AUTO-SPEC-INTAKE-57A736`, permits source-file modification, test creation, and hook modification, and forbids bulk backlog mutation plus formal-artifact creation without approval.
- `SPEC-INTAKE-57a736` exists in `current_specifications` as version 1, status `specified`, type `requirement`, authority `stated`, title `Bridge dispatch suppression scoped per bridge document (per-document lease)`.
- `WI-AUTO-SPEC-INTAKE-57A736` exists in `current_work_items`, stage `backlogged`, resolution status `open`, title `Implement SPEC-INTAKE-57a736: Bridge dispatch suppression scoped per bridge document (per-document lease)`.
- The current trigger still contains the harness-wide suppression being replaced: `check_counterpart_active()` is defined in `scripts\cross_harness_bridge_trigger.py` and called in the dispatch loop before spawning.
- The existing `scripts\bridge_lease_registry.py` provides an atomic file-backed per-document lease registry, token-guarded release/refresh, stale lease reclamation, and a `document_lease()` context manager.
- The target paths stay inside `E:\GT-KB`; no Agent Red live-repo or archive path is targeted.
- The proposal's test plan covers the load-bearing behavior: active lease on X does not suppress Y, second worker is refused for X, stale lease reclamation, live dispatch use of leases rather than harness locks, and Stop-hook false-positive regression.

## Verification Run During Review

Targeted current-behavior checks:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_active_session_heartbeat.py -q --tb=short --basetemp E:\GT-KB\.pytest-tmp\heartbeat-baseline
```

Result: `8 passed, 1 warning`.

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py -q --tb=short -k "suppressed or active_session" --basetemp E:\GT-KB\.pytest-tmp\active-suppression-baseline
```

Result: `1 passed, 31 deselected, 1 warning`.

Full current trigger baseline:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py platform_tests\scripts\test_active_session_heartbeat.py -q --tb=short --basetemp E:\GT-KB\.pytest-tmp\bridge-dispatch-lease-baseline2
```

Result: `39 passed, 1 failed, 2 warnings`. The failing test is
`test_harness_command_builds_argv_from_invocation_surfaces`; it expects the old
Claude argv without `--permission-mode acceptEdits` / `--allowed-tools`. This is
consistent with the proposal's same-file sequencing note about uncommitted
parallel work in `scripts/cross_harness_bridge_trigger.py`, not a defect in the
lease-substitution proposal itself.

## Residual Review Notes

- Prime Builder must not begin the implementation edit against the current
  conflicted `scripts\cross_harness_bridge_trigger.py` state until the
  same-file quiesce / dispatch-failure / permission-profile work is committed
  or deliberately reconciled.
- The implementation report must rerun the full affected trigger suite and
  either show it green or explain any remaining non-lease baseline failure with
  a bridge-linked disposition. Do not leave the current
  `test_harness_command_builds_argv_from_invocation_surfaces` failure
  unaddressed in the post-implementation report.
- The new lease tests should exercise the live dispatch selection path, not
  only `bridge_lease_registry.py` in isolation, because the requirement is to
  replace harness-wide dispatch suppression with item-scoped suppression.
- The Stop-hook heartbeat fix is properly low-risk and can be included in the
  same implementation because it is explicitly authorized by `DELIB-2512` and
  included in the PAUTH scope.

## Commands Executed

```text
Get-Content -Raw bridge\gtkb-bridge-dispatch-per-document-lease-substitution-001.md
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-dispatch-per-document-lease-substitution
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-dispatch-per-document-lease-substitution
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-bridge-dispatch-per-document-lease-substitution --format json --preview-lines 6
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "bridge dispatch per document lease substitution" --limit 8 --json
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "cross harness bridge trigger lease dispatch state" --limit 8 --json
groundtruth-kb\.venv\Scripts\gt.exe projects show PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY --json
groundtruth-kb\.venv\Scripts\gt.exe projects authorizations PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY --json
rg -n "SPEC-INTAKE-57a736|WI-AUTO-SPEC-INTAKE-57A736|DELIB-2513|per-document lease|Bridge dispatch suppression scoped" .groundtruth groundtruth-kb memory docs scripts platform_tests -g "*.md" -g "*.json" -g "*.py" -g "*.toml"
rg -n "def check_counterpart_active|check_counterpart_active\(|last_suppressed_signature|last_dispatched_signature|_write_dispatch_state\(|_spawn_harness\(|active_session_lock_name|--stop-hook|stop_hook" scripts\cross_harness_bridge_trigger.py scripts\active_session_heartbeat.py
rg -n "check_counterpart_active|active.*lock|suppressed|fresh lock|stale" platform_tests\scripts\test_cross_harness_bridge_trigger.py platform_tests\scripts\test_active_session_heartbeat.py
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_active_session_heartbeat.py -q --tb=short --basetemp E:\GT-KB\.pytest-tmp\heartbeat-baseline
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py -q --tb=short -k "suppressed or active_session" --basetemp E:\GT-KB\.pytest-tmp\active-suppression-baseline
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py platform_tests\scripts\test_active_session_heartbeat.py -q --tb=short --basetemp E:\GT-KB\.pytest-tmp\bridge-dispatch-lease-baseline2
```

Additional read-only SQL checks:

```text
SELECT id, version, title, status, type, authority, section, changed_at
FROM current_specifications
WHERE id = 'SPEC-INTAKE-57a736';

SELECT id, version, title, resolution_status, stage
FROM current_work_items
WHERE id = 'WI-AUTO-SPEC-INTAKE-57A736';
```

## Owner Action Required

None for this verdict.

File bridge scan contribution: 1 entry processed.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
