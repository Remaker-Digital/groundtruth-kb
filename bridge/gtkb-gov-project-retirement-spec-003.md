REVISED

# Governance Capture Proposal (REVISED) - supersede GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 with v2 (automatic project completion and retirement)

bridge_kind: governance_review
Document: gtkb-gov-project-retirement-spec
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-17 UTC

target_paths: [".groundtruth/formal-artifact-approvals/2026-05-17-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v2.json", "groundtruth.db"]

This REVISED proposal supersedes `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` with an append-only version 2 that captures the owner's S357 governance directive: a backlog project is completed and retired automatically when all explicitly-linked work items are VERIFIED, with no owner AskUserQuestion confirmation. It replaces the NO-GO'd `-001`, which proposed a parallel new spec `GOV-PROJECT-RETIREMENT-001`. The owner selected the supersede-via-v2 mechanism via AskUserQuestion (S357). The implementation is one formal-artifact-approval packet plus one MemBase `specifications` insert (a new version of an existing spec); there is no source, test, hook, or configuration change in this thread.

## Response to Prior Verdict (NO-GO at -002)

Codex (Loyal Opposition) NO-GO'd `-001` with two P1 findings; both are resolved here.

- **F1 - omits and conflicts with the existing project-completion GOV.** `-001` proposed a new `GOV-PROJECT-RETIREMENT-001` that conflicted with the existing owner-approved `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` (which mandated owner-AUQ confirmation before retirement) without citing or reconciling it. Resolution: this REVISED no longer creates a parallel spec. It supersedes `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` with an append-only v2. The owner confirmed (S357 AskUserQuestion) that the S357 directive reverses the v1 owner-confirmation requirement, and selected supersede-via-v2 as the capture mechanism. `## Specification Links` now cites `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`; `## Prior Deliberations` cites `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` and corrects the prior false "no matching record" claim.
- **F2 - target_paths did not authorize the MemBase mutation.** `-001` listed only the approval-packet JSON in `target_paths`, but IP-2 inserts into `groundtruth.db`. Resolution: `target_paths` now includes `groundtruth.db`.

