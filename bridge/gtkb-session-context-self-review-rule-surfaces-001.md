NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-automation-keep-working-2026-06-18T10-50Z
author_model: gpt-5-codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation session; Prime Builder

# Session-Context Bridge Self-Review Boundary Rule-Surface Proposal

bridge_kind: prime_proposal
Document: gtkb-session-context-self-review-rule-surfaces
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4597

target_paths: [".claude/rules/file-bridge-protocol.md",".claude/rules/codex-review-gate.md",".claude/rules/loyal-opposition.md",".claude/rules/prime-builder-role.md","AGENTS.md","CLAUDE.md","config/agent-control/SESSION-STARTUP-INDEX.md","config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md","config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md","bridge/gtkb-session-context-self-review-rule-surfaces-*.md"]

implementation_scope: governance_rule_surface_clarification
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Formalize the bridge self-review boundary on durable rule and startup instruction surfaces so agents do not confuse same-harness continuity with same-session self-review.

The implemented dispatcher and test behavior already treat review independence as session-context based. `cross_harness_bridge_trigger.py` refuses a reviewer only when the latest bridge artifact `author_session_context_id` equals the current `reviewer_session_context_id`. `test_cross_harness_bridge_trigger.py` also states that same-harness authorship is not self-review when session context differs. The remaining gap is that durable human-facing rule and prompt surfaces do not say this clearly enough, leaving future agents to rely on transient handoff notes.

This proposal is documentation and rule-surface clarification only. It does not authorize changes to dispatcher logic, reviewer selection, harness registry semantics, bridge state storage, or implementation-start authorization behavior.

## Evidence

- The dispatcher source at line 1431 parses `author_session_context_id` from the latest bridge artifact metadata.
- The dispatcher source at line 1439 refuses only when `author_session_context_id == reviewer_session_context_id`.
- The cross-harness trigger regression suite defines `test_lo_ordered_fallback_allows_same_harness_author_different_session`.
- That regression states that same-harness authorship is not self-review when session context differs.
- `gt backlog show WI-4597 --json` records this as a May29 Hygiene P2 item with no dependencies and scope limited to rule/spec/doc/prompt clarification.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge review and implementation authorization depend on correct file-bridge authority semantics.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes PAUTH, project, work item, and target path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing bridge, session-role, project-authorization, and artifact-governance surfaces.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must map wording changes to focused rule-surface scans and existing dispatch regression coverage.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the May29 Hygiene project authorization permits Prime Builder to advance unimplemented project work through the bridge protocol.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - protected rule/root/startup-surface edits must still wait for Loyal Opposition GO and a live implementation-start packet.
- `GOV-SESSION-ROLE-AUTHORITY-001` - interactive session-role authority and headless dispatch routing are distinct authority surfaces and must not be conflated.
- `DCL-SESSION-ROLE-RESOLUTION-001` - resolved session role governs in-session behavior, while headless routing remains keyed to durable role assignment.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - dispatch envelope behavior depends on author and reviewer session metadata.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher/status/health surfaces must preserve bridge routing semantics without hidden same-harness prohibitions.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target surfaces remain inside the GT-KB project root and no Agent Red external repository surface is in scope.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the clarification preserves a durable rule artifact instead of relying on transient session notes.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the change aligns code, tests, deliberations, and rule surfaces.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this WI and proposal capture a discovered governance/rule-surface drift item through the bridge lifecycle.

## Prior Deliberations

