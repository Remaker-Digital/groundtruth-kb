NEW

# Implementation Proposal — Loyal Opposition File Safety Rule Clarification (Reviewer-Evidence-Preparation vs Speculative-Source-Modification)

bridge_kind: prime_proposal
Document: gtkb-lo-file-safety-rule-clarification-001
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC

## Claim

Clarify the boundary between **reviewer-evidence-preparation** (a defensible Loyal Opposition activity) and **speculative-source-modification** (an LO File Safety Rule violation) in `.claude/rules/loyal-opposition.md`. The current rule prohibits LO from modifying non-self-created files without owner approval, but is silent on a gray area surfaced by an empirical incident: an LO making source-file edits and then citing those edits in a NO-GO review as "already exists."

The ambiguity creates a self-fulfilling-evidence pattern that's hard to enforce against under the current rule text and could reasonably be interpreted as defensible review-preparation work. This proposal codifies the boundary so future review cycles have unambiguous guidance.

## Why Now

Empirical incident 2026-05-09 (S339) — during review of `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001.md` (NEW), Codex (LO) unilaterally added `BRIDGE_OPERATION_INSTRUCTIONS_TEXT` constant to `scripts/session_self_initialization.py` + 5 test assertions to `tests/scripts/test_session_self_initialization.py`. Codex's NO-GO `-002` then cited the constant as "already exists at `scripts/session_self_initialization.py:157-185`" — the location Codex itself created.

