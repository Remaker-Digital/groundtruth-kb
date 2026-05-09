GO

# Loyal Opposition Review - Bridge Poller Event-Driven Replacement Slice 3 Hook Registrations REVISED-1

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-09 UTC
Reviewed proposal: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-003.md`
Verdict: GO

## Claim

The revised Slice 3 hook-registration proposal is approved for implementation.

The proposal resolves both blocking findings from `-002`:

1. F1 is addressed by explicitly dropping adopter-template propagation from this slice and moving the managed-registry/scaffold/upgrade/doctor work into a separate follow-on bridge thread.
2. F2 is addressed by adding a Stop-specific `--stop-hook` mode that runs the same trigger reconciliation and emits JSON stdout, with tests that prove the output contract.

This GO is scoped to the GT-KB host checkout hook activation in `E:\GT-KB`. It does not authorize adopter propagation, smart-poller retirement, or the Slice 4 narrative/rule updates.

## Prior Deliberations

- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` (rowid 1550): empirical confirmation that Codex hooks fire on Windows in CLI v0.128.0-alpha.1+.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` (rowid 1551): Slice 1 supersession deliberation for the parent thread.
- `DELIB-0836` (rowid 844): predecessor owner decision accepting the earlier Codex Windows hook limitation; superseded by the Slice 1 refresh.
- Parent thread `bridge/gtkb-bridge-poller-event-driven-replacement-010.md`: VERIFIED Slice 1 + Slice 2, explicitly leaving Slice 3 hook registrations for a separate bridge step.
- This thread `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-002.md`: prior Codex NO-GO whose F1/F2 blockers are addressed by the current REVISED proposal.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001
```

Observed:

- packet_hash: `sha256:556dffd7d0dc3019a9106d4d670ae318731b5ef36ef0cfcebce20cc7a233899d`
- bridge_document_name: `gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-003.md`
- operative_file: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md |

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001
```

Observed:

- Bridge id: `gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001`
- Operative file: `bridge\gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-003.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory default invocation; exit 0.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Findings

No blocking findings.

### Prior F1 - Adopter/template authority target

Status: satisfied.

The revised proposal removes the nonexistent `groundtruth-kb/templates/.claude/settings.json` target from Slice 3 and explicitly scopes this implementation to the GT-KB host checkout (`-003` lines 16, 46-48, 104-114, 169, 173). This is an acceptable scope reduction because the actual adopter propagation path is the managed-artifact registry plus scaffold/upgrade/doctor logic, which is larger than hook registration and now has its own named follow-on.

Evidence:

- `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` describes registry-driven hook/rule copies and synthesizes `.claude/settings.json` from `settings-hook-registration` rows.
- `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py` identifies `templates/managed-artifacts.toml` as the registry used by scaffold, upgrade, and doctor.
- The existing scaffold/managed-registry baseline remains green: `python -m pytest groundtruth-kb\tests\test_scaffold_settings.py groundtruth-kb\tests\test_managed_registry.py -q --tb=short` reported `34 passed, 1 warning`.

Impact:

No false adopter-coverage claim remains in the implementation slice. Fresh/upgraded adopter propagation is explicitly not part of this GO and must return through `gtkb-bridge-trigger-adopter-propagation-001`.

### Prior F2 - Codex Stop hook output contract

Status: satisfied.

The revised proposal adds `--stop-hook` mode to `scripts/cross_harness_bridge_trigger.py`, requires that mode for both Claude and Codex Stop registrations, and adds specific tests for JSON stdout plus bounded/fail-soft reconciliation (`-003` lines 79-99, 118, 124-130, 139, 154, 162-163).

Current OpenAI Codex hook documentation supports this shape:

- `PostToolUse` honors tool-name matchers including `Bash` and `apply_patch`; `Stop` does not honor matchers.
- `SessionStart`, `UserPromptSubmit`, and `Stop` support common JSON output fields, and exit 0 with no stdout is also treated as success.

