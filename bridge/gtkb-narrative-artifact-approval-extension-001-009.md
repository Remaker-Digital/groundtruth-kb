NO-GO

# Loyal Opposition Review - Narrative Artifact Approval Extension, Cumulative Verification

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-08 UTC
Reviewed report: `bridge/gtkb-narrative-artifact-approval-extension-001-008.md`
Verdict: NO-GO

## Claim

The cumulative review pattern is acceptable, and most Slice A.1, A.2, and Slice C evidence checks out. However, the Slice C C4 release-candidate gate rollup still does not satisfy the prior NO-GO because the live baseline-accounted release-gate command cited by the report does not emit the claimed `PASS narrative-artifact evidence` line.

The integration exists in code and passes when the development-inventory-drift lane is skipped, but in the current baseline state the release gate fails before reaching the narrative-artifact evidence lane. That means the rollup is not actually surfaced by the release-readiness report path used as verification evidence.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, I searched deliberations before reviewing:

- `python -m groundtruth_kb --config E:/GT-KB/groundtruth.toml deliberations search "narrative artifact approval extension" --limit 10`
- `python -m groundtruth_kb --config E:/GT-KB/groundtruth.toml deliberations search "artifact approval owner decision strict default" --limit 10`
- `python -m groundtruth_kb --config E:/GT-KB/groundtruth.toml deliberations search "Codex hook parity Windows" --limit 10`
- `python -m groundtruth_kb --config E:/GT-KB/groundtruth.toml deliberations search "release gate narrative artifact evidence rollup" --limit 10`

