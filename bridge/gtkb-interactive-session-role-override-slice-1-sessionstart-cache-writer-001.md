NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S371-interactive-session-role-override-slice-1
author_model: Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI default reasoning, explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001
Project: PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
Work Item: WI-3453

# GT-KB Interactive Session Role Override - Slice 1 - SessionStart Cache Writer

bridge_kind: implementation_proposal

Document: gtkb-interactive-session-role-override-slice-1-sessionstart-cache-writer
Version: 001 (NEW)
Date: 2026-05-29 UTC

## Summary

First implementation slice of the architecture-first plan approved by Codex GO at `bridge/gtkb-interactive-session-role-override-scoping-004.md`. This slice modifies `_write_role_scoped_startup_relay_caches` in BOTH `.claude/hooks/session_start_dispatch.py` and `.codex/gtkb-hooks/session_start_dispatch.py` so SessionStart unconditionally generates the `-pb.md` and `-lo.md` startup-disclosure caches regardless of the harness's durable role set. The change is byte-similar in both dispatchers; tests assert parity.

This is Slice 1 of 10. It is independent of other slices and unblocks the UserPromptSubmit init-keyword matcher's keyword-keyed cache lookup for either role, which fixes the symptomatic owner-typed `::init gtkb lo` to harness B (durable PB) defect at the disclosure-relay layer.

## In-Root Boundary Affirmation

Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md`: all touched files are in-root (`E:\GT-KB\.claude\hooks\`, `E:\GT-KB\.codex\gtkb-hooks\`, `E:\GT-KB\scripts\`, `E:\GT-KB\platform_tests\`). No `applications/<name>/` paths; no Agent Red live dependency.

## Problem Statement

`_write_role_scoped_startup_relay_caches` currently iterates the harness's durable role set (returned by `_resolve_own_role_set()`) when deciding which alternate-role startup-disclosure caches to write. For a singleton role set like `{pb}` (harness B's durable role), the loop never iterates `lo`, so the `last-user-visible-startup-lo.md` cache is never written. When the owner types `::init gtkb lo`, the UserPromptSubmit init-keyword matcher (`scripts/workstream_focus.py` `_startup_relay_pointer`) looks up the LO cache, finds it missing, and emits the startup-relay-failure diagnostic.

The defect exists symmetrically in `.codex/gtkb-hooks/session_start_dispatch.py:497-514` for the Codex harness.

## Proposed Change

Replace the iteration source in `_write_role_scoped_startup_relay_caches` from `_resolve_own_role_set()` to the keys of `_MODE_TO_ROLE_PROFILE` (which is `{"pb": "prime-builder", "lo": "loyal-opposition"}` in both dispatchers). The loop then unconditionally renders and writes the alternate-role cache regardless of the harness's durable role set.

Pseudocode of the new body:

```python
def _write_role_scoped_startup_relay_caches(additional_context: str) -> None:
    marker = "## User-Visible Startup Message"
    body = (
        additional_context.split(marker, 1)[1].strip()
        if marker in additional_context
        else additional_context.strip()
    )
    primary_mode = _startup_body_role_mode(body)
    if primary_mode:
        _write_startup_relay_cache(body, role_mode=primary_mode)
    # Per DCL-SESSION-ROLE-RESOLUTION-001 assertion 5 + ADR-INTERACTIVE-
    # SESSION-ROLE-OVERRIDE-001 Decision 2: both caches generated
    # unconditionally so the keyword-keyed cache lookup succeeds for either
    # role regardless of durable role set.
    for mode in sorted(_MODE_TO_ROLE_PROFILE.keys()):
        if mode == primary_mode:
            continue
        report = _render_role_startup_report(_MODE_TO_ROLE_PROFILE[mode])
        if report:
            _write_startup_relay_cache(report, role_mode=mode)
