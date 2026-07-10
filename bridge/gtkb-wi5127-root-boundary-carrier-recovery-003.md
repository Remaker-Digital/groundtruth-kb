REVISED
author_identity: codex
author_harness_id: A
author_session_context_id: 019f3d48-b886-7be2-a656-99678002edf1
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex desktop interactive; resolved role prime-builder via ::init gtkb pb

# Implementation Proposal - Root-Boundary Exception Carrier Recovery

bridge_kind: prime_proposal
Document: gtkb-wi5127-root-boundary-carrier-recovery
Version: 003
Date: 2026-07-10 UTC
Responds to: bridge/gtkb-wi5127-root-boundary-carrier-recovery-002.md

Project Authorization: PAUTH-PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-CANONICAL-AUTHORITY-CARRIER-RECOVERY
Project: PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION
Work Item: WI-5127

target_paths: ["groundtruth.db", ".claude/rules/project-root-boundary.md", "groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md", "groundtruth-kb/templates/rules/canonical-terminology.md", "platform_tests/scripts/test_project_root_boundary_authority_carriers.py", ".groundtruth/formal-artifact-approvals"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

## Summary

Create canonical DCL carriers for the three operative root-boundary exceptions, demote their DELIB sources to provenance, and prevent recurrence with one per-exception authority-carrier test. This REVISED proposal corrects WI-5121's missing-KB-scope defect by declaring both `groundtruth.db` and `kb_mutation_in_scope: true`.

## Claim

Prime Builder proposes one bounded recovery slice for WI-5127. The final carrier text and identifiers remain subject to owner-approved formal-artifact packets before any DCL record is created.

## Requirement Sufficiency

Operative state: Existing requirements sufficient.

`SPEC-INTAKE-bb25be` requires every operating rule to have a canonical carrier. The active root-boundary rule currently names three executable exceptions whose only cited authority is a DELIB; the exact carrier dispositions below make their remediation complete and reviewable.

## In-Root Placement Evidence

All source, template, test, packet, and MemBase mutation paths are inside the project root. The exceptions being formalized remain narrow runtime allowances, not out-of-root project artifact authority.

## Specification Links

- `SPEC-INTAKE-bb25be` - operating rules require canonical carriers rather than DELIB-only authority.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the numbered bridge chain governs the recovery and independent review.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - exception rules are promoted into durable DCL artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete specification links accompany the proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - each exception has a committed authority-carrier assertion.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project, PAUTH, WI, and actual target paths are explicit.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all mutation surfaces remain in the platform root.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - carriers, packets, bridge reports, and tests are durable project artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this successor advances the owner-authorized recovery lifecycle.

## Prior Deliberations

- `DELIB-202665929` - diagnosed root-boundary rules relying on DELIB-only authority.
- `DELIB-202665930` - authorized the initial canonical-authority remediation project.
- `DELIB-202665933` - retired WI-5121 and ordered this successor to include all actual mutation surfaces, including the KB mutation.
- `DELIB-S325-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE` - provenance for the Sandbox Output Exception.
- `DELIB-FAB03-ROOT-BOUNDARY-EXCEPTION-20260611` - provenance for the DB-Snapshot Output Exception.
- `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` - provenance for the External Harness Executable Resolution Exception.
- This proposal differs from withdrawn WI-5121 by declaring the KB mutation in target and scope metadata, enumerating every operative exception and carrier, adding a carrier test target, and identifying the interactive approval-packet constraint.

## Owner Decisions / Input

- `DELIB-202665933` authorizes the recovery and requires the successor to eliminate WI-5121's incomplete KB-mutation scope.
- `PAUTH-PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-CANONICAL-AUTHORITY-CARRIER-RECOVERY` actively covers WI-5127.
- Each new DCL requires a per-artifact formal-approval packet. Carrier creation therefore must run in an interactive Prime Builder session capable of presenting the exact content to the owner and recording approval.

## Proposed Scope

- Sandbox Output Exception: create provisional `DCL-PROJECT-ROOT-BOUNDARY-SANDBOX-OUTPUT-EXCEPTION-001`; replace the DELIB-only source in the rule with this DCL and retain the DELIB as provenance.
- DB-Snapshot Output Exception: create provisional `DCL-PROJECT-ROOT-BOUNDARY-DB-SNAPSHOT-OUTPUT-EXCEPTION-001`; replace the DELIB-only source in the rule with this DCL and retain the DELIB as provenance.
- External Harness Executable Resolution Exception: create provisional `DCL-PROJECT-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXEC-EXCEPTION-001`; replace the DELIB-only source in the rule with this DCL and retain the DELIB as provenance.
- Update the two adopter templates so they cite the canonical carrier pattern and no longer propagate DELIB-only operating-rule authority.
- Add `test_project_root_boundary_authority_carriers.py` to assert all three operative exception sections cite their DCL carrier as authority and no exception is DELIB-sole-sourced.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-INTAKE-bb25be` | The new platform test asserts each named exception has its DCL carrier citation and no DELIB-only authority remains. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify the REVISED proposal and post-implementation report are numbered bridge versions with independent LO verdicts. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Query all three created DCL records in MemBase and verify the rule and templates point to those governed carriers. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run the applicability preflight on this REVISED body and confirm no required links are missing. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the focused authority-carrier test and report exact results, carrier lookups, packet hashes, and lint evidence in the implementation report. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Confirm the live REVISED proposal carries the active PAUTH, project, WI-5127, and all six actual mutation targets. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Verify all changed paths are in-root and none creates authority in an adopter or external location. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Verify each DCL, approval packet, narrative/template update, and test is recorded as a durable artifact. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Verify WI-5121's withdrawal, this REVISED successor, approval packets, implementation report, and LO verification form an auditable lifecycle. |

## Acceptance Criteria

- Each named operative exception has a canonical DCL carrier and no DELIB remains its sole authority.
- The root-boundary rule and adopter templates cite canonical carriers while retaining DELIBs only as provenance.
- The focused test asserts all three exception sections meet the carrier-authority rule.
- Each DCL's owner-approved formal-artifact packet is present and its recorded content hash matches its created record.

## Risks / Rollback

Risk is moderate because the change creates three durable governance carriers and changes platform boundary guidance. Rollback reverts narrative, template, and test changes, then retires or supersedes DCLs through their governed lifecycle; bridge files, packets, and deliberation evidence remain append-only audit records.

## Files Expected To Change

- `groundtruth.db`
- `.claude/rules/project-root-boundary.md`
- `groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md`
- `groundtruth-kb/templates/rules/canonical-terminology.md`
- `platform_tests/scripts/test_project_root_boundary_authority_carriers.py`
- `.groundtruth/formal-artifact-approvals`

## Recommended Commit Type

`fix`
