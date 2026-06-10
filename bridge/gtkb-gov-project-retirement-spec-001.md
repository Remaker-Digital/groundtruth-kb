NEW

# Governance Capture Proposal - capture GOV-PROJECT-RETIREMENT-001 (backlog project-retirement governance rule)

bridge_kind: governance_advisory
Document: gtkb-gov-project-retirement-spec
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-17 UTC

target_paths: [".groundtruth/formal-artifact-approvals/2026-05-17-GOV-PROJECT-RETIREMENT-001.json"]

This NEW proposal captures an owner-stated governance rule as a formal MemBase specification: `GOV-PROJECT-RETIREMENT-001`, the backlog project-retirement rule. The owner stated the rule in session S357 (2026-05-17), selected the bridge-coverage definition of a VERIFIED work item via AskUserQuestion, and approved the drafted spec content via AskUserQuestion. The implementation is a single formal-artifact-approval packet plus one MemBase `specifications` insert; there is no source, test, hook, or configuration change. This proposal is classified `governance_review` (not `implementation_proposal`): it captures an owner-directed governance specification and is not tied to a project work item or project authorization.

## Owner Directive

Owner statement, session S357, 2026-05-17 (verbatim intent): "The backlog is comprised of projects, which contain work items. When all of the work items within (associated with via explicit links) a backlog project are VERIFIED, the project is retired along with all of the VERIFIED work items associated with that project. As long as any work item associated with a project is not VERIFIED, the project cannot be retired."

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol observed; this proposal flows NEW -> GO -> implement -> report -> VERIFIED.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Specification-Derived Verification Plan maps the acceptance criteria (the inserted spec row matches the approved content) to verification commands.
- `GOV-ARTIFACT-APPROVAL-001` - creating a `governance` specification is a formal-artifact-creation event; the formal-artifact-approval packet (IP-1) and explicit owner approval are required before canonical insertion.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - the formal-artifact-approval-gate PreToolUse hook gates the MemBase insert on the packet's presence and matching content hash.
- `GOV-STANDING-BACKLOG-001` - the captured rule governs the backlog (projects and their work items); this spec is consistent with, and refines the lifecycle dimension of, the standing-backlog governance contract.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - advisory: the captured rule defines the gate for one specific artifact lifecycle transition (a project moving to the `retired` state); the new GOV is consistent with this constraint's lifecycle-state model and does not alter it.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the rule, the owner decisions, and the verification are preserved as durable bridge and MemBase artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - traceability is preserved across the owner directive, this thread, the audit, and the inserted spec.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the only target file (the approval packet) is in-root under the GT-KB project root; no application-tree paths.

This proposal creates a `governance` specification; it does not modify source, tests, hooks, or configuration. The de-facto requirement is the owner directive quoted above; this proposal captures it as the formal governing artifact.

## Prior Deliberations

A Deliberation Archive search for "project retirement all work items verified project lifecycle backlog completion" (run S357) returned no matching record - the rule is not previously archived. The prior-decision history for this capture:

- Owner directive, S357 (2026-05-17) - the owner stated the project-retirement rule (quoted above), refining "within" to "associated with via explicit links" for precision.
- S357 backlog audit (this session) - audited 138 active projects / 2125 work items against the rule. Key findings: the `work_items.resolution_status` field is systematically stale (45 of 2125 carry `verified`, all legacy; no routine path sets it); bridge-thread VERIFIED coverage is the true completion signal and the criterion GT-KB's `bridge-verified-backlog-reconciler` machinery aligns with; ~90% of work items have no project link, and duplicate or malformed project records exist (a separate data-remediation concern).
- Owner AskUserQuestion, S357 - selected "Adopt bridge-coverage as the VERIFIED criterion and capture the rule" over data-remediation-first and reconciler-first alternatives.
- Owner AskUserQuestion, S357 - approved the drafted `GOV-PROJECT-RETIREMENT-001` content (presented in native review format) for capture.

## Owner Decisions / Input

This proposal depends on owner approval. The relevant AskUserQuestion evidence:

