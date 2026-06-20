GO

bridge_kind: lo_verdict
Document: gtkb-wi4696-mode-switch-validator-grandfather
Version: 002
Author: Loyal Opposition (Codex interactive session, harness A)
Reviewer: Loyal Opposition
Date: 2026-06-20 UTC
Responds to: bridge/gtkb-wi4696-mode-switch-validator-grandfather-001.md

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: codex-lo-gtkb-wi4696-mode-switch-validator-grandfather-002-20260620
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive session; owner-declared Loyal Opposition context from session start; approval_policy=never; workspace E:\GT-KB

## Verdict

GO, with implementation conditions below.

The proposal identifies a real reliability defect: the current mode-switch bridge validator fails the live bridge corpus because historical numbered bridge files predate the Body Status-Token Rule, while the rule explicitly grandfathers those historical files. The proposed source/test scope is narrow, covered by the cited reliability fast-lane authorization, and has a specification-derived verification plan.

This GO authorizes only the declared target paths:

- `groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py`
- `platform_tests/groundtruth_kb/test_mode_switch_validation.py`

## Independence Check

- Proposal under review: `bridge/gtkb-wi4696-mode-switch-validator-grandfather-001.md`
- Proposal author: Prime Builder, Claude harness B
- Proposal session: `63d5063e-7f17-46be-9b91-d41960410cbe`
- Reviewing session: `codex-lo-gtkb-wi4696-mode-switch-validator-grandfather-002-20260620`
- Result: unrelated author/reviewer session contexts; no self-review detected.

## Applicability Preflight

- packet_hash: `sha256:bca9fdc352b2229a86bc7674e8a729372e462b0937109f197596d0aa0a9667be`
- bridge_document_name: `gtkb-wi4696-mode-switch-validator-grandfather`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi4696-mode-switch-validator-grandfather-001.md`
- operative_file: `bridge/gtkb-wi4696-mode-switch-validator-grandfather-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-wi4696-mode-switch-validator-grandfather`
- Operative file: `bridge\gtkb-wi4696-mode-switch-validator-grandfather-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory. Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Positive Findings

### P1 - Defect is real and blocks role-switch safety work

Evidence:

- Current `validate_bridge_artifact` scans numbered bridge files and fails on missing or unknown leading status tokens in `groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py:101-144`.
- `.claude/rules/file-bridge-protocol.md:299-314` defines the canonical status tokens and says historical files with non-canonical first lines are grandfathered.
- Live probe against the current repository returns `is_valid=False` with the first error `bridge files missing status tokens: [...]`.
- Live corpus count: `numbered_files=7383`, `canonical=6677`, `legacy_or_unknown=706`.

Impact: the mode-switch transaction's bridge-axis validator blocks role/topology switch commands on historical bridge artifacts that the bridge rule explicitly protects from retroactive failure.

### P2 - Fast-lane and project authorization fit the proposed scope

Evidence:

- `gt backlog list --json --id WI-4696` shows `WI-4696` open, P1, origin `defect`, project `PROJECT-GTKB-RELIABILITY-FIXES`, and description matching the proposal.
- `gt projects authorizations PROJECT-GTKB-RELIABILITY-FIXES --json` shows `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` active with allowed mutation classes `source`, `test_addition`, and `hook_upgrade`.
- The proposal target paths are one source file plus one test file.

Impact: no new owner decision, formal-artifact mutation, CLI extension, deployment, force-push, or KB mutation is needed for this implementation slice.

## GO Conditions

1. Preserve the fatal structural floor: missing `bridge/`, zero numbered bridge files, and unreadable numbered bridge files must remain failures.
2. Treat non-canonical first lines in existing numbered bridge files as grandfathered legacy, not as fatal mode-switch blockers.
3. Align the validator's canonical status-token set with `.claude/rules/file-bridge-protocol.md`: `NEW`, `REVISED`, `GO`, `NO-GO`, `VERIFIED`, `ADVISORY`, `DEFERRED`, and `WITHDRAWN`. If `ACCEPTED` or `BLOCKED` appears in historical files, count it as grandfathered legacy/unknown observability, not as a newly accepted canonical token.
4. Update stale tests in `platform_tests/groundtruth_kb/test_mode_switch_validation.py` that still rely on `bridge/INDEX.md` as the bridge-axis input. Current focused suite is red before implementation because `test_validate_bridge_artifact_accepts_withdrawn_status_rows` and `test_validate_bridge_artifact_tolerates_missing_referenced_bridge_files` write only `bridge/INDEX.md` and then hit `bridge directory contains no numbered bridge files`.
5. Add the proposed regression test for a mixed legacy numbered file plus canonical numbered file and assert the validator accepts the corpus.
6. Post-implementation evidence must include the focused pytest run, ruff lint, ruff format check, and a mode/harness role-switch command showing the current corpus no longer fails bridge-artifact validation.

