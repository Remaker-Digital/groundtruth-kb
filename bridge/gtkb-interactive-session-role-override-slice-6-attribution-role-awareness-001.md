NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S375-interactive-session-role-override-slice-6
author_model: Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI default reasoning, explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001
Project: PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
Work Item: WI-3476
target_paths: ["scripts/_kb_attribution.py", "platform_tests/scripts/test_kb_attribution_session_role.py"]

# GT-KB Interactive Session Role Override - Slice 6 - MemBase Attribution Role-Awareness

bridge_kind: prime_proposal

Document: gtkb-interactive-session-role-override-slice-6-attribution-role-awareness
Version: 001 (NEW)
Date: 2026-05-30 UTC

## Summary

Slice 6 of PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE - the resolver's third consumer. `scripts/_kb_attribution.py` currently derives the `changed_by` role from the DURABLE role (`_role_for_harness_id`). Slice 6 makes the role LABEL follow the resolved session role (marker > durable) when the owner has declared an interactive session role via `::init gtkb (pb|lo)`, satisfying owner S371 Decision 1 (full session override includes MemBase attribution).

The change is a **marker override layered on top of the existing fail-closed durable resolution**: the durable role must still resolve (the existing `RuntimeError` invariant that prevents mis-attribution is preserved), and a valid session-state marker overrides only the role label. When no marker is present, attribution is byte-identical to today.

Parent GO: `bridge/gtkb-interactive-session-role-override-scoping-004.md`. Resolver dependency VERIFIED: Slice 4 (`-004`, `scripts/session_role_resolution.py`). Marker dependencies VERIFIED: Slice 2 (writer), Slice 3 (SessionStart invalidation).

## Verified Premise (not redundant, unlike Slice 5)

Unlike Slice 5, the parent scoping's Slice 6 premise is correct. `resolve_changed_by` (`scripts/_kb_attribution.py:157`) resolves `<role>/<harness_name>` where `role = _role_for_harness_id(harness_id)` reads the DURABLE role from the role-assignments projection. So MemBase writes during an interactive LO session are currently attributed `prime-builder/claude` (durable) instead of `loyal-opposition/claude` (declared). Slice 6 corrects this.

## In-Root Boundary Affirmation

Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md`: both target files are in-root (`E:\GT-KB\scripts\`, `E:\GT-KB\platform_tests\scripts\`). The override reads the in-root marker (`.claude/session/active-session-role.json`) via the Slice 4 resolver. No `applications/<name>/` paths; no Agent Red live dependency; no out-of-root path.

## Proposed Change

### `scripts/_kb_attribution.py`

Add a marker-override helper and apply it in `resolve_changed_by` after the fail-closed durable role resolution:

```python
def _session_role_override(harness_name: str) -> str | None:
    """Return the declared interactive session role for attribution, or None.

    Per ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001 Decision 1, a declared
    interactive session role overrides the durable role for the attribution
    LABEL. Returns the marker role only when a valid marker won the shared
    resolver's interactive resolution; returns None for durable sources so the
    caller keeps the (fail-closed) durable role.

    Excluded in headless dispatch context (GTKB_BRIDGE_POLLER_RUN_ID present):
    durable role remains the attribution authority for dispatched work. (Slice 3
    already clears the marker at every SessionStart, so headless sessions have
    no marker; this guard makes the interactive-only intent explicit.)

    current_session_id is None in CLI/subprocess attribution context, so the
    resolver's marker_session_id_unverified branch applies; Slice 3 keeps the
    marker fresh-per-session. Fail-soft: any resolver error returns None (keep
    durable).
    """
    if os.environ.get("GTKB_BRIDGE_POLLER_RUN_ID"):
        return None
    try:
        from scripts.session_role_resolution import resolve_interactive_session_role

        role, source = resolve_interactive_session_role(
            PROJECT_ROOT, current_session_id=None, harness_name=harness_name
        )
    except Exception:
        return None
    if source in ("marker", "marker_session_id_unverified"):
        return role
    return None
```

In `resolve_changed_by`, after the existing fail-closed durable resolution:

```python
    role = _role_for_harness_id(harness_id)
    if not role:
        raise RuntimeError(...)  # UNCHANGED: fail-closed invariant preserved
    # Slice 6: a declared interactive session role overrides the durable role
    # for the attribution label (ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001
    # Decision 1). Falls back to the durable role when no valid marker.
    effective_role = _session_role_override(resolved) or role
    return f"{effective_role}/{resolved}"
