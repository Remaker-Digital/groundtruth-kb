NEW

# GT-KB Bridge Implementation Report - gtkb-doctor-legacy-root-pattern-catalog-false-positive - 003

bridge_kind: implementation_report
Document: gtkb-doctor-legacy-root-pattern-catalog-false-positive
Version: 003 (NEW; post-implementation report)
Date: 2026-06-19 UTC
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-19T03-36-32Z-prime-builder-A-e950c0
author_model: Codex
author_model_version: GPT-5
author_model_configuration: bridge auto-dispatch; approval_policy=never; sandbox=workspace-write
Responds to GO: bridge/gtkb-doctor-legacy-root-pattern-catalog-false-positive-002.md
Approved proposal: bridge/gtkb-doctor-legacy-root-pattern-catalog-false-positive-001.md
Implementation authorization packet: `sha256:adec7ec9a9ae1493c19ce85e6c1a03af864677665ba4dec757b682e68ee91e4c`
Recommended commit type: fix:

## Implementation Claim

Implemented the approved narrow false-positive fix for `_check_active_legacy_root_references`.

`groundtruth-kb/src/groundtruth_kb/project/doctor.py` now treats the governed hygiene sweep pattern catalog file name, `hygiene-sweep-patterns.toml`, as a detector-definition surface rather than a live dependency surface. Existing detector script allowances and context-based allowances remain unchanged.

`groundtruth-kb/tests/test_doctor_legacy_root.py` now includes a regression test proving the catalog's `claude-playground` pattern block is allowed while the existing live-reference fail-case tests continue to assert hard-fail behavior for genuine live references.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` - Governs this fast-lane defect fix for WI-4627.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - The approved proposal and this report preserve concrete specification linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Verification maps each linked governing surface to executed tests or command evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - The approved proposal carries `Project Authorization`, `Project`, and `Work Item` metadata for PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING / PROJECT-GTKB-RELIABILITY-FIXES / WI-4627.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Implementation proceeded only after the live latest `GO` and implementation-start authorization packet.
- `GOV-STANDING-BACKLOG-001` - WI-4627 is the standing-backlog work item implemented by this bridge thread.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The fix is preserved as a work item, bridge proposal, test, implementation report, and verification request.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The implementation keeps the durable artifact trail intact.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The doctor-surface fix followed the required lifecycle trigger path.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - The hard-fail isolation boundary remains enforced for genuine live references; only the detector catalog is exempted.
- `SPEC-AUQ-POLICY-ENGINE-001` - Owner authorization derives from the carried-forward AUQ evidence and standing fast-lane authorization; this implementation does not change AUQ behavior.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - No hook behavior was changed.

## Owner Decisions / Input

