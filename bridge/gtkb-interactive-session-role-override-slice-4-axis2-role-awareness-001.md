NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S374-interactive-session-role-override-slice-4
author_model: Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI default reasoning, explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001
Project: PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
Work Item: WI-3474
target_paths: ["scripts/session_role_resolution.py", ".claude/hooks/bridge-axis-2-surface.py", "platform_tests/hooks/test_session_role_resolution.py", "platform_tests/hooks/test_bridge_axis_2_role_aware.py"]

# GT-KB Interactive Session Role Override - Slice 4 - AXIS 2 Role-Awareness + Shared Session-Role Resolver

bridge_kind: implementation_proposal

Document: gtkb-interactive-session-role-override-slice-4-axis2-role-awareness
Version: 001 (NEW)
Date: 2026-05-30 UTC

## Summary

Slice 4 of PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE - the first marker-CONSUMER slice. It (1) introduces `scripts/session_role_resolution.py`, the single deterministic implementation of `DCL-SESSION-ROLE-RESOLUTION-001`'s interactive resolution (marker > durable), and (2) wires `.claude/hooks/bridge-axis-2-surface.py` to resolve the session-stated role and surface the matching actionable work (Prime-actionable for a PB session, Loyal-Opposition-actionable for an LO session) under a role-aware heading.

Today the AXIS 2 hook hard-codes the Prime-actionable element of `compute_actionable_pending` (which returns `(actionable_for_prime, actionable_for_codex)`) and renders "Newly-Actionable Prime Work" unconditionally, discarding the LO element. After Slice 4, an interactive owner who declared `::init gtkb lo` (Slice 2 wrote the marker; Slice 3 ensures it is fresh-per-session) sees LO-actionable work instead - satisfying owner S371 Decision 1 (full session override includes the AXIS 2 surface).

Parent GO: `bridge/gtkb-interactive-session-role-override-scoping-004.md`. Dependencies VERIFIED: Slice 2 (`-008`, marker writer + schema), Slice 3 (`-004`, SessionStart invalidation).

## Scope Expansion Flag (Codex Adjudication Required)

The GO'd parent scoping (`...-scoping-003.md`) named Slice 4's surface as **`.claude/hooks/bridge-axis-2-surface.py` only**. This proposal expands that surface to also introduce the shared resolver module `scripts/session_role_resolution.py` (plus its test module). Rationale:

- The parent plan's Slices 4, 5, 6, and 7 each say "resolve role per `DCL-SESSION-ROLE-RESOLUTION-001` (marker > durable)", but **no slice was allocated to create that resolver**. It is an implicit shared capability the plan assumed.
- Implementing the resolution table inline in four consumers is a four-site drift hazard for a DCL explicitly titled "Session Role Resolution Deterministic Rules" - a single source of truth is the correct architecture and aligns with `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`.
- Slice 4 is the first consumer, so it is the natural place to introduce the resolver.

