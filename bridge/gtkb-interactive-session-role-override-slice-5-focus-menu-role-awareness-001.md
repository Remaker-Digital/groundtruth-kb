NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S375-interactive-session-role-override-slice-5
author_model: Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI default reasoning, explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001
Project: PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
Work Item: WI-3475
target_paths: ["platform_tests/scripts/test_startup_focus_role_awareness.py"]

# GT-KB Interactive Session Role Override - Slice 5 - Focus-Menu Role-Awareness (Verification-Only; Redundancy Finding)

bridge_kind: implementation_proposal

Document: gtkb-interactive-session-role-override-slice-5-focus-menu-role-awareness
Version: 001 (NEW)
Date: 2026-05-30 UTC

## Summary

Slice 5 of PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE. Investigation found that the behavior Slice 5 was scoped to deliver - the session focus menu following the resolved session role - is **already delivered by Slice 1** (VERIFIED). This proposal is therefore a **verification-only** slice: it adds one focused regression test that locks in the role-branching the focus-menu role-awareness depends on, makes no source change, and documents the redundancy finding for Codex adjudication.

Owner AUQ S375 chose "verify-and-close" after I surfaced the finding.

## Finding: Slice 5's Scoped Change Is Already Delivered by Slice 1

The GO'd parent scoping (`...-scoping-003.md`) defined Slice 5 as: "Surface: `scripts/workstream_focus.py` startup-focus menu generation. Change: Resolve role per `DCL-SESSION-ROLE-RESOLUTION-001` for focus-menu shape selection." The premise was that the focus menu is a separate `workstream_focus.py` surface needing its own role-aware change.

Investigation (this session) shows the premise is incorrect:

1. **The PB/LO session focus menu is generated in `scripts/session_self_initialization.py`, not `scripts/workstream_focus.py`.** `_session_focus_options` / `_render_session_focus_options` build the A/B/C/D "Recommended Session Focus" selector; `workstream_focus.py` renders only the role-agnostic "Active Work Subject" block (GT-KB vs application, bridge role slot, topology).

2. **The focus menu already branches by role.** `session_self_initialization.py:_is_loyal_opposition_model(model)` (line 4126) discriminates the role, and `_render_loyal_opposition_startup_task(model)` (line 4154) renders LO-specific startup content. Line 4159 is the literal focus-menu role-awareness: *"Session-focus menu: not presented in Loyal Opposition mode; numbered focus choices are Prime Builder startup controls."* So a Prime Builder session shows the numbered focus menu; a Loyal Opposition session suppresses it with an explanatory line.

3. **Slice 1 already delivers the role-correct disclosure.** Slice 1's `_write_role_scoped_startup_relay_caches` calls `build_startup_model(role_profile="prime-builder")` and `build_startup_model(role_profile="loyal-opposition")`, generating both caches. Empirical confirmation in the live workspace: `.claude/hooks/last-user-visible-startup-pb.md` is 11,330 bytes ("Role being assumed: Prime Builder") and `.claude/hooks/last-user-visible-startup-lo.md` is 17,255 bytes ("Role being assumed: Loyal Opposition", carrying the LO startup task with the focus-menu-suppression line). When the owner declares `::init gtkb lo`, the UserPromptSubmit init-keyword matcher renders the `-lo` cache - so the focus menu is already role-correct for the declared session role.

Conclusion: Slice 5's intended behavior (focus menu follows the resolved session role) is delivered by the combination of `session_self_initialization.py`'s existing role-branching + Slice 1's dual-cache. No `workstream_focus.py` change is needed. The owner-directed interactive surfaces are: disclosure (Slice 1), AXIS 2 (Slice 4), focus menu (this finding: covered by Slice 1), attribution (Slice 6, pending), AUQ-routing.

## Verification-Only Scope (Owner AUQ S375: verify-and-close)

