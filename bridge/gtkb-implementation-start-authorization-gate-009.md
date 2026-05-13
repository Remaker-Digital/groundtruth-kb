NEW

# Corrective Implementation Report - Implementation-Start Authorization Gate

bridge_kind: implementation_report
Document: gtkb-implementation-start-authorization-gate
Version: 009
Author: Prime Builder (Codex, harness A)
Date: 2026-05-13 UTC
Implements: `bridge/gtkb-implementation-start-authorization-gate-007.md`
GO verdict: `bridge/gtkb-implementation-start-authorization-gate-008.md`
Recommended commit type: `fix:`

## Claim

The corrective implementation-start gate scope approved at `-008` is
implemented. Known read-only Deliberation Archive search commands are allowed
before mutation-token scanning, including PowerShell `PYTHONPATH` prefaces and
quoted query text containing mutation-like words such as `apply_patch`.
Protected source/test/script writes remain denied without a live implementation
authorization packet.

## Implementation Authorization

Prime Builder ran the required implementation-start gate before source/test
work:

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-implementation-start-authorization-gate
```

Observed result: authorization packet created for latest `GO` file
`bridge/gtkb-implementation-start-authorization-gate-008.md`, proposal file
`bridge/gtkb-implementation-start-authorization-gate-007.md`, requirement
sufficiency `sufficient`, target paths `scripts/implementation_start_gate.py`
and `platform_tests/scripts/test_implementation_start_gate.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/bridge-essential.md`
- `.claude/settings.json`
- `.codex/hooks.json`

## Prior Deliberations

- `DELIB-1740`, `DELIB-1715`, `DELIB-0628`, `DELIB-1646`, and
  `DELIB-S321-SPEC-CREATION-STANDING-AUTH` - carried-forward gate design,
  bridge authority, harness parity, and requirement-sufficiency context from
  the approved proposal chain.
- `bridge/gtkb-implementation-start-authorization-gate-006.md` - verification
  NO-GO identifying the read-only Deliberation Archive search false positive.

## Owner Decisions / Input

No new owner decision was required. This correction follows the approved gate
thread and preserves the rule that read-only exploration, required
Deliberation Archive searches, and existing test/lint commands remain possible
without an implementation authorization packet.

## Files Changed

- `scripts/implementation_start_gate.py`
- `platform_tests/scripts/test_implementation_start_gate.py`

## Implementation Summary

- Added `python -m groundtruth_kb deliberations search` to the safe command
  prefix list used before mutation-token scanning.
- Added PowerShell environment-assignment prefix stripping so commands such as
  `$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb ...` are
  recognized as the underlying read-only Deliberation Archive search command.
- Kept protected source-write and patch-denial behavior unchanged.
- Added
  `platform_tests/scripts/test_implementation_start_gate.py::test_deliberation_search_query_with_patch_word_is_allowed_without_authorization`,
  covering a quoted Deliberation Archive search query containing `apply_patch`.

## Spec-to-Test Mapping

| Requirement | Evidence |
|---|---|
| Mandatory read-only Deliberation Archive searches remain possible | `test_deliberation_search_query_with_patch_word_is_allowed_without_authorization` passes with a PowerShell `PYTHONPATH` preface and quoted `apply_patch` query text. |
| Protected source writes remain denied without authorization | Existing `test_no_auth_blocks_protected_source_edit`, `test_raw_patch_protected_write_blocks_without_authorization`, and `test_shell_mutation_classification_blocks_protected_write` remain passing in the focused gate suite. |
| Bridge-only patch/report writes remain allowed | Existing bridge-only apply-patch regressions remain passing in the focused gate suite. |
| Hook parity and registration stay clean | Hook registration/Codex parity tests and `scripts/check_codex_hook_parity.py` pass. |
| Touched files are lint-clean and formatted | Targeted ruff check and ruff format-check pass for `scripts/implementation_start_gate.py` and `platform_tests/scripts/test_implementation_start_gate.py`. |

## Verification

Commands executed:

```text
python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=short
python -m pytest platform_tests/scripts/test_hook_registration_parity.py platform_tests/scripts/test_codex_hook_parity.py -q --tb=short
python -m pytest platform_tests/scripts/test_codex_bridge_compliance_gate.py platform_tests/scripts/test_hook_registration_parity.py platform_tests/scripts/test_codex_hook_parity.py platform_tests/scripts/test_implementation_start_gate.py -q --tb=short -p no:cacheprovider
python scripts/check_codex_hook_parity.py
python -m ruff check scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py
python -m ruff format --check scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py
```

Observed results:

- Implementation-start focused tests: `14 passed`.
- Hook registration plus Codex hook parity tests: `13 passed`.
- Combined gate/parity lane: `34 passed`.
- Codex hook parity script: `PASS`.
- Ruff check: `All checks passed!`
- Ruff format check: `2 files already formatted`.

## Risk And Rollback

Risk: safe-command recognition could be broadened too far. Mitigation: the
safe command family is limited to known read-only prefixes and the existing
protected-write denial regressions remain passing.

Rollback: revert only the classifier and regression-test changes in
`scripts/implementation_start_gate.py` and
`platform_tests/scripts/test_implementation_start_gate.py`, then file a
superseding bridge revision. Do not delete prior bridge files.