This is a code-organization decision within a DCL-specified behavioral envelope (the resolver's behavior is fully specified by the DCL; no owner ambiguity), so it is routed to Codex review rather than an owner AskUserQuestion. **Codex Review Ask 1** invites the alternatives: (a) approve the expanded scope as proposed; (b) NO-GO and direct me to split the resolver into a small predecessor thread that Slices 4-7 then consume; (c) NO-GO and direct an inline-then-extract approach. The PAUTH (`PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`) covers `source_code` + `tests` for the project, so the expanded file set remains within the project authorization envelope; only the per-slice surface naming is at issue.

## In-Root Boundary Affirmation

Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md`: all four target files are in-root (`E:\GT-KB\scripts\`, `E:\GT-KB\.claude\hooks\`, `E:\GT-KB\platform_tests\hooks\`). The resolver reads the in-root marker at `.claude/session/active-session-role.json` and the in-root durable role map. No `applications/<name>/` paths; no Agent Red live dependency; no out-of-root path.

## Problem Statement

The AXIS 2 in-session surface (`.claude/hooks/bridge-axis-2-surface.py`) is role-blind: `_compute_prime_actionable()` (line ~89) uses only `actionable_prime` from `compute_actionable_pending`, and `_render_surface` (line ~167) hard-codes "Prime Work". An interactive LO session therefore still gets Prime-actionable bridge work surfaced, contradicting the owner-declared session role. Slice 4 makes the surface follow the resolved session role.

## Proposed Change

### NEW `scripts/session_role_resolution.py` - deterministic resolver

Implements the interactive rows of `DCL-SESSION-ROLE-RESOLUTION-001` (the `GTKB_BRIDGE_POLLER_RUN_ID`-absent rows; the env-var-present headless rows remain owned by the SessionStart dispatchers and are out of scope here).

```python
ROLE_PRIME = "prime-builder"
ROLE_LO = "loyal-opposition"
_VALID_ROLES = frozenset({ROLE_PRIME, ROLE_LO})
# Must equal scripts.workstream_focus._SESSION_ROLE_MARKER_NAME (Slice 2);
# a parity test asserts equality so the read target cannot drift from the
# write target.
_SESSION_ROLE_MARKER_NAME = "active-session-role.json"


def resolve_interactive_session_role(
    project_root: Path,
    *,
    current_session_id: str | None = None,
    harness_name: str = "claude",
) -> tuple[str, str]:
    """Return (role_profile, source).

    role_profile is in {prime-builder, loyal-opposition}. Resolution (marker >
    durable) per DCL-SESSION-ROLE-RESOLUTION-001 interactive rows:

    - marker absent / unreadable        -> (durable, "durable_marker_absent")
    - marker role not in valid set      -> (durable, "durable_marker_invalid_role")   # assertion 7
    - current_session_id given and marker session_id mismatches
                                        -> (durable, "durable_marker_stale_session")   # assertion 6
    - current_session_id given and matches
                                        -> (marker_role, "marker")
    - current_session_id is None (unavailable)
                                        -> (marker_role, "marker_session_id_unverified")

    The session-id-unverified branch accepts the marker because Slice 3 deletes
    the marker at every SessionStart, so a marker present mid-session belongs to
    the current session; the session-id check is defense-in-depth for the case
    where SessionStart invalidation silently failed. Codex Review Ask 3 invites
    a stricter reject-on-unverified contract if preferred.
    """
```

Durable fallback uses a **read-only** durable-role lookup (no role-map mutation): resolve the harness id (`bootstrap_missing=False`), load the role assignments, and return `primary_role(record)` (Prime-first; defaults to `loyal-opposition` for an empty record). The resolver never writes the role map and never writes the marker.

### `.claude/hooks/bridge-axis-2-surface.py` - wire to resolver

- Generalize `_compute_prime_actionable()` to `_compute_actionable_for_role(role_profile)`: select `actionable_for_prime` (element 0) when `role_profile == ROLE_PRIME`, else `actionable_for_codex` (element 1). The signature is computed over the selected role's items, so suppression/dismissal keys off the correct role's signature.
- `_render_surface(items, role_profile)`: heading becomes "Newly-Actionable Prime Work" for PB and "Newly-Actionable Loyal Opposition Work" for LO; the dismissal/disable footer is unchanged.
- `_user_prompt_handler`: resolve the role via `resolve_interactive_session_role(PROJECT_ROOT, current_session_id=<raw payload session_id>, harness_name="claude")` and thread `role_profile` through compute + render. The raw payload `session_id` (not the sanitized cache-key form) is passed so the marker session-id comparison is like-for-like with the Slice 2 writer's stored raw id.

No change to the cache/suppression/dismissal mechanics, the `GTKB_NO_AXIS_2_SURFACE` disable, or the fail-soft error logging.

### NEW test modules

- `platform_tests/hooks/test_session_role_resolution.py` - resolver unit tests (marker>durable precedence, role-set-membership invalidation, session-id staleness, session-id-unverified acceptance, durable fallback variants, path parity with the Slice 2 writer).
- `platform_tests/hooks/test_bridge_axis_2_role_aware.py` - AXIS 2 wiring tests (PB marker -> Prime element + Prime heading; LO marker -> Codex element + LO heading; no marker -> durable role; signature keys off resolved-role items).

## Specification Links

- `DCL-SESSION-ROLE-RESOLUTION-001` v1 - the resolver implements its interactive rows + assertions 6 (session-id staleness) and 7 (role-set membership); assertion 8 (cross-harness parity) is not in scope here (AXIS 2 is Claude-native).
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v1 - Decision 1 (full session override includes the AXIS 2 surface) and Decision 2 (marker > durable) are the architectural source.
- `GOV-SESSION-ROLE-AUTHORITY-001` v1 - session-stated role is the authority for the AXIS 2 surface filter; durable remains the fallback.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` (advisory) - motivates the single shared resolver over four inline copies.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root boundary affirmed above.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal is filed at `-001` NEW; the `bridge/INDEX.md` update inserts a `NEW:` entry at the top of a new document block; no bridge file deletion or in-place rewrite of prior versions.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this Specification Links section satisfies the linkage gate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the spec-to-test plan below maps each acceptance criterion to executable verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the Project Authorization / Project / Work Item triple in the header satisfies the linkage gate.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - covered by `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` (active version 3; covers WI-3474 via active project membership AND explicit `included_work_item_ids`; allows source_code + tests).
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` - the project was reactivated and the PAUTH re-authorized under DELIB-2507 after this automation prematurely auto-retired the 10-slice project at 3/10 slices; owner AUQ S374 approved reactivate + pre-bind remaining slices (WI-3474..WI-3480). The recurring scanner defect is tracked as WI-3481.
- `GOV-ARTIFACT-APPROVAL-001` - this slice inserts no canonical artifact.
- `GOV-STANDING-BACKLOG-001` - this is a single feature slice, not a bulk operation. See Clause Scope Clarification below.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory), `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory), `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` (parent GO).
- `bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-008.md` (Slice 2 VERIFIED; marker writer + schema this resolver reads).
- `bridge/gtkb-interactive-session-role-override-slice-3-sessionstart-marker-invalidation-004.md` (Slice 3 VERIFIED; SessionStart invalidation that makes a present marker current-session).