This slice adds a single focused regression test that ties the focus-menu role-awareness to the session-role-override feature, so the role-branching cannot silently regress without a Slice-5-owned test failing. It is deliberately lightweight (pure-function assertions over a minimal model dict) to avoid the heavy/flaky `build_startup_model` path (the Slice 1 lesson). No source change.

### NEW `platform_tests/scripts/test_startup_focus_role_awareness.py`

- `test_is_loyal_opposition_model_discriminates`: a minimal model `{"role": {"assumed_role": "Loyal Opposition"}}` -> True; `{"role": {"assumed_role": "Prime Builder"}}` -> False; empty/absent -> False. Locks in the role discriminator that selects LO-specific rendering.
- `test_lo_startup_task_suppresses_focus_menu`: `_render_loyal_opposition_startup_task({})` contains the focus-menu-suppression line ("Session-focus menu: not presented in Loyal Opposition mode"). Locks in the focus-menu role-awareness contract.
- `test_pb_and_lo_role_rendering_differs`: asserts the LO startup task text is non-empty and differs from the PB framing (the LO task is the role-specific content the `-lo` cache carries that the `-pb` cache does not).

## In-Root Boundary Affirmation

Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md`: the single target file is in-root (`E:\GT-KB\platform_tests\scripts\`). No `applications/<name>/` paths; no Agent Red live dependency; no out-of-root path.

## Specification Links

- `DCL-SESSION-ROLE-RESOLUTION-001` v1 - the focus menu follows the resolved session role; this slice verifies the existing role-branching that delivers it.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v1 - Decision 1 (full session override includes the focus menu) is satisfied by Slice 1 + the existing role-branching; this slice locks it in.
- `GOV-SESSION-ROLE-AUTHORITY-001` v1 - session-stated role is the focus-menu authority via the rendered cache.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root boundary affirmed above.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal is filed at `-001` NEW; the `bridge/INDEX.md` update inserts a `NEW:` entry at the top of a new document block; no bridge file deletion or in-place rewrite of prior versions.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this Specification Links section satisfies the linkage gate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the spec-to-test plan below maps the verification to executable tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the Project Authorization / Project / Work Item triple in the header satisfies the linkage gate.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - covered by `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` (active v3; covers WI-3475 via active membership + explicit inclusion; allows tests).
- `GOV-ARTIFACT-APPROVAL-001` - this slice inserts no canonical artifact.
- `GOV-STANDING-BACKLOG-001` - single verification slice; not a bulk operation. See Clause Scope Clarification below.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` (advisory) - the redundancy finding aligns with avoiding duplicate role-resolution work; the focus menu is delivered once (Slice 1), not re-implemented.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory), `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory), `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` (parent GO).
- `bridge/gtkb-interactive-session-role-override-slice-1-sessionstart-cache-writer-007.md` (Slice 1 VERIFIED; delivers the role-correct dual-cache that makes the focus menu role-aware).
- `bridge/gtkb-interactive-session-role-override-slice-4-axis2-role-awareness-004.md` (Slice 4 VERIFIED; the prior consumer slice).

## Clause Scope Clarification (Not a Bulk Operation)

Per `GOV-STANDING-BACKLOG-001` bulk-ops clause-scope clarification: this slice adds one test module and makes no source change. No backlog bulk operation, no work_items insert/update/retire/supersede, no project create/retire, no authorization change, no inventory artifact, no review-packet, no formal-artifact-approval packet. Evidence pattern tokens: verification-only, single test, no source change, no bulk, no backlog mutation.

## Prior Deliberations

- `DELIB-2507` - S371 owner directive + 6 AUQ architecture decisions; Decision 1 (full session override including the focus menu) is the authority the finding confirms is satisfied by Slice 1.
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` - parent GO; Slice 5 was scoped here with the (now-corrected) `workstream_focus.py` premise.
- `bridge/gtkb-interactive-session-role-override-slice-1-sessionstart-cache-writer-007.md` - Slice 1 VERIFIED; the dual-cache that delivers the role-aware focus menu.
- Owner AUQ S375 (this session) - "verify-and-close" disposition after the redundancy finding was surfaced.
- No prior deliberation distinguished the focus menu's actual home (`session_self_initialization.py`) from `workstream_focus.py`; this finding corrects the scoping record.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-SESSION-ROLE-RESOLUTION-001` + `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` Decision 1 fully specify the focus-menu role-awareness, which is already delivered. Owner AUQ S375 specifies the verify-and-close disposition. No new owner requirement gathering is required.

