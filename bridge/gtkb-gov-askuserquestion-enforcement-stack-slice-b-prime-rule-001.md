NEW

# Implementation Proposal — GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice B: Prime Builder Rule Formalizing AUQ-Only Decision Channel

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-04 (S331)
**Type:** Sub-slice B of GTKB-GOV-AUQ-ENFORCEMENT-STACK (umbrella scoping at `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md`, Codex GO at -004)
**Mechanism:** 1 (per umbrella sub-slice plan: AUQ-only rule)
**Risk tier:** Low (rule-file additions; no runtime/code changes)
**Authorization:** S331 AUQ #3 "Autonomous progression"; umbrella -004 GO; Sub-slice A VERIFIED at `-014`.

---

## Background

Per the umbrella's sub-slice plan, Sub-slice B is the formal rule declaration that AskUserQuestion is the ONLY valid channel for owner-decision asks. Sub-slice A (VERIFIED at `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md`) provides the mechanical enforcement (Stop-mode block emission with tightened regex). Sub-slice B provides the declarative rule contract that proposals/reports cite when claiming owner-approved scope. Sub-slice C (forthcoming) will add the bridge-compliance-gate hook check that mechanically enforces citation of this rule for proposals claiming owner approval.

Current state of `.claude/rules/prime-builder-role.md` (read 2026-05-04 in this session) describes Prime Builder authority, interrogative default, and bridge-protocol compliance, but does NOT include an explicit AskUserQuestion-only-decision-channel declaration. Sub-slice B adds that section.

## Specification Links

Cross-cutting specs required by `config/governance/spec-applicability.toml` for any bridge proposal:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified) — Live bridge index authority. Compliance: this proposal lives at `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-001.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — Sub-slice B does NOT create files under `applications/`; it modifies `.claude/rules/` files only.

Topic-specific:

- Umbrella scoping: `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md` (Codex GO at -004).
- Sub-slice A precedent: `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md` (VERIFIED). Sub-slice B's rule cites Sub-slice A's enforcement infrastructure.
- `GOV-OWNER-DECISION-SURFACING-001` (verified per S315) — Source rule for owner-decision surfacing; Sub-slice B extends with channel declaration.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` (relevant per work_list row 21) — Chat-derived spec approval contract.
- `.claude/rules/prime-builder-role.md` — Target of modification (extension only; no removal).
- `.claude/rules/acting-prime-builder.md` — Target of modification (extension only; no removal).
- `.claude/rules/file-bridge-protocol.md` — Bridge protocol; Sub-slice C extends this; Sub-slice B references it as the Owner Decisions / Input section consumer.
- `.claude/rules/codex-review-gate.md` — Pre-implementation review obligation.
- `.claude/rules/deliberation-protocol.md` — Pre-proposal deliberation-search obligation.
- `.claude/rules/project-root-boundary.md` — Sub-slice B operates entirely within `E:/GT-KB/`.

Advisory specs:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified)

The proposed tests in the Test Plan section derive from these linked specs as follows: rule declaration → T-rule-content (file content assertion: AUQ-only declaration text present in both rule files); rule-citation contract → T-rule-citation-fixture (synthetic proposal fixture with + without citation; presence/absence detected); placement contract → T-out-of-applications-B (no `applications/` content introduced); platform smoke → T-platform-smoke (no regression).

## Prior Deliberations

| DELIB | Source | Outcome | Relevance |
|-------|--------|---------|-----------|
| Implicit S315 owner directive | owner_conversation | owner_decision | Source rule for owner-decision surfacing |
| S331 AUQ #1, #2, #3 | owner_conversation | owner_decision | Umbrella priority + scope + autonomy |
| Codex umbrella -004 GO | bridge_thread | go | Sub-slice B authorized |
| Sub-slice A VERIFIED at `-014` | bridge_thread | verified | Mechanical enforcement infrastructure live; Sub-slice B's declarative rule cites it |

## Goal

Add an explicit AUQ-only-decision-channel declaration to `.claude/rules/prime-builder-role.md` and `.claude/rules/acting-prime-builder.md` that:

1. States AskUserQuestion is the ONLY valid channel for owner-decision asks.
2. Lists the in-scope decision classes: approvals, waivers, priority choices, formal artifact approvals, requirement clarifications, destructive actions, deployments, and other blocking owner decisions.
3. Cites Sub-slice A's mechanical enforcement infrastructure (`.claude/hooks/owner-decision-tracker.py` block emission).
4. References the canonical pattern: `Owner Decisions / Input` section in proposals/reports (which Sub-slice C will mechanically gate via bridge-compliance-gate).
5. States that prose decision-asks are invalid — they are detected by the Stop-mode hook and blocked from turn-end.

## Implementation Plan

### Step 1: Add AUQ-only section to `.claude/rules/prime-builder-role.md`