```

`resolve_changed_by_or_none` is unchanged (it delegates to `resolve_changed_by`).

### NEW `platform_tests/scripts/test_kb_attribution_session_role.py`

Focused tests for the override (kept separate from the existing `test_kb_attribution.py` to stay within the GO'd target scope).

## Design Decisions (Codex Adjudication)

1. **Override layered on fail-closed durable, not a replacement.** The durable role must still resolve or `resolve_changed_by` raises (the 39-spec mis-attribution incident invariant). The marker only overrides the label when both a durable role AND a valid marker exist. Alternative (marker alone satisfies attribution even when durable is unresolved) would weaken the fail-closed invariant; rejected. Codex Review Ask 1.
2. **Headless guard (`GTKB_BRIDGE_POLLER_RUN_ID` absent).** The marker override is interactive-only; dispatched work stays durable-attributed. Belt-and-suspenders given Slice 3 clears the marker at SessionStart. Codex Review Ask 2.
3. **`current_session_id=None` in CLI context.** Attribution runs in CLI/subprocess context without the UserPromptSubmit payload, so the resolver's `marker_session_id_unverified` branch applies (accept the marker; Slice 3 keeps it fresh). Single-marker limitation: the marker reflects the most-recent interactive declaration; simultaneous multi-harness interactive sessions are out of scope (the marker is last-writer-wins, mitigated by Slice 3's per-SessionStart clear). Codex Review Ask 3.

## Specification Links

- `DCL-SESSION-ROLE-RESOLUTION-001` v1 - attribution consumes the shared resolver's interactive resolution (marker > durable).
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v1 - Decision 1 (full session override includes attribution) is the architectural source.
- `GOV-SESSION-ROLE-AUTHORITY-001` v1 - session-stated role is the attribution authority when declared; durable is the fallback and the fail-closed base.
- `bridge/gtkb-kb-attribution-harness-aware-004.md` (Codex GO) - the authority for the existing `resolve_changed_by` fail-closed contract this slice preserves.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root boundary affirmed above.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal is filed at `-001` NEW; the `bridge/INDEX.md` update inserts a `NEW:` entry at the top of a new document block; no bridge file deletion or in-place rewrite of prior versions.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this Specification Links section satisfies the linkage gate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the spec-to-test plan below maps each acceptance criterion to executable verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the Project Authorization / Project / Work Item triple in the header satisfies the linkage gate.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - covered by `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` (active v3; covers WI-3476 via active membership + explicit inclusion; allows source_code + tests).
- `GOV-ARTIFACT-APPROVAL-001` - this slice inserts no canonical artifact; it changes how the `changed_by` LABEL is computed, not the approval gates.
- `GOV-STANDING-BACKLOG-001` - single feature slice; not a bulk operation. See Clause Scope Clarification below.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory), `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory), `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` (parent GO).
- `bridge/gtkb-interactive-session-role-override-slice-4-axis2-role-awareness-004.md` (Slice 4 VERIFIED; the shared resolver this slice consumes).
- `bridge/gtkb-interactive-session-role-override-slice-3-sessionstart-marker-invalidation-004.md` (Slice 3 VERIFIED; SessionStart marker clearing that makes the headless guard belt-and-suspenders).

## Clause Scope Clarification (Not a Bulk Operation)

Per `GOV-STANDING-BACKLOG-001` bulk-ops clause-scope clarification: this slice adds one helper + one call-site change in `scripts/_kb_attribution.py` and one new test module. No backlog bulk operation, no work_items insert/update/retire/supersede, no project create/retire, no authorization change, no inventory artifact, no review-packet, no formal-artifact-approval packet. Evidence pattern tokens: single helper, marker override, no bulk, no backlog mutation.

## Prior Deliberations

- `DELIB-2507` - S371 owner directive + 6 AUQ architecture decisions; Decision 1 (full session override including attribution) directly authorizes this slice.
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` - parent GO; Slice 6 is the attribution consumer.
- `bridge/gtkb-kb-attribution-harness-aware-004.md` - the GO that established the fail-closed `resolve_changed_by` contract; Slice 6 preserves its invariant.
- `bridge/gtkb-interactive-session-role-override-slice-4-axis2-role-awareness-004.md` - Slice 4 VERIFIED; the shared resolver reused here.
- No prior deliberation made attribution follow a session-stated role; this is the first.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-SESSION-ROLE-RESOLUTION-001` + `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` Decision 1 + the parent GO fully specify the attribution role-awareness. The design decisions (override-on-fail-closed, headless guard, unverified branch) are derivable from the existing contracts and are flagged for Codex; they are not owner requirement gaps.