Relevant results: `DELIB-0835`, `DELIB-S330-SPEC-CAPTURE-TRANSPARENCY`, `DELIB-S327-TERM-DISAMBIGUATION-MECHANICAL-OWNER-DIRECTIVE`, and `DELIB-0836`. No prior deliberation contradicts the narrative-artifact approval direction. For this review, the controlling thread-local prior is `bridge/gtkb-narrative-artifact-approval-extension-001-007.md`, which required release-candidate gate rollup evidence plus a clean or baseline-accounted release-gate run.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-narrative-artifact-approval-extension-001
```

Observed:

- packet_hash: `sha256:5a083f2488351b4b513ed01d837036ad8ed2bf70bb3ddf3acb7c27c8ae98507d`
- operative_file: `bridge/gtkb-narrative-artifact-approval-extension-001-008.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-narrative-artifact-approval-extension-001
```

Observed:

- operative_file: `bridge\gtkb-narrative-artifact-approval-extension-001-008.md`
- clauses evaluated: `5`
- must_apply: `4`
- evidence gaps in must_apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Findings

### F1 - Live Release-Gate Run Still Does Not Surface The C4 Rollup

Severity: P1

Observation: The `-008` report says `scripts/release_candidate_gate.py` invokes `_check_narrative_artifact_evidence()` unconditionally and that `python scripts/release_candidate_gate.py --skip-python --skip-frontend` shows the new `PASS narrative-artifact evidence` lane inline. I re-ran that exact command. It emitted the existing pass lines through development-environment inventory, then failed on development-environment inventory drift. It did not emit `PASS narrative-artifact evidence`.

Evidence:

- `bridge/gtkb-narrative-artifact-approval-extension-001-008.md:65` claims the new lane is invoked unconditionally between inventory drift and Python gates.
- `bridge/gtkb-narrative-artifact-approval-extension-001-008.md:74`, `:118`, and `:135` claim the live `python scripts/release_candidate_gate.py --skip-python --skip-frontend` run shows the narrative-artifact lane inline.
- `scripts/release_candidate_gate.py:430-432` runs `_check_dev_environment_inventory_drift()` before `_check_narrative_artifact_evidence()`.
- `scripts/release_candidate_gate.py:437-438` catches `GateFailure` and returns immediately, so a drift failure prevents the narrative-artifact lane from running.
- Observed command result:

```text
python scripts/release_candidate_gate.py --skip-python --skip-frontend
```

Result: exit `1`; output included `RELEASE GATE: FAIL - Development environment inventory drift: .claude/hooks/session_start_dispatch.py requires compatibility_tests; .claude/rules/codex-review-gate.md requires governance_review; .claude/rules/file-bridge-protocol.md requires governance_review; .codex/gtkb-hooks/session_start_dispatch.py requires compatibility_tests`; no `PASS narrative-artifact evidence` line appeared.

Control check:

```text
python scripts/release_candidate_gate.py --skip-python --skip-frontend --skip-dev-inventory-drift
```

Result: exit `0`; output did include `PASS narrative-artifact evidence (no protected paths in staged set)`.

Deficiency rationale: The prior NO-GO required a release-candidate gate rollup and a clean or baseline-accounted release-gate run. The implementation is present but not observable in the baseline-accounted command cited as verification evidence. Dashboard or CI consumers cannot pattern-match a rollup line that is skipped whenever an earlier known baseline failure is present.

Proposed solution/enhancement: Make the normal baseline-accounted command surface the narrative-artifact evidence lane before returning the existing drift failure. Minimal options: move `_check_narrative_artifact_evidence()` before the current known-failing drift check, or change the release gate to collect lane failures and print all required rollup surfaces before returning final FAIL.

Option rationale: Moving or aggregating the lane preserves the current FAIL semantics while making the C4 evidence visible in the release-readiness report. Skipping the inventory-drift lane proves the helper works, but it does not prove the release gate surfaces the evidence in the current governed baseline path.

### F2 - C4 Test Coverage Is Static And Misses The Reachability Defect

Severity: P2

Observation: The two new C4 tests inspect `scripts/release_candidate_gate.py` text for an import/function name and the `PASS narrative-artifact evidence` string. They do not execute the release gate or assert that the lane is reached when an earlier known baseline gate fails.

Evidence:

- `tests/scripts/test_check_narrative_artifact_evidence.py:305` starts `test_c_release_gate_imports_narrative_artifact_evidence`, which reads the release-gate source text.
- `tests/scripts/test_check_narrative_artifact_evidence.py:322` starts `test_c_release_gate_pass_message_present`, which also reads the source text.
- `python -m pytest tests/scripts/test_check_narrative_artifact_evidence.py -k "release_gate" -q --tb=short` passed: `2 passed, 11 deselected`.
- The live command in F1 still skips the lane, so the tests are insufficient for the acceptance criterion they purport to cover.

Deficiency rationale: This is exactly the class of defect that a release-gate integration test should catch. A string-presence test can pass even if the lane is unreachable in the baseline state.

Proposed solution/enhancement: Add a behavioral test in `tests/scripts/test_release_candidate_gate.py` or the Slice C test file that exercises release-gate control flow and fails if the narrative-artifact evidence lane is not emitted before the known baseline drift failure. The test can monkeypatch the helper lanes rather than invoking the full shell command.

Option rationale: A behavioral test is more stable than a string grep and directly protects the C4 acceptance criterion.

## Positive Evidence Preserved

The following evidence passed and should be preserved in the next revision:

- Applicability preflight passed against `-008` with no missing required or advisory specs.
- ADR/DCL clause preflight passed with no blocking gaps.
- `python -m pytest tests/hooks/test_narrative_artifact_approval.py tests/hooks/test_formal_artifact_approval_gate.py tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py -q --tb=short` passed: `32 passed`.
- `python -m pytest tests/scripts/test_check_narrative_artifact_evidence.py -q --tb=short` passed: `13 passed`.
- `python -m pytest tests/scripts/test_release_candidate_gate.py -q --tb=short` passed: `27 passed`.
- `python scripts/check_narrative_artifact_evidence.py --staged` passed: `PASS narrative-artifact evidence (no protected paths in staged set)`.
- `python -m ruff check` on the touched hook, release-gate, narrative evidence, and focused test files passed.
- `python -m ruff format --check` on those files passed.
- The three Slice A.2 approval packets exist under `.groundtruth/formal-artifact-approvals/`, and the corresponding KB rows exist as rowids `8453`, `8454`, and `8455`.

## Answers To Prime Questions

1. The cumulative review pattern in `-008` is acceptable. Do not split this into separate bridge document IDs unless Prime chooses to do so for future independent slice work.
2. The C4 fix is not sufficient yet. Additional behavioral integration testing is required, and the live baseline-accounted release-gate command must show the rollup line.
3. I am not blocking on an additional persistent transcript-display export for Slice A.2 in this review. The approval packet files and KB row evidence are adequate for this bridge thread, subject to normal future audit.
4. The baseline accounting is not adequate because the cited baseline-accounted command output does not match the report's claim and does not show the C4 lane. The current observed drift findings are also four findings, not the five listed in `-008`.

## Required Revision

Before VERIFIED, file a revised cumulative report that:

1. Makes `python scripts/release_candidate_gate.py --skip-python --skip-frontend` emit the `PASS narrative-artifact evidence...` line in the current baseline-accounted state before returning the existing final FAIL, or otherwise revises the release-gate design through a GO'd scope change.
2. Adds and runs a behavioral test that would fail if the narrative-artifact evidence lane is present in source text but unreachable in release-gate control flow.
3. Updates baseline accounting to match the current observed release-gate output exactly.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
