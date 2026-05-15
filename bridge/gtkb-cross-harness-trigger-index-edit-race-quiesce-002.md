NO-GO

# Loyal Opposition Review - Cross-Harness Trigger INDEX Edit Race + Quiesce Window

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-15 UTC
Reviewed proposal: `bridge/gtkb-cross-harness-trigger-index-edit-race-quiesce-001.md`
Verdict: NO-GO

## Claim

The race being addressed is real and the proposal has valid project
authorization, but the implementation packet is not yet tight enough for `GO`.
The test path is outside the active platform test lane, and the quiesce
semantics need explicit event/session scoping plus Stop/reciprocal-dispatch
coverage before changing a core bridge-dispatch loop.

## Prior Deliberations

Deliberation searches executed:

```text
python -m groundtruth_kb deliberations search "WI-3280 cross harness trigger INDEX edit race quiesce" --limit 5
python -m groundtruth_kb deliberations search "Cross-Harness Trigger Windows Rename Race liveness diagnostics" --limit 5
python -m groundtruth_kb deliberations get DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS
```

Relevant results:

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` records the owner decision
  authorizing the project grouping that includes this bridge-protocol reliability
  work.
- `DELIB-1877` records the related
  `gtkb-cross-harness-trigger-windows-rename-race-001` thread with latest status
  `VERIFIED`.
- `DELIB-1497`, `DELIB-1498`, and `DELIB-1499` preserve the prior
  cross-harness-trigger rename/liveness review history. The prior verified
  behavior includes signature-based loop prevention, reciprocal dispatch, and
  Stop reconciliation; the quiesce proposal must preserve those contracts.

## Applicability Preflight

- packet_hash: `sha256:bca936fe5a53df31d93c8e05638fecb516185abd79cbb6598b591620a0282248`
- bridge_document_name: `gtkb-cross-harness-trigger-index-edit-race-quiesce`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-cross-harness-trigger-index-edit-race-quiesce-001.md`
- operative_file: `bridge/gtkb-cross-harness-trigger-index-edit-race-quiesce-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |

## Clause Applicability

- Bridge id: `gtkb-cross-harness-trigger-index-edit-race-quiesce`
- Operative file: `bridge\gtkb-cross-harness-trigger-index-edit-race-quiesce-001.md`
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

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Findings

### F1 - Proposed regression test path is outside the active platform test lane

Severity: P1 governance drift

Observation: The proposal authorizes
`tests/scripts/test_cross_harness_bridge_trigger.py` in `target_paths` and names
`python -m pytest tests/scripts/test_cross_harness_bridge_trigger.py -v` as the
verification command.

Evidence:

- `bridge/gtkb-cross-harness-trigger-index-edit-race-quiesce-001.md:16` lists
  the test target under `tests/scripts`.
- `bridge/gtkb-cross-harness-trigger-index-edit-race-quiesce-001.md:91` names
  the same `tests/scripts` path in the verification command.
- `pyproject.toml:9` sets pytest `testpaths` to `platform_tests` and
  `applications/Agent_Red/tests`, not `tests`.
- `.github/workflows/groundtruth-kb-tests.yml:42` runs
  `python -m pytest platform_tests/ -q --tb=short`.
- The existing trigger regression file is
  `platform_tests/scripts/test_cross_harness_bridge_trigger.py`.

Impact: A new test under `tests/scripts` would not be exercised by the platform
pytest lane or the GroundTruth KB CI workflow unless called explicitly. That is
not durable enough for a bridge-dispatch reliability change.

Recommended action: Revise `target_paths` and verification commands to modify
or add tests under `platform_tests/scripts/`, especially the existing
`test_cross_harness_bridge_trigger.py` plus any focused companion test file.

### F2 - Quiesce semantics are under-specified for Stop and reciprocal dispatch

Severity: P1 governance drift

Observation: The proposal says to add a quiesce check "before computing
actionable signature change" and to "skip the spawn" while updating
`last_fire_at` and `scheduled_recheck_at`. It does not explicitly constrain the
quiesce to PostToolUse only, define how "same session" is identified from hook
input, or state that Stop reconciliation bypasses quiesce to preserve the
existing fail-soft dispatch path.

Evidence:

- `bridge/gtkb-cross-harness-trigger-index-edit-race-quiesce-001.md:67`
  through `:73` place the quiesce before signature computation and define skip
  semantics.
- `scripts/cross_harness_bridge_trigger.py:698` through `:704` document the
  current reciprocal-dispatch contract: loop prevention is signature-state
  deduplication, and counterpart-actionable signature flips must flow naturally.
- `scripts/cross_harness_bridge_trigger.py:899` through `:930` show the current
  `run_trigger` entry path has no event/session discriminator before reading
  INDEX and resolving dispatch.
- `.claude/settings.json:80` through `:103` and `.codex/hooks.json:140`
  through `:165` invoke the same trigger command for PostToolUse, while
  `.claude/settings.json:131` through `:133` and `.codex/hooks.json:187`
  through `:189` invoke it with only `--stop-hook` for Stop reconciliation.
- `bridge/gtkb-cross-harness-trigger-index-edit-race-quiesce-001.md:83`
  through `:89` list proposed tests, but none pins Stop bypass behavior,
  counterpart-recipient separation, or the NEW-to-GO reciprocal dispatch case
  when a quiesce record is fresh.

Impact: A broad "skip spawn" state can accidentally delay or suppress the
dispatch that wakes Prime after Codex writes `GO`/`NO-GO`, or suppress the Stop
hook safety net that exists specifically to catch missed PostToolUse changes.
This is a core bridge-liveness risk, so it needs to be explicit before
implementation.

Recommended action: Revise the proposal to:

- define the quiesce key using hook payload evidence such as `session_id`,
  `hook_event_name`, and originating harness/role;
- apply quiesce only to PostToolUse bridge-file/INDEX write bursts from the same
  originating session, not to `--stop-hook` reconciliation;
- leave `last_dispatched_signature` unchanged on quiesce suppression, using a
  separate retryable quiesce marker;
- add tests for Stop reconciliation with a fresh quiesce record, Codex
  `NEW -> GO` reciprocal dispatch within/after the quiesce window, and
  per-role/per-session separation.

## Positive Checks

- Project authorization exists and is active:
  `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH`.
- `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` includes `WI-3280`.
- Mandatory applicability preflight passed with no missing required specs.
- Mandatory ADR/DCL clause preflight passed with zero blocking gaps.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-cross-harness-trigger-index-edit-race-quiesce`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-cross-harness-trigger-index-edit-race-quiesce`
- `python -m groundtruth_kb deliberations search "WI-3280 cross harness trigger INDEX edit race quiesce" --limit 5`
- `python -m groundtruth_kb deliberations search "Cross-Harness Trigger Windows Rename Race liveness diagnostics" --limit 5`
- `python -m groundtruth_kb deliberations get DELIB-1877`
- `python -m groundtruth_kb deliberations get DELIB-1497`
- `python -m groundtruth_kb projects show PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`
- `python -m groundtruth_kb projects authorizations PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`
- Source inspection of `scripts/cross_harness_bridge_trigger.py`,
  `.claude/settings.json`, `.codex/hooks.json`, `pyproject.toml`,
  `.github/workflows/groundtruth-kb-tests.yml`, and `platform_tests/scripts/`

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
