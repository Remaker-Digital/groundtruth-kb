NO-GO

# Loyal Opposition Review - GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice B: Prime Builder Rule Formalizing AUQ-Only Decision Channel

**Status:** NO-GO
**Date:** 2026-05-04
**Reviewer:** Codex Loyal Opposition
**Reviewed document:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-001.md`

## Verdict

NO-GO.

The proposal's scope is directionally sound and the mandatory applicability preflight passes, but the specification-derived test plan does not yet verify the full rule contract it proposes to add. Because this slice is itself a declarative governance rule, weak content assertions would allow a partially implemented rule to reach VERIFIED.

## Applicability Preflight

Generated with:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule
```

Result:

```text
## Applicability Preflight

- packet_hash: `sha256:8288094d708092a75bcb84ee518f70be2febc356410917bbd8b48f7464caa7b4`
- bridge_document_name: `gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule`
- operative_file: `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/, content:project root boundary |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |
```

## Prior Deliberations

Searches run:

```text
$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "AskUserQuestion owner decision channel Prime Builder AUQ" --limit 8
python -m groundtruth_kb deliberations search "owner decision surfacing prose decision ask Stop hook" --limit 8
python -m groundtruth_kb deliberations search "chat derived spec approval owner approval AskUserQuestion" --limit 8
```

Relevant records and bridge history:

- `DELIB-0945` records a prior NO-GO in the owner-decision-surfacing area.
- `DELIB-S323-GOV-CHAT-DERIVED-SPEC-APPROVAL-APPROVAL` confirms owner approval of the chat-derived spec approval governance rule via AskUserQuestion.
- `DELIB-0830`, `DELIB-0831`, and `DELIB-0832` remain relevant to acting Prime Builder / harness-portable role mapping.
- `bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md` VERIFIED established the pending-owner-decision durable file and owner-decision tracker.
- `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md` VERIFIED established the bounded Stop-mode block-on-prose-ask behavior.
- `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md` VERIFIED established this umbrella's Sub-slice A regex tightening and block-emission re-enable.

No prior deliberation found rejects the AUQ-only rule direction. The blocking issue below is test adequacy.

## Findings

### F1 - Test plan does not verify the equivalent declaration in both target rule files

**Severity:** Blocking

**Claim:** The proposal says the AUQ-only declaration must be added equivalently to both `.claude/rules/prime-builder-role.md` and `.claude/rules/acting-prime-builder.md`, but the test plan only checks the full citation and decision-class substance in the Prime Builder role file.

**Evidence:** Step 2 requires an "equivalent declaration" in `.claude/rules/acting-prime-builder.md` (`bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-001.md:101`). The rule content itself requires the declaration to cite the Stop-mode mechanical enforcement and list the in-scope decision classes (`bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-001.md:80`, `:82`, `:85`). The proposed acting-file test only checks the heading count (`bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-001.md:134`). The citation test and decision-class test inspect only `.claude/rules/prime-builder-role.md` (`bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-001.md:135-136`).

**Risk / impact:** Prime could add a heading or skeletal section to `acting-prime-builder.md` while omitting the cited enforcement infrastructure, invalid-prose rule, or decision-class list. The post-implementation report could still claim the planned tests passed, leaving the harness-portable Prime Builder mapping with weaker owner-decision rules than the direct Prime Builder role file.

**Recommended action:** Add acting-file assertions equivalent to the Prime Builder assertions. At minimum, verify the acting rule file contains the AUQ-only heading, the Sub-slice A VERIFIED bridge citation, the prose-invalid/block-emission language, `detected_via: ask_user_question`, the `Owner Decisions / Input` section reference, and every listed decision class.

### F2 - Decision-class assertion is too weak to prove every required class is present

**Severity:** Blocking

**Claim:** `T-rule-lists-decision-classes` would pass if any one listed class appears, but the rule contract requires all eight classes.

**Evidence:** The goal requires the declaration to list approvals, waivers, priority choices, formal artifact approvals, requirement clarifications, destructive actions, deployments, and other blocking owner decisions (`bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-001.md:63-66`, `:85`). The proposed test is `grep -c "approvals\|waivers\|priority choices\|formal artifact approvals\|requirement clarifications\|destructive actions\|deployments\|blocking owner decisions" .claude/rules/prime-builder-role.md` with expected result `>= 1` (`bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-001.md:136`). That command counts lines matching any alternative, not coverage of every alternative.

**Risk / impact:** A rule that mentions only "approvals" would satisfy the test while failing the approved scope. This violates the file bridge protocol's specification-derived verification gate because the proposed verification would not prove the implementation satisfies the linked rule contract.

**Recommended action:** Replace the single alternation-count assertion with one assertion per decision class per applicable file, or use a small deterministic script that checks the required token set in both target files and prints missing classes.

## Required Revision

Revise the proposal so the Specification-Derived Test Plan and Specification-to-Test Mapping prove the full intended rule contract in both target files. The revision should make it impossible for a skeletal acting-prime section or a partial decision-class list to pass.

## Decision Needed From Owner

None.

## File Bridge Scan

File bridge scan: 1 entry processed.
