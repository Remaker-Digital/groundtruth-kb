REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3d48-b886-7be2-a656-99678002edf1
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex desktop interactive; resolved role prime-builder via ::init gtkb pb

# Implementation Proposal Revision - CLAUDE.md Memory Framing

bridge_kind: prime_proposal
Document: gtkb-wi5123-reconcile-claude-md-memory-framing
Version: 005
Responds to: bridge/gtkb-wi5123-reconcile-claude-md-memory-framing-004.md
Project Authorization: PAUTH-PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-EXECUTION
Project: PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION
Work Item: WI-5123
target_paths: ["CLAUDE.md", ".groundtruth/formal-artifact-approvals"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

Retain the already-reviewed single-line CLAUDE.md memory framing and add the
missing owner-approved narrative-artifact packet. The revision changes no
CLAUDE.md wording; it makes that protected narrative change auditable and
eligible for independent verification.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-INTAKE-bb25be` requires operating
guidance to direct authority to canonical carriers rather than memory; this
revision adds only the approval evidence required to finalize the existing
compliant wording.

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

- `DELIB-202665929` - diagnosis of contradictory memory authority framing.
- `DELIB-202665930` - execution authorization for the remediation project.
- `bridge/gtkb-wi5123-reconcile-claude-md-memory-framing-004.md` - narrow NO-GO identifying only the missing packet.
- `bridge/gtkb-wi5126-deterministic-services-carrier-recovery-006.md` - verified sibling narrative-packet pattern.

## Owner Decisions / Input

- `DELIB-202665930` remains the active project authorization.
- `AUQ-FALLBACK-CODEX-2026-07-10-WI-5123-ARTIFACT`: Mike approved the exact CLAUDE.md memory-framing line by replying `approve WI-5123 artifact`.

## Findings Addressed

### F1 [P1] No narrative-artifact approval packet for the protected CLAUDE.md edit

Response: after independent GO, stage the existing CLAUDE.md blob and generate `NARRATIVE-CLAUDE-MEMORY-FRAMING-001`. The packet will record the owner-presented approval and exact staged-file hash. The revised implementation report will cite that packet and its hash.

## Scope Changes

- Added `.groundtruth/formal-artifact-approvals` to `target_paths` for the required packet.
- No CLAUDE.md wording, memory-file, implementation, or test scope is added; the existing reviewed line is unchanged.

## Pre-Filing Preflight Subsection

- Applicability and clause preflights will be run against this completed revision before filing.

## Specification-Derived Verification Plan

| Spec / governing surface | Verification |
| --- | --- |
| `SPEC-INTAKE-bb25be` | Run a focused `python -c` assertion that reads CLAUDE.md and verifies the exact state-and-bootstrap wording and MemBase/governed-artifact authority; observed result must be exit 0. |
| `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001` | Validate the packet has owner-presented approval metadata and that its `full_content_sha256` equals the staged CLAUDE.md blob. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Re-run the focused textual assertion, confirm CLAUDE.md remains at or below the GOV-01 300-line limit, and report observed results. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirm this REVISED proposal, post-implementation report, and independent LO verdict form the numbered thread. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirm both target paths remain in the repository root. |

Observed baseline: the CLAUDE.md diff is the owner-presented one-line replacement and the file remains within the GOV-01 300-line limit.

## Risk And Rollback

Risk is low: this revision creates approval evidence for accepted wording without changing the wording. Rollback of the narrative line requires a future GO-authorized change; bridge and approval records remain append-only.

## Recommended Commit Type

`fix`
