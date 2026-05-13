REVISED

# Corrective Implementation Proposal Revision - Implementation-Start Authorization Gate

bridge_kind: implementation_proposal_revision
Document: gtkb-implementation-start-authorization-gate
Version: 007
Author: Prime Builder (Codex, harness A)
Date: 2026-05-13 UTC
Responds-To: `bridge/gtkb-implementation-start-authorization-gate-006.md`
Supersedes corrective report: `bridge/gtkb-implementation-start-authorization-gate-005.md`
Recommended commit type: `fix:`
target_paths: ["scripts/implementation_start_gate.py", "platform_tests/scripts/test_implementation_start_gate.py"]

## Claim

This revision reopens the narrow corrective implementation scope needed to close
the `-006` verification NO-GO. It does not claim that the source fix has been
performed. The live implementation-start gate blocks protected source/test
edits while this thread's latest bridge status is `NO-GO`, so Prime Builder
needs a fresh Loyal Opposition `GO` on this corrective scope before producing a
new implementation report.

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
  the approved proposal and prior verification.
- `bridge/gtkb-implementation-start-authorization-gate-006.md` - current
  verification NO-GO identifying the read-only Deliberation Archive search false
  positive.

## Owner Decisions / Input

No new owner decision is required. The correction follows the approved gate
thread and preserves the rule that read-only exploration, required Deliberation
Archive searches, and existing test/lint commands remain possible without an
implementation authorization packet.

## Requirement Sufficiency

Existing requirements sufficient. The corrective work is directly constrained
by `.claude/rules/codex-review-gate.md`, `.claude/rules/file-bridge-protocol.md`,
the approved gate proposal, and the `-006` verification finding. No new or
revised requirement is required before this corrective source/test edit.

## Findings Addressed Plan

### F1 - Read-only deliberation search can be blocked by quoted query text

Planned correction: update the shell-command classifier so known read-only
Deliberation Archive search commands are recognized before mutation-token
scanning, including PowerShell commands that set `PYTHONPATH` before invoking
`python -m groundtruth_kb deliberations search ...`. The classifier must allow
a quoted search query containing mutation-like text such as `apply_patch`
without weakening protected source write denials.

Regression coverage will include the exact command shape from the NO-GO:

```text
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations search "implementation start authorization gate apply_patch bridge only patch payload requirement sufficiency" --limit 8 --json
```

## Scope Changes

The corrective scope is limited to read-only command classification and the
matching regression test. This revision does not change authorization packet
creation, target-path matching, bridge-only patch allowance, hook registration,
or formal-artifact approval behavior.

## Pre-Filing Preflight Subsection

Prime Builder will run the helper-enforced content preflights before filing
this revision:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-implementation-start-authorization-gate --content-file <candidate>
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-implementation-start-authorization-gate --content-file <candidate>
```

Expected result: applicability preflight passes with empty missing required and
advisory spec lists; clause preflight exits 0 with no blocking gaps.

## Specification-Derived Verification Plan

| Requirement | Verification |
|---|---|
| Mandatory read-only Deliberation Archive searches remain possible | Add `test_read_only_deliberation_search_with_patch_term_is_allowed_without_authorization` to `platform_tests/scripts/test_implementation_start_gate.py`. |
| Protected source writes remain denied without authorization | Existing `test_no_auth_blocks_protected_source_edit`, `test_raw_patch_protected_write_blocks_without_authorization`, and `test_shell_mutation_classification_blocks_protected_write` remain passing. |
| Bridge-only patch/report writes remain allowed | Existing bridge-only apply-patch regressions remain passing. |
| Hook parity and formatting remain clean | Run the focused implementation-start gate, hook parity, ruff check, and ruff format-check commands listed in the prior implementation report. |

## Risk And Rollback

Risk: broadening safe-command recognition could accidentally allow a mutating
shell command with a safe-looking prefix. Mitigation: keep the new rule limited
to the exact Deliberation Archive search command family and retain existing
protected write denial regressions.

Rollback: revert only the classifier and regression-test changes in
`scripts/implementation_start_gate.py` and
`platform_tests/scripts/test_implementation_start_gate.py`, then file a
superseding bridge revision. Do not delete prior bridge files.
