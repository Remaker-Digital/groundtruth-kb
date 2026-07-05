NEW

# Implementation Report - WI-5015 Duplicate-SoT Doctor Guard

bridge_kind: implementation_report
Document: gtkb-sot-singleton-doctor-guard
Version: 003 (NEW; post-implementation report)
Date: 2026-07-05T06:32:00Z
Responds to GO: bridge/gtkb-sot-singleton-doctor-guard-002.md
Approved proposal: bridge/gtkb-sot-singleton-doctor-guard-001.md
Recommended commit type: feat

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f23f0-b16e-7481-8a18-9622ab564d50
author_model: GPT-5 via Codex Desktop
author_model_version: current Codex Desktop runtime
author_model_configuration: interactive Prime Builder session; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS-UMBRELLA
Project: PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS
Work Item: WI-5015

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/project/sot_audit.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_sot_duplicate_audit.py", "platform_tests/scripts/test_check_sot_duplicate_guard.py", "platform_tests/scripts/test_check_sot_registry_completeness.py", ".gtkb-state/sot-singleton-audit", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX"]

## Implementation Claim

Prime Builder implemented `WI-5015` by adding a duplicate-SoT drift-prevention doctor check that reuses the verified WI-5014 audit engine instead of adding a second scanner.

The implemented check:

- Adds `_check_sot_duplicate_guard(target)` in `groundtruth-kb/src/groundtruth_kb/project/doctor.py`.
- Calls `groundtruth_kb.project.sot_audit.run_duplicate_sot_audit(target)`.
- Fails when the audit baseline is unavailable or coverage is incomplete.
- Fails when duplicate-SoT violations are uncovered by remediation work.
- Warns, rather than passing green, for known covered/delegated violations such as `duplicate-dispatch-harness-fields->WI-5012(existing_covering_work_item)`.
- Passes only when coverage is complete and no duplicate-SoT violations exist.
- Wires the check into `run_doctor()` immediately after the existing SoT registry completeness and read-discipline checks.
- Adds `platform_tests/scripts/test_check_sot_duplicate_guard.py` covering pass, unavailable baseline, permitted derived cache, invalid derived cache failure, WI-5012 covered-warning behavior, and doctor wiring.

No changes were made to `groundtruth-kb/src/groundtruth_kb/project/sot_audit.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`, or `groundtruth-kb/tests/test_sot_duplicate_audit.py`; those WI-5014 artifacts are treated as verified dependencies.

## Implementation-Start Evidence

- Work-intent claim: `python scripts/bridge_claim_cli.py claim gtkb-sot-singleton-doctor-guard`
- Observed claim: `claim_kind=go_implementation`, `acting_role=prime-builder`, `rowid=30002`, `ttl_expires_at=2026-07-05T07:07:01Z`.
- Implementation authorization: `python scripts/implementation_authorization.py begin --bridge-id gtkb-sot-singleton-doctor-guard`
- Observed packet hash: `sha256:c1bedfb21d2ae61de96d7f0157622763dad4307d8a0c8bca545988519808afd8`
- Latest bridge status at authorization time: `GO`
- GO file: `bridge/gtkb-sot-singleton-doctor-guard-002.md`
- Proposal file: `bridge/gtkb-sot-singleton-doctor-guard-001.md`

Preconditions were satisfied before implementation:

- `WI-5013` latest bridge status was `VERIFIED`; MemBase work item was resolved.
- `WI-5014` latest bridge status was `VERIFIED`; MemBase work item was resolved by the bridge-verified backlog reconciler.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `platform_tests/scripts/test_check_sot_duplicate_guard.py`

## Architecture Alignment Ledger