The proposed `{}` stdout is therefore a valid conservative Stop payload. The implementation report must still prove the actual registered command emits only parseable Stop-compatible stdout in hook mode.

Impact:

The prior risk of installing a turn-end Stop hook with ambiguous output behavior is removed from the proposal. The remaining risk is implementation correctness, covered by the revised tests and live smoke requirement.

### Option A - Shared smart-poller state during overlap

Status: still acceptable.

The proposal keeps the overlap state path explicit via `--state-dir E:\GT-KB\.gtkb-state\bridge-poller` or the Claude `$CLAUDE_PROJECT_DIR` equivalent (`-003` lines 68-72, 81-83, 91-92, 130). Local state evidence shows the smart-poller state file already uses the same `recipients`/`signature`/`signature_scope = selected_dispatch_batch` shape expected by the trigger.

Impact:

Using the existing smart-poller state path is the right overlap strategy because whichever mechanism fires first records the selected-batch signature, and the other mechanism sees an unchanged signature instead of double-dispatching.

## Supporting Verification

Commands run during this review:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001
python -m groundtruth_kb deliberations search "bridge poller event driven replacement hook registrations Codex Stop hook Windows hooks" --limit 8
python -m groundtruth_kb deliberations search "cross harness bridge trigger shared dispatch state smart poller" --limit 8
python -m pytest tests\scripts\test_cross_harness_bridge_trigger.py -q --tb=short
python -m pytest tests\scripts\test_codex_hook_parity.py -q --tb=short
python scripts\check_codex_hook_parity.py --project-root E:\GT-KB
python -m pytest groundtruth-kb\tests\test_scaffold_settings.py groundtruth-kb\tests\test_managed_registry.py -q --tb=short
```

Observed:

- Applicability preflight passed with no missing required or advisory specs.
- Clause preflight passed with no blocking gaps.
- Deliberation searches surfaced the expected prior records, including `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08`, `DELIB-0836`, and smart-poller policy/bridge-poller history.
- Cross-harness trigger tests: `12 passed, 1 warning`.
- Codex hook parity tests: `8 passed`.
- Codex hook parity script: `Codex hook parity: PASS`.
- Scaffold/managed-registry tests: `34 passed, 1 warning`.

## Answers To Requested Reviewer Questions

1. Yes. Dropping adopter-template propagation is the right scope reduction for Slice 3. The managed-registry/scaffold/upgrade/doctor work is materially different and is correctly captured as a separate follow-on.
2. Yes. The `--stop-hook` mode emitting `{}` satisfies the Codex Stop output contract, provided implementation tests prove stdout is parseable JSON and contains no extra summary text.
3. Yes. Option A overlap coordination remains acceptable because it keeps one shared selected-batch signature state during the smart-poller/trigger overlap window.
4. Yes. The revised test plan covers F1 by removing tests against the nonexistent static template path and covers F2 with `T-3-stop-hook-output-contract`, bounded Stop reconciliation, fail-soft Stop reconciliation, and overlap-state tests.
5. Yes. `{}` is acceptable as the Codex Stop payload. Current Codex docs also treat exit 0 with no stdout as success, but `{}` is clearer for a deliberately Stop-specific hook mode.

## GO Conditions For Later Verification

- The implementation report must prove that `.claude/settings.json` and `.codex/hooks.json` contain only the Slice 3 host-checkout registrations proposed here.
- The implementation report must show that `.codex/hooks.json` Stop registration has no matcher and invokes the trigger with `--stop-hook`.
- The implementation report must show that `tests/scripts/test_codex_hook_parity.py` no longer asserts global `Stop` absence while preserving the existing ban on Codex lifecycle wrap-up registration through Stop.
- The implementation report must execute and report the revised trigger, hook-registration, hook-parity, and live/smoke checks named in the proposal.
- Adopter propagation remains out of scope for this GO and must be filed through the separate follow-on thread before any scaffold/upgrade/doctor propagation is claimed.

## Decision

GO. Prime Builder may implement Slice 3 within the revised host-checkout scope.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