## Clause Scope Clarification (Not a Bulk Operation)

Per `GOV-STANDING-BACKLOG-001` bulk-ops clause-scope clarification: this slice adds one shared module + a hook rewire + two test modules. No backlog bulk operation, no work_items insert/update/retire/supersede, no project create/retire, no authorization change, no inventory artifact, no review-packet, no formal-artifact-approval packet. The project reactivation + re-authorization that preceded this filing were owner-AUQ-approved governance recovery (S374), not part of this slice's source change. Evidence pattern tokens: single feature slice, shared resolver, no bulk, no backlog mutation.

## Prior Deliberations

- `DELIB-2507` - S371 owner directive + 6 AUQ architecture decisions; Decision 1 (full session override including AXIS 2 surface) directly authorizes this slice's behavior; also the standing owner-decision backing the reactivated PAUTH.
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` - parent GO; Slice 4 is the first consumer slice.
- `bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-008.md` - Slice 2 VERIFIED; established the marker schema (`role`, `session_id`, `session_id_source`, `written_at`, `source`) that this resolver reads.
- `bridge/gtkb-interactive-session-role-override-slice-3-sessionstart-marker-invalidation-004.md` - Slice 3 VERIFIED; the SessionStart invalidation that underwrites the session-id-unverified acceptance branch.
- `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-006.md` (Codex GO) - the deliberation chain that authored the AXIS 2 surface hook this slice rewires.
- No prior deliberation has built a shared session-role resolver; this is the first.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-SESSION-ROLE-RESOLUTION-001` (interactive rows + assertions 6/7) + `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` Decision 1/2 + the parent GO fully specify the resolver behavior and the AXIS 2 role-awareness. The only open design point (session-id-unverified acceptance vs rejection) is derivable from the DCL intent + Slice 3's guarantee and is flagged for Codex; it is not an owner requirement gap.

## Spec-Derived Verification Plan

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

| Acceptance criterion | Test | Expected |
|---|---|---|
| marker (valid, matching session id) wins over durable | `test_resolver_marker_beats_durable[pb]`, `[lo]` | resolved == marker role, source "marker" |
| marker role not in valid set -> durable (assertion 7) | `test_resolver_invalid_role_falls_back` | resolved == durable, source "durable_marker_invalid_role" |
| marker session id mismatch -> durable (assertion 6) | `test_resolver_stale_session_falls_back` | resolved == durable, source "durable_marker_stale_session" |
| marker present, current session id unavailable -> accept marker | `test_resolver_accepts_unverified_when_no_session_id` | resolved == marker role, source "marker_session_id_unverified" |
| marker absent -> durable | `test_resolver_no_marker_uses_durable[pb-durable]`, `[lo-durable]` | resolved == durable, source "durable_marker_absent" |
| resolver never mutates the role map or marker | `test_resolver_is_read_only` | role map + marker bytes unchanged after resolve |
| resolver marker path equals Slice 2 writer path | `test_resolver_marker_path_matches_writer` | path == `workstream_focus._session_role_marker_path(root)` |
| AXIS 2: PB marker -> Prime element + Prime heading | `test_axis2_pb_marker_surfaces_prime` | items == prime element; heading contains "Prime Work" |
| AXIS 2: LO marker -> Codex element + LO heading | `test_axis2_lo_marker_surfaces_lo` | items == codex element; heading contains "Loyal Opposition Work" |
| AXIS 2: no marker -> durable role's element | `test_axis2_no_marker_uses_durable` | items match durable role |
| AXIS 2: signature keys off resolved-role items | `test_axis2_signature_role_scoped` | LO and PB signatures differ for the same INDEX |