- `DECISION-1272` (S445 AskUserQuestion, owner answer "Yes") authorized fixing the trivial legacy-root reference. The approved proposal cites this as recorded in `memory/pending-owner-decisions.md`.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` remains active and covers this fast-lane defect work through active membership in `PROJECT-GTKB-RELIABILITY-FIXES`.

## Prior Deliberations

- `DELIB-20260602-GLOSSARY-CLI-SCAN-LEGACY-ROOT-HARD-FAIL` - Owner selected hard-fail doctor behavior for active artifacts treating the retired archive root as live. This implementation preserves that hard-fail path.
- `DELIB-20263459` - Hygiene Sweep Scope Regression 2026-06-12.
- `DELIB-20263489` - Loyal Opposition Hygiene Assessment - Advisory Report (2026-06-15).
- `bridge/gtkb-doctor-legacy-root-pattern-catalog-false-positive-001.md` - Approved implementation proposal carried forward.
- `bridge/gtkb-doctor-legacy-root-pattern-catalog-false-positive-002.md` - Loyal Opposition `GO` verdict authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-RELIABILITY-FAST-LANE-001` | Scoped target diff is limited to `doctor.py` and `test_doctor_legacy_root.py`; `git diff --stat -- <targets>` reports 2 files changed, 29 insertions. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward all approved proposal links above. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest` regression run passed 6 tests; the same run covers the new allow-case and existing fail-case tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Implementation-start packet succeeded and returned active PAUTH metadata for `WI-4627`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `implementation_authorization.py begin --bridge-id gtkb-doctor-legacy-root-pattern-catalog-false-positive` returned latest status `GO` and packet hash `sha256:adec7ec9a9ae1493c19ce85e6c1a03af864677665ba4dec757b682e68ee91e4c`. |
| `GOV-STANDING-BACKLOG-001` | Scope remains tied to `WI-4627`; no backlog mutation was required. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | This implementation report is filed as the next bridge audit artifact for Loyal Opposition verification. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Test and bridge evidence are durable artifacts; no transient-only claim is used. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Work followed proposal -> GO -> implementation -> report. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Existing hard-fail tests still pass; live doctor output now reports the active legacy-root control surface as `[OK]`. |
| `SPEC-AUQ-POLICY-ENGINE-001` | No AUQ code, policy-engine code, or owner-decision capture behavior changed. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | No Codex/Claude hook files were changed by this implementation. |

## Commands Run

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_doctor_legacy_root.py -q`
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_doctor_legacy_root.py -q --basetemp E:\GT-KB\.gtkb-tmp\pytest-doctor-legacy-root-20260619T0341` with pytest cache provider disabled to avoid cache writes during the retry.
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_legacy_root.py`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_legacy_root.py`
- `groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb project doctor`
- `groundtruth-kb/.venv/Scripts/gt.exe hygiene sweep`
- `groundtruth-kb/.venv/Scripts/gt.exe hygiene sweep --pattern-set claude-playground --output .gtkb-tmp\hygiene-sweep-claude-playground-20260619T0343 --format both --report-only`
- Inline `groundtruth_kb.hygiene.sweep.run_sweep(...)` API verification using the live `claude-playground` registry pattern against a temp fixture root.

## Observed Results

- Initial pytest attempt: `ERROR` during setup before test execution because the default Windows temp root denied access to `C:\Users\micha\AppData\Local\Temp\pytest-of-micha`.
- Pytest rerun with in-workspace basetemp: `6 passed in 0.43s`.
- Ruff lint: `All checks passed!`
- Ruff format: `2 files already formatted`.
- Live doctor: overall command exited `1` because of unrelated pre-existing findings, but the acceptance-relevant line now reports `[OK] No active control-surface references to <legacy-root>`. Remaining doctor failures included AUQ coverage, verified bridge Owner Decisions section debt, duplicate SoT artifact id, active dispatch target launchability, and standing backlog health.
- Full hygiene sweep command: timed out after 120 seconds.
- Single-pattern hygiene sweep command: timed out after 300 seconds.
- Scoped sweep API verification with the live `claude-playground` pattern: `patterns_loaded=1`, `files_scanned=1`, `finding_count=1`; the catalog fixture path was self-excluded, and a separate planted live-reference file was detected.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `groundtruth-kb/tests/test_doctor_legacy_root.py`

Unrelated dirty worktree files were already present in the shared checkout and are intentionally excluded from this implementation report.

## Target Diff Summary

```text
groundtruth-kb/src/groundtruth_kb/project/doctor.py        |  3 +++
groundtruth-kb/tests/test_doctor_legacy_root.py            | 26 ++++++++++++++++++++++
2 files changed, 29 insertions(+)
```

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: This repairs a doctor false positive without adding a new user-facing capability or changing public API surface.

## Acceptance Criteria Status

- [x] `_check_active_legacy_root_references` returns PASS for the `claude-playground` pattern catalog.
- [x] Existing genuine-live-reference fail-case tests still assert FAIL behavior.
- [x] The live doctor legacy-root control-surface check now reports `[OK]`; unrelated pre-existing doctor failures remain outside this bridge scope.
- [x] The live `claude-playground` sweep pattern still self-excludes the catalog path and detects a separate planted live reference in scoped API verification.
- [x] `ruff check` and `ruff format --check` are clean on both changed files.

## Risk And Rollback

Residual risk is limited to the full-workspace `gt hygiene sweep` runtime: both the full sweep and single-pattern CLI sweep exceeded this dispatch's time budget, so the sweep evidence is API-scoped rather than full-workspace CLI-scoped. The scoped API check uses the live pattern registry and proves the behavior the approved proposal needed from the `claude-playground` pattern.

Rollback is file-local: revert `groundtruth-kb/src/groundtruth_kb/project/doctor.py` and `groundtruth-kb/tests/test_doctor_legacy_root.py`. No schema, data, MemBase, or runtime-state migration is involved.

## Loyal Opposition Asks

1. Verify the implementation against the approved proposal, linked specifications, target diff, and command evidence.
2. Return `VERIFIED` if the scoped implementation satisfies the bridge proposal; otherwise return `NO-GO` with findings.
