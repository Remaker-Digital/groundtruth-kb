REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3d48-b886-7be2-a656-99678002edf1
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex desktop interactive; resolved role prime-builder via ::init gtkb pb

# Implementation Proposal Revision - Peer Review Reliability Weighting

bridge_kind: prime_proposal
Document: gtkb-wi5122-promote-peer-review-weighting-rule
Version: 005
Responds to: bridge/gtkb-wi5122-promote-peer-review-weighting-rule-004.md
Project Authorization: PAUTH-PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-EXECUTION
Project: PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION
Work Item: WI-5122
target_paths: [".claude/rules/loyal-opposition.md", ".groundtruth/formal-artifact-approvals"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

Retain the already-reviewed peer-review reliability rule text and add its
missing owner-approved narrative-artifact packet. This revision changes no
rule wording; it makes the existing protected narrative change auditable and
eligible for independent verification.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-INTAKE-bb25be` requires this operating
rule to live in a canonical carrier; the revision adds only the approval evidence
required to finalize that already-approved carrier.

## Specification Links

- `SPEC-INTAKE-bb25be`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`

## Prior Deliberations

- `DELIB-202665929` - diagnosis requiring a canonical carrier for operational rules.
- `DELIB-202665930` - execution authorization for the canonical-authority remediation project.
- `bridge/gtkb-wi5122-promote-peer-review-weighting-rule-004.md` - narrow NO-GO identifying only the missing packet.
- `bridge/gtkb-wi5126-deterministic-services-carrier-recovery-006.md` - verified sibling pattern for rule text plus matching narrative packet.

## Owner Decisions / Input

- `DELIB-202665930` remains the project authorization.
- `AUQ-FALLBACK-CODEX-2026-07-10-WI-5122-ARTIFACT`: the exact `Peer Review Reliability Weighting` section was presented to Mike, and Mike replied `Continue.` to authorize the narrative-artifact approval path.

## Findings Addressed

### F1 [P1] No narrative-artifact approval packet for the protected loyal-opposition.md edit

Response: after independent GO, stage the existing `.claude/rules/loyal-opposition.md` blob and generate `NARRATIVE-LOYAL-OPPOSITION-PEER-REVIEW-WEIGHTING-001`. The packet will record the owner-presented content, approval, and exact staged-file hash. The revised implementation report will cite that packet and its hash.

## Scope Changes

- Added `.groundtruth/formal-artifact-approvals` to `target_paths` for the required packet.
- No rule-text, memory-file, implementation, or test scope is added; the existing reviewed rule content is unchanged.

## Pre-Filing Preflight Subsection

- Applicability preflight: pending execution against this revision before filing.
- ADR/DCL clause preflight: pending execution against this revision before filing.

## Specification-Derived Verification Plan

| Spec / governing surface | Verification |
| --- | --- |
| `SPEC-INTAKE-bb25be` | Run a focused `python -c` assertion that reads the canonical LO rule file and verifies the heading plus its three approved paragraphs; observed result must be exit 0. |
| `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001` | Validate the packet has owner-presented approval metadata and that its `full_content_sha256` equals the staged rule blob. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirm this REVISED proposal, post-implementation report, and independent LO verdict form the numbered thread. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Re-run the focused textual assertion and report the staged-file and packet-hash comparison; observed result must be exit 0. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirm both target paths remain in the repository root. |

Observed baseline: `git diff -- .claude/rules/loyal-opposition.md` shows only the 19-line owner-presented section; no unrelated rule text is included.

## Risk And Rollback

Risk is low: this revision creates approval evidence for accepted rule wording without changing the wording. Rollback removes the rule section only through a future GO-authorized change and retains bridge and approval records as append-only audit evidence.

## Recommended Commit Type

`fix`
