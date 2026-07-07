NEW

# GT-KB Bridge Implementation Report - gtkb-wi5057-advisory-scanner-helper - 003

bridge_kind: implementation_report
Document: gtkb-wi5057-advisory-scanner-helper
Version: 003 (NEW; post-implementation report)
Author: Prime Builder (Codex)
Date: 2026-07-07T19:45:00Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3d79-c37d-7432-8c82-a66b675a389a
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; reasoning=xhigh; approval_policy=never

Responds to GO: bridge/gtkb-wi5057-advisory-scanner-helper-002.md
Approved proposal: bridge/gtkb-wi5057-advisory-scanner-helper-001.md
Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW-WI5057-ADVISORY-SCANNER-20260707
Project: PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW
Work Item: WI-5057
Recommended commit type: feat

## Implementation Claim

Implemented the WI-5057 live ADVISORY scanner/helper predicate needed by the advisory-intake workflow.

`scripts/advisory_backlog_router.py` now exposes `is_live_advisory(db, status_map, source_key)`, a deterministic helper that returns false when an advisory has already been promoted or rejected in the candidate store, and also returns false when the advisory already has a work-item row. Staged and absent-from-candidate-store advisories remain live.

`platform_tests/scripts/test_advisory_backlog_router.py` now covers the live predicate across staged, absent, promoted, rejected, and already-work-item-backed advisories. Existing `platform_tests/scripts/test_advisory_intake_scanner.py` coverage still proves the scanner selects only adopt/adapt ADVISORY entries with the Required Prime Builder Owner-Grilling Gate section and preserves deterministic summary/order fields.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`
- `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Owner Decisions / Input

No new owner decision was required. Owner approval is carried by `DELIB-202665870` and PAUTH `PAUTH-PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW-WI5057-ADVISORY-SCANNER-20260707`.

## Prior Deliberations

- `DELIB-202665870` - owner approved filing all six child implementation proposals for WI-5054 through WI-5059.
- `DELIB-202665486` - owner authorized the live ADVISORY scanner/summarizer helper child item.
- `bridge/gtkb-wi5057-advisory-scanner-helper-001.md` - approved implementation proposal.
- `bridge/gtkb-wi5057-advisory-scanner-helper-002.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Requirement | Executed verification evidence |
| --- | --- |
| `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` and `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` | Existing scanner tests prove only adopt/adapt advisories with the Required Prime Builder Owner-Grilling Gate section are intake-ready. |
| Live ADVISORY filtering | New router test proves promoted, rejected, and already-work-item-backed advisories are not live; staged and absent candidates remain live. |
| Deterministic summary/order | Existing scanner tests cover summary fields and presentation order. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Proposed WI-5057 test command passed and maps to `TEST-11295`. |
| Bridge/project authorization specs | Claim, applicability preflight, clause preflight, and implementation-start authorization all succeeded before report filing. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_claim_cli.py claim gtkb-wi5057-advisory-scanner-helper --ttl-seconds 7200`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5057-advisory-scanner-helper --json`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5057-advisory-scanner-helper`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi5057-advisory-scanner-helper --expires-minutes 120`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_advisory_backlog_router.py platform_tests/scripts/test_advisory_intake_scanner.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\ruff.exe check scripts/advisory_backlog_router.py scripts/advisory_intake_scanner.py platform_tests/scripts/test_advisory_backlog_router.py platform_tests/scripts/test_advisory_intake_scanner.py`
- `groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts/advisory_backlog_router.py scripts/advisory_intake_scanner.py platform_tests/scripts/test_advisory_backlog_router.py platform_tests/scripts/test_advisory_intake_scanner.py`

## Observed Results

- Work-intent claim acquired for session `019f3d79-c37d-7432-8c82-a66b675a389a`; implementation deadline `2026-07-07T20:13:30Z`, grace through `2026-07-07T20:23:30Z`.
- Applicability preflight passed with packet hash `sha256:f41e15940caee8e541d5ff0dcdc31c78e2d43bd6cd08316392d90c799f021e83`; no missing required or advisory specs.
- ADR/DCL clause preflight passed; `Blocking gaps (gate-failing): 0`.
- Implementation-start authorization succeeded with packet hash `sha256:77b16dfea1e9d13d6d390ea66ed4d36a639a2fe1700e705a08f1cd194cde3610`.
- Proposed pytest command passed: `19 passed`, with the pre-existing `asyncio_mode` pytest warning.
- Ruff check passed.
- Ruff format check passed: `4 files already formatted`.

## Files Changed

- `scripts/advisory_backlog_router.py`
- `platform_tests/scripts/test_advisory_backlog_router.py`
- `groundtruth.db`

`groundtruth.db` changed as part of the governed work-intent/implementation-start/project evidence flow. `scripts/advisory_intake_scanner.py` and `platform_tests/scripts/test_advisory_intake_scanner.py` were verified but did not require source changes for WI-5057.

## Acceptance Criteria Status

- [x] The helper output is deterministic enough for Prime Builder advisory-intake triage.
- [x] Live filtering excludes promoted, rejected, and already-work-item-backed advisories.
- [x] Existing scanner coverage still requires adopt/adapt classification plus the Required Prime Builder Owner-Grilling Gate section.
- [x] TEST-11295 is satisfied by test output and this implementation-report evidence.
- [x] Bridge lifecycle evidence is present: GO, work-intent claim, implementation-start authorization, preflight pass, and this report.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