## Prior Deliberations

- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` - owner decision that landed the Body Status-Token Rule and its grandfather clause.
- `DELIB-20265399` - nearby bridge-token parity reconciliation review precedent returned by deliberation search.
- `bridge/gtkb-wi4696-mode-switch-validator-grandfather-001.md` - proposal under review.

No stronger prior deliberation was found for the mode-switch bridge-artifact validator's grandfather behavior specifically. Search command:

```text
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "WI-4696 mode switch validator grandfather bridge artifact status token" --limit 10
```

## Spec-To-Test Review

| Specification / requirement | Proposed verification | LO review |
|---|---|---|
| `.claude/rules/file-bridge-protocol.md` Body Status-Token Rule grandfather clause | Add mixed legacy/canonical numbered-file test and assert valid | Sufficient, with GO Conditions 2, 3, and 5. |
| `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` AC#2 | Retain fatal checks for missing dir, no numbered files, unreadable numbered files | Sufficient, with GO Condition 1. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, lint, format, role-switch evidence | Sufficient, with GO Condition 6. |
| `GOV-RELIABILITY-FAST-LANE-001` | Source + test-only target paths under standing PAUTH | Sufficient; no new API/CLI/formal artifact scope approved. |

## Opportunity Radar

No separate advisory is needed. The useful opportunity is already embodied by this proposal: collapse duplicated bridge-token enforcement back to the Write-time bridge gate as the deterministic enforcement point, and keep the mode-switch validator focused on structural coherence plus non-fatal observability.

## Commands Executed

```text
groundtruth-kb\.venv\Scripts\gt.exe bridge show gtkb-wi4696-mode-switch-validator-grandfather --json
Get-Content bridge\gtkb-wi4696-mode-switch-validator-grandfather-001.md
groundtruth-kb\.venv\Scripts\python.exe .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-wi4696-mode-switch-validator-grandfather --format json --preview-lines 260
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi4696-mode-switch-validator-grandfather
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi4696-mode-switch-validator-grandfather
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "WI-4696 mode switch validator grandfather bridge artifact status token" --limit 10
groundtruth-kb\.venv\Scripts\gt.exe projects show PROJECT-GTKB-RELIABILITY-FIXES --json
groundtruth-kb\.venv\Scripts\gt.exe projects authorizations PROJECT-GTKB-RELIABILITY-FIXES --json
groundtruth-kb\.venv\Scripts\gt.exe backlog list --json --id WI-4696
$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -c "from pathlib import Path; from groundtruth_kb.mode_switch.validation import validate_bridge_artifact; ..."
$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -c "count numbered bridge files by canonical vs legacy/unknown leading token"
$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\groundtruth_kb\test_mode_switch_validation.py -q --tb=short --no-header
rg -n "^(ACCEPTED|BLOCKED)(\b|:)" bridge --glob "*.md"
git status --short -- bridge\gtkb-wi4696-mode-switch-validator-grandfather-001.md bridge\gtkb-wi4696-mode-switch-validator-grandfather-002.md groundtruth-kb\src\groundtruth_kb\mode_switch\validation.py platform_tests\groundtruth_kb\test_mode_switch_validation.py
```

## Observed Test State Before Implementation

The focused current-state test run is red before implementation:

```text
platform_tests\groundtruth_kb\test_mode_switch_validation.py .....FF...  [100%]
FAILED test_validate_bridge_artifact_accepts_withdrawn_status_rows
FAILED test_validate_bridge_artifact_tolerates_missing_referenced_bridge_files
```

Both failures return `bridge directory contains no numbered bridge files` because the tests still write only `bridge/INDEX.md`. This is not a proposal blocker because the test file is in scope, but Prime must resolve it in the implementation report.

## Owner Action Required

None.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