- `DELIB-2195` - owner decision: bridge proposal reviews require an unrelated session context from the proposal author context; same-session self-review is prohibited, but a single harness may carry both roles when the review occurs in an unrelated session context.
- `DELIB-2196` - owner decision: interactive sessions may act only in the owner-declared role; this must remain distinct from headless dispatch eligibility.
- `DELIB-20264294` - Loyal Opposition GO for LO review dispatch reliability, explicitly approving session-context-based review independence and rejecting same-harness-only refusal.
- `DELIB-20263083` - GO example where the proposal and verdict were both harness A but had different session contexts, with an explicit same-session guard.
- `DELIB-20264446` - GO example documenting same-harness continuity as a caution rather than a blocker when session contexts differ.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION` is active for proposals covering unimplemented work items linked to `PROJECT-GTKB-MAY29-HYGIENE`.
- `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` is the owner-decision evidence for that project authorization.
- `DELIB-2195` and `DELIB-2196` are existing owner decisions establishing the session-context and declared-role boundaries this proposal will clarify.
- No new owner decision is required. This proposal formalizes existing owner decisions and existing implemented behavior on durable surfaces.

## Requirement Sufficiency

Existing requirements sufficient. The owner decisions in `DELIB-2195` and `DELIB-2196`, the active May29 Hygiene PAUTH, and the current dispatch test behavior are enough to clarify the rule surfaces. The implementation must not create or mutate formal MemBase specifications, ADRs, DCLs, or GOV records unless a separate formal-artifact approval path already exists.

If any target surface requires narrative or formal artifact approval evidence before write, the implementation must obtain and cite that packet. This proposal does not waive approval gates; it only requests Loyal Opposition review of the intended scoped wording update.

## In-Root Placement Evidence

All implementation targets are under the E:/GT-KB project root. The bridge proposal, implementation report, and any later verdict files for this thread remain under the E:/GT-KB bridge directory. The proposal and future report use numbered, versioned bridge files in an append-only chain; no prior bridge version may be deleted or rewritten. No live path outside E:/GT-KB is in scope.

## Proposed Implementation

1. Update the bridge protocol and Codex review-gate rule surfaces to state the normative boundary: bridge review is invalid only when the reviewer session context is the same as the artifact author session context, or when author session metadata is missing/unreadable according to fail-closed dispatcher rules.
2. State explicitly that same harness ID alone is not a self-review blocker when author and reviewer session contexts are unrelated and the reviewer is operating under a valid Loyal Opposition role or dispatch context.
3. Preserve the interactive-role boundary: an interactive session may not switch roles merely because it has a durable role assignment; a separately launched headless or fresh session context is the eligible review context when role and dispatch rules allow it.
4. Align root and startup instruction surfaces only where they currently leave this to transient handoff notes. Do not introduce new dispatcher behavior or alter protected implementation-start semantics.
5. Keep the wording concise and rule-level. Avoid adding operational shortcuts, hook bypasses, or any claim that same-harness review is always valid.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SCOPE-001 | Yes | Restrict edits to the listed rule/root/startup surfaces and this bridge thread. | `git diff --name-only` and implementation-start packet target-path validation. | No waiver. |
| CQ-TESTS-001 | Yes | Run the existing cross-harness dispatch regression that proves same-harness/different-session eligibility. | the focused cross-harness dispatch pytest selector for same-harness/different-session and self-review cases. | No waiver. |
| CQ-LINT-001 | Conditional | If Python tests are edited, run `ruff check` and `ruff format --check` on the edited Python file. | Report exact command output in the implementation report when applicable. | Not applicable for docs-only implementation. |

## Spec-Derived Verification Plan

| Specification / governing surface | Verification command or evidence | Expected result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | the bridge applicability preflight for this bridge id | `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | the ADR/DCL clause preflight for this bridge id | Exit 0 with no blocking gaps. |
| `GOV-SESSION-ROLE-AUTHORITY-001`, `DCL-SESSION-ROLE-RESOLUTION-001`, `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` | `python -m pytest test_cross_harness_bridge_trigger.py -q --tb=short -k "same_harness_author_different_session or self_review"` | Regression proves same-harness/different-session review eligibility and same-session refusal behavior remain intact. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Text scan over target surfaces for `same-session`, `session context`, and `same harness` language. | Durable rule/startup/root surfaces now state the boundary without relying on transient handoff notes. |
| `CQ-SCOPE-001` | scoped git diff name-only review over the approved target paths | Only approved target surfaces changed. |
| Formatting hygiene | git diff whitespace check over changed approved target paths | Exit 0. |

## Acceptance Criteria

- Durable rule/root/startup surfaces distinguish same-session self-review from same-harness continuity.
- The clarified rule states that same harness ID alone is not a review blocker when session contexts are unrelated and role/dispatch rules are satisfied.
- The clarified rule preserves fail-closed handling for missing or unreadable author session metadata.
- Interactive sessions remain bound to the owner-declared role and do not gain permission to self-review by citing durable role assignment.
- No dispatcher/source behavior changes are made under this proposal.

## Risk / Rollback

Risk is wording drift: a too-broad clarification could accidentally imply that same-harness review is always valid, or that interactive sessions may switch roles. The implementation should use the existing source/test behavior as the wording anchor.

Rollback is a normal git revert of the rule/root/startup wording changes and any bridge report created by the implementation cycle. Do not revert unrelated concurrent workspace changes.

## Bridge Filing

This proposal should be filed through the governed Codex bridge writer for this slug. Before implementation, Prime Builder must wait for Loyal Opposition GO and create a fresh implementation-start packet for this bridge id.

## Recommended Commit Type

`docs:` - rule/root/startup instruction wording only; no source behavior change is proposed.
