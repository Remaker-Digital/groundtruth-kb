GO

# Loyal Opposition Review - GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice B Prime Rule REVISED-1

**Status:** GO
**Date:** 2026-05-04
**Reviewer:** Codex Loyal Opposition
**Reviewed document:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-003.md`

## Verdict

GO.

The revised proposal resolves the two blocking findings from `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-002.md`. It now requires equivalent AUQ-only rule coverage in both Prime Builder rule files and replaces the weak any-class decision assertion with deterministic per-class checks.

## Applicability Preflight

Generated with:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule
```

Result:

```text
## Applicability Preflight

- packet_hash: `sha256:f433232fdeeee86ab37bb52b8b53add8166e4a38c309d77b92d3d8d4bfed0b45`
- bridge_document_name: `gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule`
- operative_file: `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/, content:project root boundary |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |
```

## Prior Deliberations

Searches run:

```text
$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "AskUserQuestion owner decision channel Prime Builder AUQ" --limit 8
$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "owner decision surfacing prose decision ask Stop hook" --limit 8
$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "acting Prime Builder harness portable role mapping" --limit 8
```

Relevant records:

- `DELIB-0945` remains relevant as prior NO-GO history in the owner-decision-surfacing area.
- `DELIB-S323-GOV-CHAT-DERIVED-SPEC-APPROVAL-APPROVAL` remains relevant to AskUserQuestion-backed owner approval.
- `DELIB-0830`, `DELIB-0831`, and `DELIB-0832` remain relevant to acting Prime Builder and harness-portable role assignment.
- `DELIB-S330-REQUIREMENTS-COLLECTION-HOOK-WITH-3-OPTION-CLARIFICATION` is adjacent future-scope governance for owner-input collection, but does not block this rule-only sub-slice.

No deliberation found rejects the revised AUQ-only rule approach.

## Findings

None blocking.

### Resolved F1 - Acting Prime rule is now tested with equivalent substance

**Claim:** The revised proposal fixes the prior under-test by applying the same required-token set to both `.claude/rules/prime-builder-role.md` and `.claude/rules/acting-prime-builder.md`.

**Evidence:** The revision states the test script asserts all required tokens in both files (`bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-003.md:21`). The proposed script defines both target paths and checks `REQUIRED_TOKENS` for `ACTING_RULE` in `test_acting_prime_builder_has_auq_only_section` (`bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-003.md:125`, `:168`). The test plan includes `T-rule-tokens-acting` for `.claude/rules/acting-prime-builder.md` (`bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-003.md:212`).

**Risk / impact:** Residual risk is low. A future change could still drift rule prose beyond substring coverage, but the revised tests now cover the specific contract this sub-slice proposes.

**Recommended action:** Implement as proposed and capture the exact post-implementation test output in the implementation report.

### Resolved F2 - Decision classes are now checked individually in both files

**Claim:** The revised proposal replaces the prior any-class grep with deterministic all-class assertions.

**Evidence:** The proposed test module defines `DECISION_CLASSES` with all eight classes and checks that list separately for `PRIME_RULE` and `ACTING_RULE` (`bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-003.md:140`, `:164`, `:173`). The test plan separately lists `T-rule-classes-prime` and `T-rule-classes-acting`, both requiring all eight classes (`bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-003.md:211`, `:213`). The spec-to-test mapping explicitly says enumeration completeness is covered in both files and requires all eight classes (`bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-003.md:227`).

**Risk / impact:** Residual risk is low. The test now fails for any omitted decision class in either target file.

**Recommended action:** Implement as proposed.

## Implementation Conditions

- The post-implementation report must carry forward the linked specifications, spec-to-test mapping, exact commands, and observed results.
- `T-out-of-applications-B` should be evaluated against the actual implementation diff so this rule slice does not accidentally touch `applications/`.
- Any deviation from the proposed rule text or test script should be explained in the implementation report and still preserve equivalent coverage in both target rule files.

## Decision Needed From Owner

None.

## File Bridge Scan

File bridge scan: 1 entry processed.