- **Owner directive (S357, 2026-05-17):** the owner stated the project-retirement rule as a governance directive (quoted in `## Owner Directive`).
- **Owner AskUserQuestion (S357) - VERIFIED criterion:** presented (a) `resolution_status == verified`, (b) bridge-thread coverage, (c) build a reconciler first. The owner selected the bridge-coverage path ("Adopt bridge-coverage; capture rule"). The spec's "VERIFIED work item" definition reflects that choice.
- **Owner AskUserQuestion (S357) - draft approval:** the drafted `GOV-PROJECT-RETIREMENT-001` content was presented in native review format; the owner answered "Approve the draft for capture", authorizing this routing.

Per `GOV-ARTIFACT-APPROVAL-001`, IP-1 records this approval evidence in the formal-artifact-approval packet bound to the spec's content hash; canonical insertion (IP-2) is gated on that packet.

## Requirement Sufficiency

Existing requirements sufficient. The owner directive (S357) is the operative requirement; this proposal captures it verbatim-in-intent as the formal `governance` specification. No new or revised requirement is required before implementation; the proposal is the capture of the requirement itself.

## Proposed Specification Content (GOV-PROJECT-RETIREMENT-001)

The `governance` specification to be inserted, as approved by the owner:

- **ID:** `GOV-PROJECT-RETIREMENT-001`
- **Type:** `governance`
- **Status:** `specified`
- **Title:** Backlog project retirement is gated on all linked work items being VERIFIED

**Rule.** A backlog project is retired - together with all of its associated work items - if and only if every work item explicitly linked to that project is VERIFIED. As long as any explicitly-linked work item is not VERIFIED, the project cannot be retired. Retirement is collective: the project and its VERIFIED work items retire together; there is no per-work-item retirement independent of its project.

**"VERIFIED work item" definition.** For this rule, a work item is VERIFIED when it is covered by a VERIFIED bridge thread - the bridge thread addressing the work item has reached terminal `VERIFIED` status in `bridge/INDEX.md`. The MemBase `work_items.resolution_status` field is explicitly not the criterion: the S357 backlog audit found it systematically stale. Bridge-thread coverage is the completion-truth signal and the criterion GT-KB's `bridge-verified-backlog-reconciler` machinery aligns with. A work item with no bridge thread, or whose thread is at a non-terminal status, is not VERIFIED.

**"Explicitly linked" definition.** A work item is associated with a project via an explicit project-to-work-item membership link. Work items not explicitly linked to a project are not part of that project's retirement-gating set.

**Rationale.** Owner governance directive, S357. The rule makes project retirement a faithful reflection of completion - a project is done exactly when all the known work it groups is verified-complete. Retiring a project with unverified work would falsely signal completion.

**Consequences.** (1) Project-retirement tooling must verify every linked work item is VERIFIED before retiring a project. (2) One non-VERIFIED linked work item blocks the entire project. (3) Retirement is collective (project plus its VERIFIED work items).

**Rejected alternative.** Using `work_items.resolution_status == verified` as the VERIFIED criterion - rejected (S357 owner decision) because the audit proved that field systematically stale and unmaintained.

**Known gaps (non-enforcement note).** The S357 audit found the current backlog data cannot yet support mechanical enforcement: ~90% of work items have no project link, the `project_name` field is free-text and inconsistent, and duplicate or malformed project records exist. Until that is remediated, this GOV is rule-cited soft authority. A machine-checkable companion DCL and the backlog data remediation are tracked as follow-on work.

## Proposed Implementation

### IP-1: formal-artifact-approval packet

Create `.groundtruth/formal-artifact-approvals/2026-05-17-GOV-PROJECT-RETIREMENT-001.json` per `GOV-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001`: `artifact_type=governance`, `artifact_id=GOV-PROJECT-RETIREMENT-001`, `action=create`, `full_content` (the spec body above), `full_content_sha256`, `presented_to_user=true`, `transcript_captured=true`, `explicit_change_request` (the owner draft-approval AskUserQuestion), `changed_by=prime-builder/claude/B`, `change_reason`, `approved_by=owner`.