### Required verification commands (post-implementation report will show observed results)

```text
python -m ruff check scripts/session_role_resolution.py .claude/hooks/bridge-axis-2-surface.py platform_tests/hooks/test_session_role_resolution.py platform_tests/hooks/test_bridge_axis_2_role_aware.py
python -m ruff format --check scripts/session_role_resolution.py .claude/hooks/bridge-axis-2-surface.py platform_tests/hooks/test_session_role_resolution.py platform_tests/hooks/test_bridge_axis_2_role_aware.py
python -m pytest platform_tests/hooks/test_session_role_resolution.py platform_tests/hooks/test_bridge_axis_2_role_aware.py -q
```

Both ruff gates (lint + formatter) are run per the Slice 2 NO-GO -006 lesson that they are distinct gates.

## Acceptance Criteria

- Codex issues GO with explicit adjudication of the scope expansion (Review Ask 1) and confirmation that:
  - The resolver implements the DCL interactive rows + assertions 6/7 correctly and is read-only.
  - The AXIS 2 hook selects element 0 for PB and element 1 for LO, with a role-aware heading.
  - The session-id-unverified acceptance branch is acceptable (or NO-GO names the stricter contract).
  - No other AXIS 2 behavior changes (cache/suppression/dismissal/disable/fail-soft unchanged).
- If GO, implement and file the post-implementation report carrying forward Spec Links + spec-to-test mapping + observed results for both ruff gates and both test modules + recommended Conventional Commits type.
- If NO-GO, revise via `-002 REVISED`.

## Risk and Rollback

- **Risk:** prime/codex tuple elements swapped (LO session shows Prime work). **Mitigation:** `compute_actionable_pending` docstring fixes the order `(actionable_for_prime, actionable_for_codex)`; `test_axis2_lo_marker_surfaces_lo` asserts the LO session gets the codex element.
- **Risk:** resolver mutates the role map (a UserPromptSubmit hook must be side-effect-free on durable state). **Mitigation:** read-only durable lookup (`bootstrap_missing=False`, no `ensure_prime_on_startup` write path); `test_resolver_is_read_only` asserts no mutation.
- **Risk:** marker path drifts from the Slice 2 writer. **Mitigation:** `test_resolver_marker_path_matches_writer` asserts equality.
- **Risk:** session-id sanitization mismatch (AXIS 2 cache key sanitizes; marker stores raw). **Mitigation:** the resolver compares the marker's raw `session_id` against the RAW payload session id, not the sanitized cache-key form; documented + tested.
- **Risk:** scope expansion is not approved. **Mitigation:** Codex Review Ask 1 offers the split/inline alternatives; on NO-GO I refile per the chosen packaging.
- **Rollback:** revert the AXIS 2 hook to the Prime-only computation and delete the resolver module + test modules. No state to unwind (read-only; no marker writes; Slices 5-7 not yet landed).

## Owner Decisions / Input

This slice proceeds under `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` (active version 3; covers WI-3474 via active project membership and explicit inclusion; cites `DELIB-2507`). Per `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` the project authorization removes per-slice direct AskUserQuestion overhead for bounded project work; per `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` the slice runs through the full bridge protocol (this NEW -> Codex GO -> implement -> post-implementation report -> VERIFIED).

DELIB-2507 holds the 6 S371 owner AskUserQuestion decisions; Decision 1 (full session override, explicitly including the AXIS 2 surface) directly authorizes this slice. One additional owner decision was captured this session: **owner AUQ S374** approved reactivating the project + pre-binding all remaining slice WIs after the `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` scanner prematurely auto-retired the 10-slice project at 3/10 slices (the recurring scanner defect is tracked as WI-3481). That recovery was governance-state restoration backed by the existing DELIB-2507; it did not change the slice's behavior. The shared-resolver scope expansion is a code-organization decision within the DCL-specified behavioral envelope and is routed to Codex review, not a new owner decision.

## Codex Review Asks

1. **Scope expansion adjudication:** approve introducing `scripts/session_role_resolution.py` in this slice, OR NO-GO directing (a) a separate predecessor resolver thread, or (b) inline-in-AXIS-2 with later extraction.
2. Confirm the prime/codex tuple mapping (element 0 = PB, element 1 = LO) and the role-aware heading.
3. Confirm the session-id-unverified acceptance branch, or NO-GO in favor of reject-on-unverified.
4. Confirm the resolver is read-only with respect to the durable role map and the marker.
5. Flag any specification this proposal should cite but does not.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
