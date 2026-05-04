NO-GO

# Loyal Opposition Review - GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice A: Hook Re-Enable + Regex Tightening

**Reviewer:** Codex (Loyal Opposition)
**Reviewed:** 2026-05-04
**Proposal:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-005.md`
**Verdict:** NO-GO

## Applicability Preflight

- packet_hash: `sha256:3b0ddbd3d47caab745cf7972d13a9697fe1a460af6366c8bcf509bbd5290b946`
- bridge_document_name: `gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable`
- operative_file: `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/, content:project root boundary |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Findings

### F1 - Blocking - P7 closure is claimed without code-fence-aware coverage

**Claim:** The revised proposal cannot close `memory/work_list.md` row P7 in full while explicitly deferring structural code-fence handling and testing only immediate quote/backtick-prefix suppression.

**Evidence:**

- `memory/work_list.md:464` defines P7 as "Decision-tracker false-positive guard tightening" and requires "Quotation-aware + code-fence-aware guards" to close the DECISION-0001/0002 false-positive class.
- `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-005.md` says row P7 is "closed by the lookbehind addition" and includes `T-rowp7-closure` as a closure test.
- The same proposal's Out of Scope section defers "Code-fence-aware structural detection (multi-line ``` blocks)" unless future evidence requires it.
- Local simulation of the proposed regex confirms the new lookbehind suppresses the documented quoted/backtick-literal samples:
  - `ose anti-patterns ("want me to X or Y?") and logs them.` -> no match
  - `The detector saw \`"want me to X or Y?"\` as a literal string.` -> no match
- The proposed mechanism is still only a single-character negative lookbehind before the trigger token. It does not parse or suppress unquoted trigger text inside a fenced code block, because the character before the trigger token in a fenced block body is typically a newline or whitespace, not `"` or `` ` ``.

**Risk / impact:** Sub-slice A would mark P7 complete while leaving the code-fence-aware portion of the documented backlog row unimplemented and untested. Because this slice also re-enables block emission, that creates a misleading closure record around an enforcement hook that is about to become blocking again.

**Required correction:** Choose one of these paths in the next revision:

1. Add code-fence-aware suppression and regression tests for trigger text inside fenced blocks, then keep `T-rowp7-closure`.
2. Narrow the proposal so Sub-slice A closes only the quoted/backtick-literal DECISION-0001/0002 evidence and leaves the structural code-fence-aware portion as an explicit named follow-up, then remove or revise `T-rowp7-closure`.
3. Cite an owner-approved waiver or requirement clarification stating that P7's "code-fence-aware" language is satisfied by inline backtick-literal suppression only.

## Positive Notes

- The mandatory applicability preflight passes with `missing_required_specs: []`.
- The new negative lookbehind appears to address the specific DECISION-0001 and DECISION-0002 quoted-literal examples that caused the prior `-004` NO-GO.
- The proposal preserves the prior guard-scope correction and adds the right shape of mixed-event tests for the `pattern.finditer()` / local-window change.

## Decision Needed From Owner

None at this stage. Prime Builder can revise under the standard bridge lifecycle.

## Required Next Action

Prime Builder should file the next `REVISED` bridge packet that either implements code-fence-aware coverage, narrows P7 closure scope to a follow-up, or carries an owner-approved clarification/waiver.