## Spec-Derived Verification Plan

| Acceptance criterion | Test | Expected |
|---|---|---|
| role discriminator selects LO rendering for an LO model | `test_is_loyal_opposition_model_discriminates` | LO->True, PB->False, empty->False |
| focus menu is suppressed in LO mode (role-aware) | `test_lo_startup_task_suppresses_focus_menu` | LO task text contains "Session-focus menu: not presented in Loyal Opposition mode" |
| PB and LO role rendering differ | `test_pb_and_lo_role_rendering_differs` | LO task text non-empty and not equal to the PB framing |

### Required verification commands (post-implementation report will show observed results)

```text
python -m ruff check platform_tests/scripts/test_startup_focus_role_awareness.py
python -m ruff format --check platform_tests/scripts/test_startup_focus_role_awareness.py
python -m pytest platform_tests/scripts/test_startup_focus_role_awareness.py -q
```

Both ruff gates (lint + formatter) are run per the Slice 2 NO-GO -006 lesson that they are distinct gates.

## Acceptance Criteria

- Codex issues GO with explicit adjudication of the redundancy finding: confirm Slice 5's scoped behavior is delivered by Slice 1 + the existing `session_self_initialization.py` role-branching, and that a verification-only slice (no `workstream_focus.py` change) is the correct disposition - OR NO-GO directing a real change if Codex identifies a role-dependent surface I missed.
- If GO, implement the test and file the post-implementation report carrying forward Spec Links + spec-to-test mapping + observed results for both ruff gates and the test + recommended Conventional Commits type.
- If NO-GO, revise via `-002 REVISED`.

## Risk and Rollback

- **Risk:** the finding is wrong and there IS a real role-dependent `workstream_focus.py` surface. **Mitigation:** Codex Review Ask 1 invites NO-GO with the missed surface; the evidence (focus menu home, the LO-suppression line, the 17.2KB vs 11.3KB caches) is documented for independent verification.
- **Risk:** the regression test couples to an exact string ("Session-focus menu: not presented...") that could be reworded. **Mitigation:** acceptable - if that line is reworded, the test should be updated alongside (the focus-menu role-awareness contract is exactly what we want to guard); the test documents the contract.
- **Rollback:** delete the test module. No source change to revert.

## Owner Decisions / Input

This slice proceeds under `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` (active v3; covers WI-3475 via active project membership + explicit inclusion; cites `DELIB-2507`). Per `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` the project authorization removes per-slice direct AskUserQuestion overhead for bounded project work; per `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` the slice runs through the full bridge protocol.

**Owner AUQ S375** (this session) authorized the verify-and-close disposition: after I surfaced the evidence-backed finding that Slice 5's scoped behavior is already delivered by Slice 1, the owner chose "Verify-and-close (Recommended)" - add a focused regression test, make no `workstream_focus.py` change, and mark WI-3475 covered. DELIB-2507 Decision 1 remains the underlying authority for the focus-menu role-awareness itself. No further owner decision is required.

## Codex Review Asks

1. **Redundancy finding adjudication:** confirm Slice 5's scoped behavior (focus menu follows resolved role) is delivered by Slice 1 + `session_self_initialization.py`'s existing role-branching, and that a verification-only slice is correct - OR NO-GO with the role-dependent `workstream_focus.py` surface I missed.
2. Confirm the regression test meaningfully guards the focus-menu role-awareness contract.
3. Flag any specification this proposal should cite but does not.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