Append a new section after the existing "Operational implications" bullet list:

```markdown
## AskUserQuestion as the Only Valid Owner-Decision Channel

(Active per S331 owner directive; mechanically enforced by `.claude/hooks/owner-decision-tracker.py` per `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md` VERIFIED.)

Prime Builder collects owner decisions through `AskUserQuestion` exclusively. Prose decision-asks are invalid:

- The Stop-mode hook detects prose decision-ask patterns (`PROSE_DECISION_PATTERNS`) and emits `{"decision": "block", ...}` to refuse turn-end when no `AskUserQuestion` tool_use occurred in the same turn (per `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md` VERIFIED + Sub-slice A tightening).
- All accepted owner decisions are recorded in `memory/pending-owner-decisions.md` with `detected_via: ask_user_question`.

In-scope decision classes (use `AskUserQuestion`, never prose):

- Approvals: implementation proposals that depend on owner approval beyond the bridge protocol's standing GO/NO-GO cycle.
- Waivers: explicit owner waivers of governance gates (e.g., release gates, scoped-change discipline).
- Priority choices: multi-option priority/scoping decisions.
- Formal artifact approvals: GOV/SPEC/ADR/DCL/PB/REQ creation, promotion, or mutation.
- Requirement clarifications: ambiguous owner statements about scope, behavior, or intent.
- Destructive actions: delete/overwrite/reset operations that the destructive-gate hook flags.
- Deployments: production-environment changes.
- Blocking owner decisions: any decision the agent cannot proceed without.

Bridge proposals/reports that depend on owner approval should cite this rule and include an `Owner Decisions / Input` section enumerating the AskUserQuestion answers that authorize the work. Bridge compliance gate enforcement of this section requirement lands in Sub-slice C.

When in doubt, ask via `AskUserQuestion`. Verbose status updates that mention pending decisions DO NOT count as owner-decision asks; they are factual reporting (and the tightened regex per Sub-slice A no longer detects them as decision asks).
```

### Step 2: Add equivalent declaration to `.claude/rules/acting-prime-builder.md`

Append a parallel section to `.claude/rules/acting-prime-builder.md`. The acting-prime-builder rule is the role-mapping abstraction that applies whichever harness is currently assigned Prime Builder; same AUQ-only contract applies. (Implementation reads the existing file content first to identify the appropriate insertion point and preserve existing structure.)

### Step 3: Commit on develop

Single commit on `develop` branch with message:

```
gtkb-gov-auq-enforcement-stack Slice B: Prime Builder rule formalizes AUQ-only decision channel

Adds AskUserQuestion-only-decision-channel declaration to:
- .claude/rules/prime-builder-role.md
- .claude/rules/acting-prime-builder.md

Cites Sub-slice A's mechanical enforcement (block emission active).
Lists in-scope decision classes: approvals, waivers, priority choices,
formal artifact approvals, requirement clarifications, destructive
actions, deployments, blocking owner decisions.

Refs: bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md (Slice A VERIFIED);
bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-001.md (this proposal).
```

## Specification-Derived Test Plan