- OPS consolidation alignment: the guard reduces owner burden by turning duplicate-SoT drift into deterministic doctor evidence instead of recurring manual inspection.
- Dispatcher daemon architecture alignment: the guard leaves dispatch routing unchanged and reports the known dispatcher duplicate-field cluster as covered by `WI-5012`, preserving that lane for dispatch-specific remediation.
- Lifecycle-first/scoring-last precedence: the guard classifies lifecycle authority and remediation coverage before treating any duplicate as an optimization/scoring concern.
- Portfolio reconciliation alignment: the implementation is scoped to the WI-5015 doctor/prevention lane and does not remediate WI-5012 or the P2 audit lanes directly.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-PLATFORM-SOT-REGISTRY-001`
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`
- `DCL-SOT-READ-HOOK-CONTRACT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Owner Decisions / Input

No new owner decision was required for this implementation report.

Carried-forward owner/project authority:

- `DELIB-202665441`: owner selected registry-governed authoritative homes and strict derived-cache semantics.
- `DELIB-202665444`: owner selected registry-plus-closure whole-system audit coverage.
- `DELIB-202665455`: owner selected risk-first incremental remediation with one violation class per child/remediation work item.
- `PAUTH-PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS-UMBRELLA`: active umbrella authorization for WI-5015.

## Spec-Derived Verification

| Specification | Verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Latest thread status was `GO`; work-intent claim and implementation authorization packet were created before protected edits. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Report carries project authorization, project, work item, and parseable `target_paths`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-sot-singleton-doctor-guard --json` passed with `missing_required_specs=[]` and `missing_advisory_specs=[]`; packet hash `sha256:6221be575e02272c5cba96cbcecead158068fade6cba4da1646905f36ebf0ec1`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This report maps linked specifications to executed commands and observed results. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Tests prove invalid/stale cache-shaped duplicates fail and permitted machine-checkable derived caches pass. |
| `GOV-PLATFORM-SOT-REGISTRY-001`, `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | Guard uses the WI-5014 typed audit engine, which starts from the platform SoT registry. |
| `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` | Test proves the dispatcher/harness duplicate field cluster is not silently green and remains delegated to `WI-5012`. |
| `DCL-SOT-READ-HOOK-CONTRACT-001` | Existing `_check_sot_read_discipline` remains wired; regression suite includes its focused tests. |
| `GOV-STANDING-BACKLOG-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Guard messages include candidate ids, paths, fields, and remediation work-item linkage for follow-on work. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All changed files are under `E:\GT-KB` and within the GO target paths. |

## Verification Commands and Observed Results

Command:

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_check_sot_duplicate_guard.py
```

Observed: exit `0`; `All checks passed!`

Command:

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_check_sot_duplicate_guard.py
```

Observed: exit `0`; `2 files already formatted`

Command:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb/tests/test_sot_duplicate_audit.py platform_tests/scripts/test_check_sot_duplicate_guard.py platform_tests/scripts/test_check_sot_registry_completeness.py platform_tests/scripts/test_check_sot_read_discipline.py -q --tb=short
```

Observed: exit `0`; `29 passed, 1 warning in 0.84s`

Command:

```text
gt project doctor --json
```

Observed: exit `1` because the full checkout still has unrelated pre-existing doctor failures. The new WI-5015 check produced the intended non-green delegated-violation signal:

```json
{
  "name": "SoT duplicate guard",
  "status": "warning",
  "required": false,
  "message": "1 duplicate-SoT violation(s) covered by remediation work: duplicate-dispatch-harness-fields->WI-5012(existing_covering_work_item)"
}
```

Unrelated existing full-doctor failures observed include `Uncited owner-input bridges`, `Cross-harness parity discovery-diff`, `External harness exec boundary`, `Dispatcher config CLI-only guard`, Agent Red application-slot checks, and prior-session ORIENT block. These are outside the WI-5015 target scope.

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-sot-singleton-doctor-guard
```

Observed: exit `0`; `Blocking gaps (gate-failing): 0`.

## Risk / Rollback

Primary residual risk is false-positive pressure from a strict guard. The implementation reduces that risk by warning, not failing, when a violation is already covered by an explicit remediation work item. Rollback is a normal source/test revert for `doctor.py` and `platform_tests/scripts/test_check_sot_duplicate_guard.py`; no KB, registry, CLI, or audit-engine state was changed.

## Acceptance Status

Ready for Loyal Opposition verification.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