```

The `_render_role_startup_report` helper imports the shared `scripts.session_self_initialization` `build_startup_model` + `render_report`, which is harness-agnostic; no change to the shared module is required in Slice 1.

Identical change applied to `.codex/gtkb-hooks/session_start_dispatch.py`.

## Specification Links

- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v1 (operative; Decision 2 mandates both caches unconditionally generated).
- `DCL-SESSION-ROLE-RESOLUTION-001` v1 (operative; assertion 5 is the deterministic ephemerality contract that the cache-generation change supports; this Slice 1 specifically lands the cache writer change, not the marker work).
- `GOV-SESSION-ROLE-AUTHORITY-001` v1 (operative; governance boundary).
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v2 (operative; the receiver-side decision table now includes INTERACTIVE_OVERRIDE_AUTHORIZED, which depends on the keyword-matched cache existing).
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v2 (operative; receiver-side semantics updated).
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - both dispatchers receive the byte-similar change to honor parity.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - blocking applicability spec; in-root boundary affirmed above.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal is filed under `bridge/` at -001 NEW per the bridge protocol; INDEX update inserts a new entry at the top of `bridge/INDEX.md` (after the header comments); no prior versions are deleted or rewritten.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) - this slice does not transition any artifact lifecycle state itself; the spec lifecycle transitions for the v1/v2 artifacts inserted today (e.g., `specified` to `implemented`) happen at the post-implementation report turn, not this NEW filing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this Specification Links section satisfies the linkage gate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the test plan below maps each acceptance criterion to executable verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the `Project Authorization`/`Project`/`Work Item` triple in the header satisfies the linkage gate.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - covered by `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` (active; includes WI-3453 via project membership; includes the 5 specs above explicitly).
- `GOV-ARTIFACT-APPROVAL-001` - this slice does not insert new canonical artifacts; it implements a behavior already governed by the v1/v2 artifacts inserted earlier today under DELIB-2507.
- `GOV-STANDING-BACKLOG-001` - this slice is a single behavior change, not a bulk operation; see `## Clause Scope Clarification` below.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) - the change implements the artifact-mediated authority split.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) - same.
- `DCL-CONCEPT-ON-CONTACT-001` - no new load-bearing terms introduced by Slice 1; `session-stated role` lands in Slice 9.
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` (GO) - parent scoping authority.

## Clause Scope Clarification (Not a Bulk Operation)

Per `GOV-STANDING-BACKLOG-001` bulk-ops clause-scope clarification: this slice modifies a single helper function in two dispatcher files plus its symmetric Codex counterpart, lands tests, and updates no backlog or work-item bulk surfaces. It is a single behavior change. Evidence pattern: tokens include "single function", "byte-similar", "no bulk", "no backlog mutation".

## Prior Deliberations

- `DELIB-2507` (S371 owner directive + 6 AUQ architecture decisions; owner-decision DELIB for PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001).
- `bridge/gtkb-interactive-session-role-override-scoping-003.md` (REVISED-1 scoping) and `-004.md` (Codex GO).
- `bridge/gtkb-canonical-init-keyword-syntax-001-007.md` (Codex GO at -008) - the deliberation chain establishing `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`.
- `bridge/gtkb-claude-session-start-parity-001.md` (Codex GO at -002) - the deliberation chain that introduced the Claude SessionStart dispatcher's current shape; this slice extends it.
- No prior deliberation has touched the role-set iteration source in `_write_role_scoped_startup_relay_caches`; this is the first behavior change to that loop.

## Requirement Sufficiency

Existing requirements sufficient. ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001 Decision 2 + DCL-SESSION-ROLE-RESOLUTION-001 assertion 5 + the parent scoping GO at -004 fully specify the cache-generation behavior. No new owner clarification required for Slice 1.

## target_paths

- `.claude/hooks/session_start_dispatch.py` (modify `_write_role_scoped_startup_relay_caches`; ~10 lines changed)
- `.codex/gtkb-hooks/session_start_dispatch.py` (byte-similar change to `_write_role_scoped_startup_relay_caches`; ~10 lines changed)
- `platform_tests/hooks/test_session_start_dispatch_role_cache.py` (NEW; parameterized over Claude + Codex dispatchers)

No other files are touched. No rule-file edits in this slice; rule updates land in Slice 9. No shared `scripts/session_self_initialization.py` edits required (the existing `build_startup_model` + `render_report` is harness-agnostic and accepts arbitrary `role_profile`).

**No KB/MemBase mutation in Slice 1.** `groundtruth.db` is NOT in target_paths because this slice performs no `db.insert_*`, `db.update_*`, `db.retire_*`, or any other groundtruth.db write. The ADR/DCL/GOV v1 + SPEC/DCL v2 artifacts that govern this slice were inserted/updated in the preceding scoping turn (today, S371) under `DELIB-2507`'s formal-artifact-approval evidence; they exist in MemBase already and are read-only references to this slice. The runtime startup-disclosure caches `last-user-visible-startup-*.md` written by `_write_startup_relay_cache` are NOT MemBase rows; they are ephemeral filesystem files under `.claude/hooks/` (Claude) or `.codex/gtkb-hooks/` (Codex), not in `groundtruth.db`.

## Spec-Derived Verification Plan

| Acceptance criterion | Verification |
|---|---|
| Harness B (durable PB) SessionStart writes both `last-user-visible-startup-pb.md` and `last-user-visible-startup-lo.md` plus matching metadata sidecars | unit test invoking `_write_role_scoped_startup_relay_caches` with a fixture body whose body indicates Prime-Builder; assert both files present with valid metadata |
| Harness A (durable LO) SessionStart writes both caches | parameterized fixture flipping the durable role; same assertion |
| Metadata sidecar `role_mode` field is `pb` for the `-pb.md` cache and `lo` for the `-lo.md` cache regardless of which harness is running | inspect metadata after write; assert exact match |
| Parity: same fixture run against `.codex/gtkb-hooks/session_start_dispatch.py._write_role_scoped_startup_relay_caches` produces equivalent output | fixture imports both modules; asserts symmetric file output |
| `_render_role_startup_report` failure mode (returns None) does not raise; the missing cache is skipped silently | fixture monkeypatches the renderer to return None for one role; assert the other cache is still written and no exception |
| Pre-existing caches from a prior session are overwritten cleanly | fixture pre-writes corrupt caches; assert post-call content matches expected |
| Existing tests in `platform_tests/hooks/test_session_start_dispatch.py` continue to pass (regression) | run full test module before and after the change |

## Acceptance Criteria

- Codex issues GO on this implementation proposal with explicit confirmation that:
  - The change to `_write_role_scoped_startup_relay_caches` is byte-similar in both dispatchers.
  - The test parameterization adequately covers both dispatchers.
  - No other behavior is changed (e.g., `_bridge_dispatch_keyword_check` is untouched; STRICT_DROP unchanged).
- If GO, the implementation lands as the Slice 1 post-implementation report (`-002` NEW carrying forward Spec Links).
- If NO-GO, revise via `-002` REVISED per Codex findings (no in-place edit of `-001`).

## Risk and Rollback

- **Risk:** Unconditional cache generation slows SessionStart by ~one extra `render_report` call when the alternate-role cache is fresh. **Mitigation:** the alternate-role render is purely additive and the `render_report` call is already invoked by the primary-mode path; cost is one extra in-memory render + one extra small file write. Slice 1 acceptance includes a timing assertion (informational) confirming the additional cost is bounded.
- **Risk:** A test that asserts the durable-role-only loop behavior would regress. **Mitigation:** searched for such tests; none found in `platform_tests/hooks/` or `tests/scripts/`. If one surfaces during Codex review, it will be updated as part of this slice.
- **Risk:** Codex dispatcher and Claude dispatcher diverge over time. **Mitigation:** Slice 8 (later) updates `scripts/check_codex_hook_parity.py` to enforce parity; until then, the test parameterization in Slice 1 surfaces drift.
- **Rollback:** revert the two function bodies to their previous form. The marker file design (Slices 2-3) and AXIS 2 changes (Slice 4) are not landed yet, so Slice 1's rollback does not require unwinding any state.

## Owner Decisions / Input

This implementation slice proceeds under the project-scoped authorization `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` (active; includes WI-3453 via project membership; cites `DELIB-2507` as the owner-decision deliberation). Per `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, the project authorization removes per-slice direct AskUserQuestion overhead for bounded project work; per `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`, this slice still runs through the bridge protocol (Codex GO required before implementation; post-implementation report required before VERIFIED).

DELIB-2507 captures the 6 owner AskUserQuestion decisions from S371 (Override scope; Undeclared default; Role persistence; Declaration UX; Landing path; Disclosure presentation) and the 7th post-GO batch-authorization decision. Source: AskUserQuestion turn-by-turn in session S371; owner-decision-tracker hook recorded each to `memory/pending-owner-decisions.md`.

No new owner AskUserQuestion is required for Slice 1: the behavior is already specified by ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001 Decision 2, DCL-SESSION-ROLE-RESOLUTION-001 assertion 5, and the GO'd scoping plan at `bridge/gtkb-interactive-session-role-override-scoping-004.md`.

## Codex Review Asks

1. Confirm or NO-GO the byte-similar change pattern across both dispatchers.
2. Confirm or NO-GO the test parameterization approach (fixture imports both modules; asserts symmetric output) vs an alternative (separate test files per dispatcher).
3. Confirm or NO-GO that no existing test asserts the durable-role-only loop behavior such that this change would regress.
4. Flag any specification this proposal should cite but does not.
5. Confirm or NO-GO that `scripts/session_self_initialization.py` (shared `build_startup_model` + `render_report`) requires no change in Slice 1.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