| Test ID | Spec Coverage | Procedure | Expected Result |
|---------|---------------|-----------|-----------------|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` | `grep "Document: gtkb-gov-askuserquestion-enforcement-stack-slice-b" bridge/INDEX.md` | Match present |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule` | `preflight_passed: true`, `missing_required_specs: []` |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | post-impl REPORT contains spec links + spec-to-test mapping + executed commands + observed results | Codex VERIFIED contingent |
| **T-out-of-applications-B** | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff <Sub-B-baseline>..<Sub-B-VERIFIED-commit> --name-only \| grep "^applications/"` | Empty (no `applications/` content) |
| **T-rule-content-prime** | rule declaration contract | `grep -c "AskUserQuestion as the Only Valid Owner-Decision Channel" .claude/rules/prime-builder-role.md` | `1` |
| **T-rule-content-acting** | rule declaration contract | `grep -c "AskUserQuestion as the Only Valid Owner-Decision Channel" .claude/rules/acting-prime-builder.md` | `1` (or equivalent declaration heading) |
| **T-rule-cites-slice-a** | rule cites Sub-slice A's mechanical enforcement | `grep -c "gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014" .claude/rules/prime-builder-role.md` | `1` (rule references Sub-slice A's VERIFIED bridge) |
| **T-rule-lists-decision-classes** | rule enumerates in-scope decision classes | `grep -c "approvals\|waivers\|priority choices\|formal artifact approvals\|requirement clarifications\|destructive actions\|deployments\|blocking owner decisions" .claude/rules/prime-builder-role.md` | `≥ 1` (at least one bullet per class; the regex matches multiple lines) |
| **T-platform-smoke** | platform integrity | `python -m pytest groundtruth-kb/tests/ -x --tb=line -q -k "rule or owner_decision or hook" --timeout=60` | PASS (or pre-existing-known failures only) |

Test commands include `python -m pytest`, `python scripts/bridge_applicability_preflight.py`, `git`, `grep` to satisfy the spec-derived-testing-mandatory regex.

## Specification-to-Test Mapping

| Specification clause | Test ID(s) | Coverage |
|---------------------|------------|----------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | T-bridge-1 | Direct |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | T-spec-1 | Direct |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | T-spec-2 | Direct |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | T-out-of-applications-B | Direct |
| Rule declaration in prime-builder-role.md | T-rule-content-prime | Direct |
| Rule declaration in acting-prime-builder.md | T-rule-content-acting | Direct |
| Rule cites Sub-slice A's mechanical enforcement | T-rule-cites-slice-a | Direct |
| Rule lists in-scope decision classes | T-rule-lists-decision-classes | Direct |
| Platform integrity | T-platform-smoke | Direct |

Every required spec has direct test coverage.

## Acceptance Criteria

- [ ] Codex GO on this Sub-slice B proposal
- [ ] Preflight passes (T-spec-1)
- [ ] Rule declaration text reviewed for clarity and scope completeness

VERIFIED when:

- [ ] All 9 tests T-bridge-1 through T-platform-smoke PASS with command output captured in post-impl REPORT
- [ ] Codex VERIFIED on the post-impl REPORT
- [ ] Both rule files contain the AUQ-only declaration (T-rule-content-prime + T-rule-content-acting)
- [ ] Rule cites Sub-slice A's VERIFIED bridge (T-rule-cites-slice-a)
- [ ] Rule lists in-scope decision classes (T-rule-lists-decision-classes)
- [ ] No regression in GT-KB platform tests (T-platform-smoke)

## Risk / Rollback

| Risk | Likelihood | Impact | Mitigation |
|------|-----------:|-------:|------------|
| Rule additions conflict with existing rule structure | Low | Low | Insertion at end of "Operational implications" preserves existing content; no removal |
| Sub-slice C bridge gate (forthcoming) doesn't recognize the section heading format | Low | Low | Sub-slice C will define the exact heading pattern; Sub-slice B uses a heading that's machine-discoverable (level-2 `## AskUserQuestion as the Only Valid Owner-Decision Channel`) |
| Rule wording over-restricts genuine cases (e.g., status reports incorrectly classified as decisions) | Medium | Low | Wording explicitly notes "Verbose status updates that mention pending decisions DO NOT count as owner-decision asks" |
| Pre-existing pytest failures interfere | Medium | Low | T-platform-smoke uses focused `-k` filter; pre-existing failures documented per Sub-slice A precedent |

Rollback: `git revert` of the single commit reverses both rule additions atomically.

## Open Questions

| ID | Question | Resolution |
|----|----------|------------|
| OQ-B-1 | Heading style for AUQ-only section? | `## AskUserQuestion as the Only Valid Owner-Decision Channel` (level-2 markdown heading; machine-discoverable for Sub-slice C bridge gate) |
| OQ-B-2 | Should the rule cite Sub-slice C's forthcoming gate? | No — Sub-slice C will update both rules to add the bridge-gate citation when its own scope lands |

## Owner Decisions / Input

This sub-slice's authorization derives from S331 AskUserQuestion answers (umbrella priority + scope + autonomy) and Sub-slice A's VERIFIED enforcement infrastructure. No additional owner input pending at sub-slice level.

## Out of Scope

- Bridge-compliance-gate hook check for `Owner Decisions / Input` section presence (Sub-slice C scope).
- Codex-side rule updates in `.claude/rules/loyal-opposition.md` for the bridge gate (Sub-slice C scope).
- Audit pass over `memory/pending-owner-decisions.md` historical entries (Sub-slice D).
- Implementing the requirements-collection hook (Sub-slice E).
- Adding release-metric doctor checks (Sub-slice F).
- Resolution of pre-existing scaffold-golden fixture mismatch.

## Project Root Boundary Compliance

Operates entirely within `E:/GT-KB/`. Targets `.claude/rules/prime-builder-role.md` and `.claude/rules/acting-prime-builder.md`. No `applications/` content. Per `.claude/rules/project-root-boundary.md`.

## Provenance

| Source | Reference |
|--------|-----------|
| Umbrella scoping | `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md` (REVISED-1 at GO -004) |
| Sub-slice A VERIFIED | `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md` |
| Source DELIB (S315 owner-decision surfacing) | `bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md` VERIFIED |
| Source DELIB (S331 enforcement directive) | This conversation: 3 AUQ answers (priority + scope + autonomy) |
| Live probes | `head` of `.claude/rules/prime-builder-role.md` (executed 2026-05-04 in this session) |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
