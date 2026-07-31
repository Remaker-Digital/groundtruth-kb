NO-GO
::init gtkb pb
::open test

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f7815-a565-78d3-a599-dec8388086ff
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Loyal Opposition; reasoning_effort=xhigh; sandbox=none; thread_source=user
author_metadata_source: x-codex-turn-metadata via current owner transcript role assignment

# Loyal Opposition Proposal Review - NO-GO - WI-5630 Platform Tests Discovery

bridge_kind: lo_verdict
Document: gtkb-wi5630-spec-derived-platform-tests-discovery
Version: 002
Responds to: bridge/gtkb-wi5630-spec-derived-platform-tests-discovery-001.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5630
Recommended commit type: none; proposal requires revision before implementation

## Verdict

NO-GO. The underlying defect is real: `scripts/run_spec_derived_tests.py` currently discovers only `tests/` and `groundtruth-kb/tests/`, so `platform_tests/` suites are invisible to the spec-derived runner. But v001 overclaims its concrete unblocker: it says this change covers `platform_tests/scripts/test_batch_archive_terminal_verdicts.py` for the WI-5370 archive-preserve verification, while preserving module-docstring-only matching and changing only the runner plus runner tests.

That named WI-5370 test file has no module-level spec citation for `DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001`. Adding `platform_tests/` as a discovery root alone would still leave the WI-5370 archive-preserve spec at `no_derived_tests`. Therefore the proposal as written does not actually satisfy its stated scope and should be revised before implementation.

## First-Line Role Eligibility And Review Independence

PASS. The live thread head before this verdict was `NEW` at `bridge/gtkb-wi5630-spec-derived-platform-tests-discovery-001.md`, which is Loyal-Opposition-actionable. `NO-GO` is a Loyal Opposition status under `GOV-FILE-BRIDGE-AUTHORITY-001`.

PASS. Version 001 was authored by Prime Builder session `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`; this verdict is authored by Loyal Opposition session `019f7815-a565-78d3-a599-dec8388086ff`. The author and reviewer session contexts are independent.

## Blocking Finding

### F1 - The named WI-5370 beneficiary would still not be discovered

Severity: P1 blocking proposal-scope defect.

Version 001 says the current runner reports `no_derived_tests` for `platform_tests/scripts/test_batch_archive_terminal_verdicts.py` in the canonical WI-5370 implementation report, and proposes to preserve conservative module-level-docstring discovery while adding `platform_tests/` as a root. That is only half of the necessary repair.

The runner's current contract is explicit: only module-level docstrings are scanned, and `TEST_DIRS` currently contains only `tests/` and `groundtruth-kb/tests/`.

```text
# Test-discovery roots. CONSERVATIVE: only module-level docstrings are scanned;
# function-level docstrings would risk overcounting (per -003 §1.3).
TEST_DIRS = (PROJECT_ROOT / "tests", PROJECT_ROOT / "groundtruth-kb" / "tests")
```

The WI-5370 archive test module's docstring is only:

```text
"""Tests for scripts/batch_archive_terminal_verdicts.py."""
```

It contains no module-level `DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001` citation. An internal test fixture later mentions `GOV-WORK-TREE-HYGIENE-001`, but the runner intentionally does not count function-level, fixture-string, or arbitrary body references as derived-test linkage.

The current dry-run confirms the actual consequence:

```text
python scripts/run_spec_derived_tests.py --bridge-id gtkb-wi5370-batched-archive-preserve-service --dry-run --json
verified_overall False
archive_spec_entry {'reason': 'no_derived_tests', 'tests_found': [], 'tests_passed': 0, 'tests_failed': 0, 'verified': False}
```

Because v001's target paths are only `scripts/run_spec_derived_tests.py` and `platform_tests/scripts/test_run_spec_derived_tests.py`, implementation cannot add the missing module-level spec citation to `platform_tests/scripts/test_batch_archive_terminal_verdicts.py` without exceeding the reviewed target scope. A revision must either remove the claim that this slice unblocks the named WI-5370 test, or include the authorized test-linkage update needed for the named file to satisfy the preserved module-docstring-only rule.

## Non-Blocking Confirmations

The proposed runner-root change is directionally correct. Applicability and mandatory clause preflights pass, `WI-5630` is open under the tree-stabilization PAUTH, and the existing runner test module currently passes 47 tests.

The correct revised shape is likely small: add `platform_tests/` discovery and grouped execution coverage, while also making the stated beneficiary accurate by either narrowing the claim or explicitly updating the relevant platform test module's docstring under a governed target path.

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5630-spec-derived-platform-tests-discovery --content-file bridge/gtkb-wi5630-spec-derived-platform-tests-discovery-001.md --json`
Exit code: 0

- packet_hash: `sha256:d67329b50bfd67b9b5ff0e97b023d411aa08e422b922b39d5f46a18505fcee8d`
- candidate_evidence_hash: sha256:d9e8024a8ce8f993b03b477cd319b8e4a932cc41f17fbfc1c1cc706a48ddd5d0
- bridge_document_name: `gtkb-wi5630-spec-derived-platform-tests-discovery`
- content_file: `bridge/gtkb-wi5630-spec-derived-platform-tests-discovery-001.md`
- operative_file: `bridge/gtkb-wi5630-spec-derived-platform-tests-discovery-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []
- declared_target_paths: [`platform_tests/scripts/test_run_spec_derived_tests.py`, `scripts/run_spec_derived_tests.py`]

## Clause Applicability

Command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5630-spec-derived-platform-tests-discovery --content-file bridge/gtkb-wi5630-spec-derived-platform-tests-discovery-001.md`
Exit code: 0

- Bridge id: `gtkb-wi5630-spec-derived-platform-tests-discovery`
- Operative file: `bridge\gtkb-wi5630-spec-derived-platform-tests-discovery-001.md`
- Clauses evaluated: 5
- must_apply: 4
- may_apply: 1
- not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0

## Verification Evidence

```text
python -m pytest platform_tests/scripts/test_run_spec_derived_tests.py -q --tb=short
47 passed in 74.24s
```

## Specification Links

- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-VERIFIED-BRIDGE-HISTORY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`

## Commands Executed

```text
python .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-wi5630-spec-derived-platform-tests-discovery --format json --preview-lines 100
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5630-spec-derived-platform-tests-discovery --content-file bridge/gtkb-wi5630-spec-derived-platform-tests-discovery-001.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5630-spec-derived-platform-tests-discovery --content-file bridge/gtkb-wi5630-spec-derived-platform-tests-discovery-001.md
python scripts/run_spec_derived_tests.py --bridge-id gtkb-wi5370-batched-archive-preserve-service --dry-run --json
python -m pytest platform_tests/scripts/test_run_spec_derived_tests.py -q --tb=short
Get-Content scripts/run_spec_derived_tests.py | Select-Object -First 90
Get-Content platform_tests/scripts/test_batch_archive_terminal_verdicts.py | Select-Object -First 110
rg -n "DCL-ARCHIVE-PRESERVE|WI-5370|SPEC|GOV|DCL|Tests for" platform_tests/scripts/test_batch_archive_terminal_verdicts.py bridge/gtkb-wi5630-spec-derived-platform-tests-discovery-001.md scripts/run_spec_derived_tests.py
```

## Owner Decisions / Input

None required.

## Skills Applied

- gtkb-bridge
- proposal-review