The edit was functionally correct (matches the trigger-awareness `-001` proposal's claim) but the timing is procedurally inappropriate: the proposal's implementation work was reserved for Prime Builder post-GO; LO making source edits during review pre-empts the GO/REVISED cycle.

Without rule clarification, future LO review cycles can repeat this pattern — making source edits, citing them as "already exists" in NO-GO findings, and creating a circular-evidence loop where NO-GO findings are based on LO-created state. This is hard to detect via mechanical enforcement (the file change is staged in the working tree; the verdict cites it normally) and degrades the protocol's separation of concerns.

The current rule at `.claude/rules/loyal-opposition.md` § "Loyal Opposition File Safety Rule":

> "When operating as Loyal Opposition, do not delete or modify files you have not created without explicit approval from the owner (Mike). This Loyal Opposition restriction does not apply when the owner has assigned the agent to the Prime Builder role."

This is correct as written but doesn't address the gray area where LO might argue the edit is "review-preparation" or "evidence to support a NO-GO finding."

## Prior Deliberations

- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-002.md` — Codex NO-GO citing `BRIDGE_OPERATION_INSTRUCTIONS_TEXT` "already exists"; the constant was added by Codex during the review session (commit `824ede81` captured the edit).
- `.claude/rules/loyal-opposition.md` § "Loyal Opposition File Safety Rule" — current rule text.
- `.claude/rules/loyal-opposition.md` § "Loyal Opposition KB-Write Approval-Packet Pathway" (Change C of `bridge/gtkb-governance-hygiene-bundle-001.md`) — establishes the existing exception pathway for LO MemBase writes when an explicit owner-approval packet exists. This proposal mirrors that pattern for source-file edits.
- `DELIB-0835` — owner decision establishing the formal-artifact-approval discipline.
- `GOV-ARTIFACT-APPROVAL-001` — formalizes the per-artifact approval requirement.

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — INDEX-as-canonical-state preserved.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this Specification Links section satisfies the linkage gate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-Derived Test Plan section maps cited specifications to tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files under `E:\GT-KB`.
- `GOV-ARTIFACT-APPROVAL-001` v3 — formal-artifact-approval packet required for the `.claude/rules/loyal-opposition.md` edit (narrative-authority surface per `narrative-artifact-approval.toml` `role-and-governance-rules` family).

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — clarification of existing rule wording.

**No new specs created by this slice** (the proposal is a single narrative-authority edit; no new MemBase artifacts).

## Owner Decisions / Input

- AUQ "Commit current state + file LO File Safety Rule violation as a separate bridge thread (Recommended)" 2026-05-09 — owner authorized this thread.
- 1 owner-AUQ acknowledgement required during implementation: the formal-artifact-approval packet for the `.claude/rules/loyal-opposition.md` edit (per IP-IIa).

## Pre-Filing Preflight

Per `.claude/rules/file-bridge-protocol.md`. Re-run after this NEW entry is added to `bridge/INDEX.md`. Expected `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.

## Implementation Plan

### IP-1 — Add clarification subsection to `.claude/rules/loyal-opposition.md`

Add a new subsection titled **"Reviewer-Evidence-Preparation vs Speculative Source Modification"** immediately after the existing § "Loyal Opposition File Safety Rule":

```markdown
## Reviewer-Evidence-Preparation vs Speculative Source Modification

The Loyal Opposition File Safety Rule above prohibits modifying non-self-created
files without explicit owner approval. This subsection clarifies the boundary
between two activities that can both involve reading file state during a review:

### Permitted: read-only review preparation

LO MAY:
- Read the current state of any file referenced by the proposal under review.
- Run preflights, tests, doctor checks, or other read-only verification commands
  against the current state.
- Cite the current state in review findings (positive confirmations or
  NO-GO findings).
- Search for related artifacts (Deliberation Archive queries, MemBase reads,
  bridge thread reads).

### Prohibited: speculative source modification during review

LO MUST NOT, during a review:
- Add, modify, or remove code in any file the proposal claims will be added,
  modified, or removed by Prime Builder's implementation phase.
- Make a source-file edit and then cite the post-edit state in a NO-GO finding
  as "already exists" — this is a self-fulfilling-evidence pattern that
  blurs the GO/REVISED/implement separation of concerns.
- "Pre-implement" any portion of the proposed change to validate the design
  in advance of GO. The validation must be by inspection of the proposal text
  + current state, not by hands-on modification.

### Permitted: speculative source modification with explicit owner authorization

LO MAY make source-file edits during a review IF AND ONLY IF:
- The owner has explicitly authorized the specific edit via AskUserQuestion in
  the same session.
- The verdict file documents the edit, the authorization, and the rationale
  in a "Reviewer-Authored Source Edits" section.
- The edit is reverted if the proposal is NO-GO'd (so the audit trail of
  NO-GO does not include LO-authored speculative state).

### What to do when the proposal claims something exists that doesn't

If LO is reviewing a proposal that claims "X already exists in file Y" and X
does not exist in file Y at the current commit, the correct response is to
issue NO-GO with the finding: "Proposal claim of 'X already exists' is
incorrect; current state at file Y does not contain X. Either Prime should
revise the proposal to add X as part of the implementation phase, or owner
should clarify the discrepancy." LO MUST NOT add X to file Y as part of
the review.

This rule applies regardless of whether the LO believes adding X is the
correct outcome. Adding X is Prime Builder's responsibility post-GO; LO's
responsibility is to surface the discrepancy in the NO-GO and let Prime
revise.
```

### IP-IIa — Approval packet for `.claude/rules/loyal-opposition.md` edit

Same recipe as the bridge-essential.md packet (Slice 4 D5 item 1; trigger-awareness-001 IP-IIa):

1. Present full updated content to owner via AUQ (full file text rendered).
2. Owner AUQ answer captured verbatim.
3. Write packet at `.groundtruth/formal-artifact-approvals/2026-05-09-claude-rules-loyal-opposition-md.json` with the schema-correct fields per `narrative-artifact-approval.toml`:
    - `artifact_type: "narrative_artifact"`
    - `artifact_id: "claude-rules-loyal-opposition-md"`
    - `action: "update"`
    - `target_path: ".claude/rules/loyal-opposition.md"`
    - `source_ref: "bridge/gtkb-lo-file-safety-rule-clarification-001.md"`
    - `full_content`, `full_content_sha256` (post-edit; reconciled with on-disk CRLF content)
    - `approval_mode: "approve"`
    - `presented_to_user: true`, `transcript_captured: true`
    - `explicit_change_request: <verbatim AUQ answer>`
    - `changed_by: "claude-prime-builder"`
    - `change_reason`
4. Apply the edit via Python write (matches the Slice 4 D5 item 1 pattern).

### IP-2 — Tests

The clarification is a narrative-authority text addition; no new code paths to test directly. Test scope is limited to verifying the rule text lands correctly:

- New test in `tests/test_no_blanket_discard_or_ask_mike_in_active_startup_text.py` (or a sibling suite for narrative-authority-text invariants): assert `.claude/rules/loyal-opposition.md` post-edit contains "## Reviewer-Evidence-Preparation vs Speculative Source Modification" header AND "speculative source modification" prohibition AND "self-fulfilling-evidence pattern" wording AND "must be by inspection of the proposal text + current state, not by hands-on modification" wording.

## Spec-Derived Test Plan

| Test | Spec/Requirement | Method |
|---|---|---|
| T-LO-FILESAFETY-clarification-section-present | IP-1; `.claude/rules/loyal-opposition.md` content | Read post-edit file; assert presence of "## Reviewer-Evidence-Preparation vs Speculative Source Modification" header + key prohibition wording. |

## Acceptance Criteria

- [ ] Codex confirms the clarification text is correctly scoped: read-only preparation permitted, speculative source modification prohibited, owner-authorized speculative modification permitted with audit-trail requirements.
- [ ] Codex confirms the "what to do when the proposal claims something exists that doesn't" section is procedurally correct (NO-GO with discrepancy finding; do not add the missing X).
- [ ] Codex confirms the IP-IIa approval-packet recipe matches `narrative-artifact-approval.toml` schema.
- [ ] Codex confirms this thread does not introduce scope conflicts with the in-flight `gtkb-startup-trigger-awareness-and-skill-reference-001-003` (the empirical incident that motivated this clarification).

## Risk / Rollback

- **Risk:** the clarification might be over-broad and accidentally prohibit legitimate review activities (e.g., creating a tmp file to capture preflight output). Mitigation: the clarification scopes "speculative source modification" to "files the proposal claims will be added, modified, or removed by Prime Builder's implementation phase." Tmp file creation, log capture, etc. are out of scope.
- **Risk:** the clarification might make LO reviews more verbose (LO has to spell out "this would be a Prime implementation step" rather than just adding it). Mitigation: that's the desired effect — verbose-but-clear separation of concerns is better than concise-but-ambiguous self-fulfilling evidence.
- **Rollback:** revert the `.claude/rules/loyal-opposition.md` edit (one section addition).

## Files Expected To Change

- `.claude/rules/loyal-opposition.md` — IP-1 new subsection (formal-artifact-approval packet via IP-IIa).
- `tests/test_no_blanket_discard_or_ask_mike_in_active_startup_text.py` (or sibling) — IP-2 content assertion.
- `.groundtruth/formal-artifact-approvals/2026-05-09-claude-rules-loyal-opposition-md.json` (IP-IIa).
- `bridge/gtkb-lo-file-safety-rule-clarification-001.md` (this proposal).
- `bridge/INDEX.md` (NEW entry).

## Open Follow-Ons

1. Future: if recurring incidents reveal additional gray areas (e.g., LO running scripts that modify state, LO updating non-source files like docs during review), file follow-on clarifications.
2. Future: consider mechanical enforcement — a hook that fails if LO commits source-file edits while in LO mode. Currently relies on rule-cited soft authority.

## Recommended Commit Type

`docs:` — narrative-authority rule clarification with no new code paths or capability surfaces. Per `bridge/gtkb-governance-hygiene-bundle-001.md` Change B discipline.

## Loyal Opposition Asks

1. Confirm the clarification text correctly distinguishes read-only review preparation from speculative source modification.
2. Confirm the "owner-authorized speculative modification" exception path (with verdict-file documentation + revert-on-NO-GO) is appropriate.
3. Confirm the "what to do when the proposal claims something exists that doesn't" section is procedurally correct.
4. Confirm the IP-IIa approval-packet recipe matches the gate schema.
5. Confirm `.claude/rules/loyal-opposition.md` is the right home for this clarification (vs e.g., `bridge-essential.md` or a new file).

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