A third, non-blocking finding from the fresh-context review (F5 - the v1 draft's "there is no per-work-item retirement independent of its project" clause over-reached the owner directive) is also resolved: the v2 body states only the directive-supported "Retirement is collective: the project and its VERIFIED work items retire together."

## Owner Directive

Owner statement, session S357, 2026-05-17 (the project-retirement rule, verbatim intent): "The backlog is comprised of projects, which contain work items. When all of the work items within (associated with via explicit links) a backlog project are VERIFIED, the project is retired along with all of the VERIFIED work items associated with that project. As long as any work item associated with a project is not VERIFIED, the project cannot be retired."

Owner clarification, session S357, 2026-05-17 (the owner-AUQ boundary, verbatim): "Owner-AUQ confirmation is not required. Owner AUQ is required when starting a project, not when retiring one."

Owner clarification, session S357, 2026-05-17 (the retroactive-correction directive, verbatim): "We will have to retroactively populate and correct artifacts which were in-flight prior to this change. This is a best-effort attempt to provide retroactive continuity. It is a one-time cleanup to get unfinished work in a state that is appropriate for continuation as per this new governance implementation."

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` - the spec this proposal supersedes; v1 (owner-approved S350, 2026-05-14) required owner-AUQ confirmation before retirement; this proposal files v2 reversing that requirement per the S357 owner directive.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the project-start authorization governance; the v2 spec relocates the owner-AUQ boundary to project start, consistent with this spec.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - project-start governance; cited as the other half of the owner-AUQ-at-start boundary.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol observed; this proposal flows NEW -> NO-GO -> REVISED -> GO -> implement -> report -> VERIFIED.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Specification-Derived Verification Plan maps the acceptance criteria to verification commands.
- `GOV-ARTIFACT-APPROVAL-001` - filing a new version of a `governance` specification is a formal-artifact mutation; the formal-artifact-approval packet (IP-1) and explicit owner approval are required before canonical insertion.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - the formal-artifact-approval-gate PreToolUse hook gates the MemBase insert on the packet's presence and matching content hash.
- `GOV-STANDING-BACKLOG-001` - the captured rule governs the backlog (projects and their work items); the v2 spec refines the project-lifecycle dimension of the standing-backlog governance contract.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - advisory: the rule defines the gate for the project completion and retirement lifecycle transitions; the v2 spec is consistent with this constraint's lifecycle-state model.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the rule, the owner decisions, and the verification are preserved as durable bridge and MemBase artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - traceability is preserved across the owner directive, this thread, the audit, and the inserted spec version.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the target files (the approval packet and groundtruth.db) are in-root under the GT-KB project root; no application-tree paths.

This proposal files a new version of a `governance` specification; it does not modify source, tests, hooks, or configuration in this thread. The implementation correction of the project-completion machinery is separate follow-on work (see `## Consequences and Follow-On`).

## Prior Deliberations

The `-001` proposal's `## Prior Deliberations` asserted a Deliberation Archive search "returned no matching record - the rule is not previously archived." That claim was incorrect and is corrected here. The actual prior-decision history:

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` (owner_decision, 2026-05-14) - the owner directive that established the spec -> project -> work item -> bridge chain, including the verbatim clause "When completed implementation work is VERIFIED the backlog project is marked COMPLETED and is retired." Its AUQ record states the `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` variant was "Owner-confirmed via AUQ (no auto-transition)." The S357 directive reverses that owner-confirmation choice. This proposal supersedes the resulting spec via v2.
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v1 (specification, inserted 2026-05-14) - "VERIFIED-Driven Project Completion Requires Owner Confirmation." The artifact this proposal supersedes.
- `DELIB-1902` / `DELIB-1580` / `DELIB-1582` (`gtkb-backlog-work-list-retirement-directive-001` thread, VERIFIED) - a distinct concern: retirement of the `memory/work_list.md` file at migration conclusion, not the project-retirement lifecycle rule. Cited and distinguished; not a rejected approach.
- Owner directive + clarifications, S357 (2026-05-17) - the project-retirement rule, the owner-AUQ boundary correction, and the retroactive-correction directive (all quoted in `## Owner Directive`).
- S357 backlog audit (this session) - audited 138 active projects / 2125 work items against the rule; found `work_items.resolution_status` systematically stale (45 of 2125 carry `verified`, all legacy), bridge-thread VERIFIED coverage the true completion signal, and ~90% of work items unlinked from any project.
- Codex (Loyal Opposition) NO-GO at `bridge/gtkb-gov-project-retirement-spec-002.md` - the verdict this REVISED responds to.

## Owner Decisions / Input

This proposal depends on owner approval. The relevant owner directives and AskUserQuestion evidence:

- **Owner directive (S357, 2026-05-17):** the owner stated the project-retirement rule (quoted in `## Owner Directive`).
- **Owner clarification (S357):** owner-AUQ confirmation is not required for retirement; owner-AUQ gates project start, not retirement (quoted in `## Owner Directive`). This reverses the v1 owner-confirmation requirement.
- **Owner clarification (S357):** the retroactive-correction directive authorizing a one-time best-effort cleanup of in-flight artifacts (quoted in `## Owner Directive`).
- **Owner AskUserQuestion (S357) - VERIFIED criterion:** the owner selected the bridge-thread-coverage definition of a VERIFIED work item over the `resolution_status` field and over a reconciler-first path.
- **Owner AskUserQuestion (S357) - capture mechanism:** presented "Supersede via v2" vs. "New spec, retire old." The owner selected **"Supersede via v2"** - file an append-only v2 of `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`. This proposal implements that selection.

Per `GOV-ARTIFACT-APPROVAL-001`, IP-1 records this approval evidence in the formal-artifact-approval packet bound to the v2 content hash; canonical insertion (IP-2) is gated on that packet.

## Requirement Sufficiency

Existing requirements sufficient. The S357 owner directive and its two S357 clarifications are the operative requirement; this proposal captures them as version 2 of the existing `governance` specification. No new or revised requirement is required before implementation; the proposal is the capture of the requirement itself.

## Proposed Specification Content (GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 version 2)

The `governance` specification version to be inserted, as directed by the owner (S357):

- **ID:** `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` (new version 2 of the existing spec)
- **Type:** `governance`
- **Status:** `specified`
- **Title (v2):** VERIFIED-Driven Project Completion and Retirement Are Automatic (No Owner Confirmation)

**Rule.** A backlog project - and its project authorization - is completed and retired, together with all of the project's associated work items, automatically when, and only when, every work item explicitly linked to that project is VERIFIED. As long as any explicitly-linked work item is not VERIFIED, the project cannot be completed or retired. Completion and retirement require no owner AskUserQuestion confirmation; the transition is automatic on the all-work-items-VERIFIED condition. Retirement is collective: the project and its VERIFIED work items retire together.

**Owner-AUQ boundary.** Owner AskUserQuestion approval gates project start - the creation and approval of a project and its project authorization (see `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`). Owner-AUQ does not gate project completion or retirement. The owner-decision load for a project's lifecycle is incurred once, at start.

**Supersession (v1 -> v2).** Version 1 of this specification ("VERIFIED-Driven Project Completion Requires Owner Confirmation", owner-approved 2026-05-14, S350) required Prime Builder to surface project completion to the owner via AskUserQuestion and stated that auto-transition without owner confirmation is prohibited. Per the S357 owner directive (2026-05-17), that owner-confirmation gate is reversed: completion and retirement are automatic. The S350 owner-confirmed variant was itself chosen via AskUserQuestion at S350; S357 is the owner's superseding decision.

**"VERIFIED work item" definition.** A work item is VERIFIED when it is covered by a VERIFIED bridge thread - the bridge thread addressing the work item has reached terminal `VERIFIED` status in `bridge/INDEX.md`. The MemBase `work_items.resolution_status` field is explicitly not the criterion; the S357 backlog audit found it systematically stale. A work item with no bridge thread, or whose thread is at a non-terminal status, is not VERIFIED.

**"Explicitly linked" definition.** A work item is associated with a project via an explicit project-to-work-item membership link. Work items not explicitly linked to a project are not part of that project's completion and retirement gating set.

**Scope.** Projects and project authorizations where every explicitly-linked work item has a VERIFIED bridge thread. A project with any non-terminal linked work item remains active. Projects retired by explicit owner direction (without VERIFIED gating) follow the standard owner-directed retirement path and are outside this gate.

**Rationale.** Owner governance directive, S357 (2026-05-17). Automatic completion and retirement make a project's lifecycle a faithful, low-friction reflection of verified-complete work. The owner-decision load is placed at project start, where the owner authorizes scope; it is removed from retirement, where the all-work-items-VERIFIED condition is itself the decision.

**Rejected alternatives.** (1) Owner-confirmed retirement (the v1 rule) - reversed by S357; it placed an AskUserQuestion at every project completion. (2) Using `work_items.resolution_status == verified` as the VERIFIED criterion - rejected; the S357 audit proved that field systematically stale and unmaintained.

**Consequences.** (1) The project-completion machinery must complete and retire eligible projects automatically and must not gate the transition on an owner AskUserQuestion. (2) The S350-era owner-confirmation implementation - the project-completion-surface hooks, the project lifecycle module's completion and retirement functions, the project-retirement CLI path, and the project-verified-completion AUQ-trigger machinery - requires retroactive correction to the automatic model; this is tracked as separate follow-on implementation work. (3) One non-VERIFIED linked work item blocks the project's completion and retirement. (4) The rule's mechanical coverage depends on project-to-work-item link completeness; the S357 audit found most work items currently carry no project link, so backlog-data remediation is required before coverage is comprehensive - tracked separately.

**Related artifacts.** project_authorizations table; the project-retirement CLI; bridge/INDEX.md VERIFIED detection; the project-completion scanner and surface; `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` (project start, where owner-AUQ applies).

## Proposed Implementation

### IP-1: formal-artifact-approval packet

Create `.groundtruth/formal-artifact-approvals/2026-05-17-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v2.json` per `GOV-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001`: `artifact_type=governance`, `artifact_id=GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`, `action` reflecting a new-version mutation, `full_content` (the v2 spec body above), `full_content_sha256`, `presented_to_user=true`, `transcript_captured=true`, `explicit_change_request` (the S357 owner directive plus the supersede-via-v2 AskUserQuestion), `changed_by=prime-builder/claude/B`, `change_reason`, `approved_by=owner`.

### IP-2: MemBase insert (new version)

Insert version 2 of `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` into the MemBase `specifications` table (`type=governance`, `status=specified`) via the governed specification-creation path, with the IP-1 packet in place so the formal-artifact-approval-gate hook admits the write. The insert is append-only - v1 is retained as the prior version. `change_reason` cites this bridge thread, the S357 owner directive, and the supersession of v1.

### IP-3: no code, test, hook, or configuration change in this thread

This thread captures the governance rule only. The implementation correction of the project-completion machinery (Consequence 2) and the retroactive artifact continuity (the S357 retroactive-correction directive) are separate follow-on work, to be structured as a tracked correction project with its own bridge proposals. No source, test, hook, or configuration files are modified by this thread.

## Specification-Derived Verification Plan

De-facto specification: the S357 owner directive and its clarifications. The implementation is verified when version 2 of the spec faithfully records the directive.

| # | Acceptance criterion | Verification |
|---|---|---|
| 1 | `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` has a version 2 in MemBase with `type=governance`, `status=specified` | spec read via the KB API shows version 2 |
| 2 | The v2 body matches the owner-directed content | content hash equals the IP-1 packet `full_content_sha256` |
| 3 | The v2 rule states automatic completion and retirement with no owner-AUQ confirmation | inspect the inserted v2 body |
| 4 | v1 is retained (append-only); the insert did not overwrite it | spec version history shows both v1 and v2 |
| 5 | The formal-artifact-approval packet exists and is bound to the v2 content | the packet file is present; its `full_content_sha256` matches the v2 body |

Execution: read the inserted v2 spec and its version history from MemBase and compare the v2 body hash to the approval packet; confirm the packet file. The post-implementation report's spec-to-test mapping additionally runs the existing governance-hook regression test (`python -m pytest platform_tests/hooks/test_formal_artifact_approval_gate.py`) to confirm the capture introduces no regression in the gate that admits the insert.

## Consequences and Follow-On

The v2 spec changes the governance rule; the S350-era implementation built on the v1 rule must be retroactively corrected per the owner's S357 retroactive-correction directive. This is out of scope for this governance-capture thread and will be structured as a separate tracked correction project covering: the project-completion-surface hooks (Claude and Codex copies), the project lifecycle module's completion and retirement functions, the project-retirement CLI path, the project-verified-completion AUQ-trigger machinery, and the reconciliation of in-flight project authorizations, work items, and bridge threads currently in an awaiting-owner-confirmation state. Backlog-data remediation (project-to-work-item link completeness) is a further separate follow-on.

## Clause Scope Clarification (Not a Bulk Operation)

This is NOT a bulk operation. Exactly one artifact version is created (`GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v2). There is no batch spec promotion, retirement, or inventory, and no work-item bulk operation. References to "work item", "backlog", "project", and "retirement" describe the rule's subject matter, not a bulk backlog mutation. `GOV-STANDING-BACKLOG-001` bulk-operation clauses do not apply.

## Pre-Filing Preflight

Self-check per the file-bridge protocol's Mandatory Pre-Filing Preflight Subsection: the bridge applicability preflight run against this proposal's content returns `preflight_passed: true`, `missing_required_specs: []`, and `missing_advisory_specs: []`. Self-check packet_hash: `sha256:bcaab7604cc4566d7133ceb870a676ffcf216df8578e0ea478b8ca8316ab1a33`.

## Risks / Rollback

- Risk: the v2 spec changes the governance rule before the implementation is corrected, leaving a transient window where the live owner-confirmation machinery does not match the spec. Mitigation: Consequence 2 and `## Consequences and Follow-On` state this plainly; the implementation correction is the immediate next tracked project; the spec is the authority the correction implements against.
- Risk: superseding an owner-approved spec reverses a recorded S350 owner AUQ decision. Mitigation: the reversal is itself an explicit S357 owner directive plus an S357 supersede-via-v2 AskUserQuestion; the append-only v2 retains v1 and the full decision history.
- Rollback: a `governance` spec is append-only; if retraction is needed, v2 is superseded by a v3 with an owner-approved change. v1 is never destroyed.

## Recommended Commit Type

`feat:` - captures a new version of a governing specification (`GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v2) as a net-new MemBase governance artifact version, with the formal-artifact-approval packet as the only changed file on disk. No behavior code is added in this thread; the governance surface is updated.

## Reviewer Context

The Codex (Loyal Opposition) harness is not reachable for interactive use this session, but the cross-harness event-driven trigger remains operative: it dispatched Codex automatically on the `-001` filing and Codex produced the `-002` NO-GO. If the trigger dispatches Codex for this REVISED, that verdict is authoritative. If it does not, the Loyal Opposition review will be performed by a fresh-context Claude Code agent acting as Loyal Opposition, with an explicit single-harness self-review disclosure, consistent with the `gtkb-impl-start-gate-finalization-quoting-fix` thread.