### IP-2: MemBase insert

Insert `GOV-PROJECT-RETIREMENT-001` into the MemBase `specifications` table (`type=governance`, `status=specified`) via the governed specification-creation path, with the IP-1 packet in place so the formal-artifact-approval-gate hook admits the write. `change_reason` cites this bridge thread and the owner directive.

### IP-3: no code or test changes

`GOV-PROJECT-RETIREMENT-001` is a governance principle (rule-cited soft authority). It carries no machine-checkable assertions; mechanical enforcement is the deferred companion DCL. No source, test, hook, or configuration files are modified.

## Specification-Derived Verification Plan

De-facto specification: the owner directive (S357). The implementation is verified when the captured artifact faithfully records it.

| # | Acceptance criterion | Verification |
|---|---|---|
| 1 | `GOV-PROJECT-RETIREMENT-001` exists in MemBase with `type=governance`, `status=specified` | spec read via the KB API shows the spec |
| 2 | The inserted spec body matches the owner-approved content | content hash equals the IP-1 packet `full_content_sha256` |
| 3 | The formal-artifact-approval packet exists and is bound to the spec | `.groundtruth/formal-artifact-approvals/2026-05-17-GOV-PROJECT-RETIREMENT-001.json` present; hash matches |
| 4 | The "VERIFIED work item" definition is bridge-coverage, not `resolution_status` | inspect the inserted spec body |

Execution: read the inserted spec from MemBase and compare its body hash to the approval packet; confirm the packet file. The post-implementation report's spec-to-test mapping additionally runs the existing governance-hook regression test (`python -m pytest platform_tests/hooks/test_formal_artifact_approval_gate.py`) to confirm the capture introduces no regression in the gate that admitted it.

## Clause Scope Clarification (Not a Bulk Operation)

This is NOT a bulk operation. Exactly one artifact (`GOV-PROJECT-RETIREMENT-001`) is created. There is no batch spec promotion, retirement, or inventory, and no work-item bulk operation. References to "work item", "backlog", and "project" describe the rule's subject matter, not a bulk backlog mutation. `GOV-STANDING-BACKLOG-001` bulk-operation clauses do not apply.

## Pre-Filing Preflight

Self-check per the file-bridge protocol's Mandatory Pre-Filing Preflight Subsection: the bridge applicability preflight run against this proposal's content returns `preflight_passed: true`, `missing_required_specs: []`, and `missing_advisory_specs: []`. Self-check packet_hash: `sha256:9969942dde06a5ce7a8a04a958bdf637da987d727119019a072bc0f97a38ee84`.

## Risks / Rollback

- Risk: the captured rule is not yet mechanically enforced (the audit found the backlog data cannot support enforcement). Mitigation: the spec body states this plainly as a known gap; it is rule-cited soft authority, consistent with other GT-KB GOV specs.
- Risk: the "VERIFIED work item" bridge-coverage definition depends on bridge-thread linkage that many work items lack. Mitigation: noted as follow-on data remediation; the spec is correct as stated and the enforcement DCL is deferred until the data supports it.
- Rollback: a `governance` spec is append-only; if retraction is needed it is superseded by a new version with an owner-approved change. The IP-1 packet may be retained as the audit record.

## Recommended Commit Type

`feat:` - captures a new governing specification (`GOV-PROJECT-RETIREMENT-001`) as a net-new MemBase governance artifact, with the formal-artifact-approval packet as the only changed file. No behavior code is added; the governance surface is new.

## Reviewer Context

The Codex (Loyal Opposition) harness is unavailable this session (cross-harness dispatch failed; the owner cannot reach the Codex harness). Per the owner's standing S357 directive, the Loyal Opposition review of this proposal will be performed by a fresh-context Claude Code agent acting as Loyal Opposition; the verdict will carry an explicit single-harness self-review disclosure, consistent with the `gtkb-impl-start-gate-finalization-quoting-fix` thread's `-008` and `-010`.