## Spec-Derived Verification Plan

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

| Acceptance criterion | Test | Expected |
|---|---|---|
| LO marker overrides durable PB in the changed_by label | `test_attribution_lo_marker_overrides_durable_pb` | `loyal-opposition/<harness>` despite durable PB |
| PB marker overrides durable LO | `test_attribution_pb_marker_overrides_durable_lo` | `prime-builder/<harness>` despite durable LO |
| no marker -> durable role (unchanged behavior) | `test_attribution_no_marker_uses_durable` | durable role label |
| invalid-role marker -> durable role | `test_attribution_invalid_marker_uses_durable` | durable role label |
| headless dispatch (env-var present) -> durable role even with a marker | `test_attribution_headless_ignores_marker` | durable role label |
| fail-closed preserved: no durable role -> RuntimeError even with a marker | `test_attribution_failclosed_when_no_durable_role` | raises RuntimeError |
| resolver error -> durable role (fail-soft override) | `test_attribution_resolver_error_uses_durable` | durable role label |

### Required verification commands (post-implementation report will show observed results)

```text
python -m ruff check scripts/_kb_attribution.py platform_tests/scripts/test_kb_attribution_session_role.py
python -m ruff format --check scripts/_kb_attribution.py platform_tests/scripts/test_kb_attribution_session_role.py
python -m pytest platform_tests/scripts/test_kb_attribution_session_role.py platform_tests/scripts/test_kb_attribution.py -q
```

Both ruff gates are run (Slice 2 NO-GO -006 lesson). The existing `test_kb_attribution.py` is run as a regression to confirm the no-marker path is unchanged.

## Acceptance Criteria

- Codex issues GO with confirmation that:
  - The marker override is layered on the fail-closed durable resolution (the `RuntimeError` invariant is preserved when no durable role resolves).
  - The headless guard correctly excludes dispatched work from the marker override.
  - The no-marker path is byte-identical to today (existing `test_kb_attribution.py` still passes).
- If GO, implement and file the post-implementation report carrying forward Spec Links + spec-to-test mapping + observed results for both ruff gates and both test modules + recommended Conventional Commits type.
- If NO-GO, revise via `-002 REVISED`.

## Risk and Rollback

- **Risk:** the override weakens the fail-closed invariant (a marker lets a write proceed when no durable role exists). **Mitigation:** the override is applied AFTER the fail-closed durable check; durable must still resolve. `test_attribution_failclosed_when_no_durable_role` asserts the RuntimeError persists.
- **Risk:** headless dispatch attribution incorrectly flips to a stale marker role. **Mitigation:** the `GTKB_BRIDGE_POLLER_RUN_ID` guard + Slice 3's SessionStart marker clear; `test_attribution_headless_ignores_marker` asserts durable wins under the env-var.
- **Risk:** the no-marker path regresses. **Mitigation:** existing `test_kb_attribution.py` run as regression; `_session_role_override` returns None on no-marker so the code path is identical.
- **Risk:** single-marker last-writer-wins under simultaneous multi-harness interactive sessions. **Accepted/documented:** out of scope; the marker is ephemeral and Slice 3 clears it per SessionStart. Noted in the design decisions for Codex.
- **Rollback:** remove `_session_role_override` and revert the one-line `effective_role` change; delete the test module. No state to unwind (read-only override).

## Owner Decisions / Input

This slice proceeds under `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` (active v3; covers WI-3476 via active project membership + explicit inclusion; cites `DELIB-2507`). Per `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` the project authorization removes per-slice direct AskUserQuestion overhead for bounded project work; per `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` the slice runs through the full bridge protocol. DELIB-2507 holds the 6 S371 owner decisions; Decision 1 (full session override, explicitly including attribution) directly authorizes this slice. The design decisions are engineering choices within the DCL-specified envelope and are routed to Codex review, not a new owner decision; no new owner AskUserQuestion is required.

## Codex Review Asks

1. Confirm the override-on-fail-closed-durable design preserves the `resolve_changed_by` mis-attribution invariant (durable must resolve; marker overrides only the label).
2. Confirm the headless guard (`GTKB_BRIDGE_POLLER_RUN_ID` absent) is the correct way to keep dispatched-work attribution durable.
3. Confirm the `current_session_id=None` / `marker_session_id_unverified` reliance is acceptable in CLI attribution context (Slice 3 keeps the marker fresh), and the single-marker limitation is acceptable to document.
4. Flag any specification this proposal should cite but does not.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
