NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S371-interactive-session-role-override-scoping
author_model: Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI default reasoning, explanatory output style

# GT-KB Interactive Session Role Override - Architecture-First Scoping

bridge_kind: prime_proposal

Document: gtkb-interactive-session-role-override-scoping
Version: 001 (NEW; architecture-first scoping for the interactive-vs-headless role authority split)
Date: 2026-05-29 UTC

## Summary

Scopes the architecture-first correction of an authority defect identified by the owner in S371: GT-KB currently treats the durable harness role assignment in the registry projection at `harness-state/harness-registry.json` (mirrored to `harness-state/role-assignments.json`) as authoritative for ALL session-rendered behavior, including interactive sessions where the owner has explicitly stated a different role via the canonical init keyword `::init gtkb (pb|lo)`. The owner's stated intent is that durable role assignment is the default for HEADLESS dispatch of work only and does NOT apply to interactive sessions that declare a role.

This SCOPING proposal does not mutate code, MemBase, or rule text. It proposes the architectural artifact set (one ADR, one DCL, one GOV - all new), revisions to two existing specs, a per-surface implementation slice plan, and a verification approach. Implementation follows as separate per-surface bridges (each filed as `bridge_kind: implementation_proposal` with their own Project Authorization / Project / Work Item triple) after Codex GO on the architecture.

The owner approved the architecture-first landing path via AskUserQuestion in S371 (Decision 5 of 6, captured in `## Owner Decisions / Input`).

This proposal is filed as `bridge_kind: spec_intake` because its deliverable is a draft architecture artifact set for Codex review, not a code or MemBase mutation; implementation work is deferred to per-slice bridges.

## In-Root Boundary Affirmation

Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md`: this scoping proposal is purely platform-internal. It introduces no application-layer files, no `applications/<name>/` paths, no Agent Red references in a live-dependency role, and no out-of-root paths. All target paths listed below are within `E:\GT-KB`. The new runtime marker file (`.claude/session/active-session-role.json`, proposed for the implementation slices) lives in-root under `.claude/session/`. The implementation slices that follow GO must reaffirm this boundary on each filing.

## Problem Statement

### Symptom

The owner's directive (verbatim, S371):

> "We are currently treating the harness role assignment as authoritative, overriding the user's stated preference for a given interactive session. This is not correct.
>
> The assignment of roles to harnesses is a default and should not override the user's stated preference for a session, irrespective of what the default role is for a harness: harness role assignment is the default for headless assignment of work, and does not apply to interactive sessions."

Concrete reproduction for the symptomatic case "owner types `::init gtkb lo` to harness B (Claude, durable Prime Builder)":

1. SessionStart hook (`.claude/hooks/session_start_dispatch.py`) calls `_resolve_own_role_set()` -> `{pb}` for harness B.
2. `_write_role_scoped_startup_relay_caches` (`scripts/session_self_initialization.py` via the hook's role-scoped cache writer at `session_start_dispatch.py:503-520`) iterates the durable role set. With `role_set={pb}` and `primary_mode=pb`, the loop writes only `.claude/hooks/last-user-visible-startup-pb.md`. The `-lo.md` cache is never written.
3. UserPromptSubmit init-keyword matcher (`scripts/workstream_focus.py:1053` `_CANONICAL_DISPATCH_INIT_RE`, applied via `.claude/hooks/workstream-focus.py`) parses `lo` from the owner's keyword and looks up `.claude/hooks/last-user-visible-startup-lo.md`.
4. Cache missing -> `_startup_relay_failure_context` fires with "the cache file or its metadata sidecar is missing, empty, or malformed".
5. Owner receives a startup-relay failure diagnostic instead of the requested LO disclosure. The interactive override is silently refused.

Additionally, independent of the disclosure-relay symptom, every other role-keyed surface continues to behave as the durable role:

- AXIS 2 in-session surface (`.claude/hooks/bridge-axis-2-surface.py`) is hardcoded to compute Prime-actionable work via `compute_actionable_pending`. There is no role lookup; an interactive owner running a session as LO still gets Prime work surfaced.
- Workstream focus / startup focus menu (`scripts/workstream_focus.py`) selects PB or LO focus-menu shape from the durable role.
- MemBase attribution (`scripts/_kb_attribution.py`) derives `prime-builder/<harness>` or `loyal-opposition/<harness>` `changed_by` tags from the durable role.
- The SessionStart hook's `_bridge_dispatch_keyword_check` `SPOOF_FALLBACK` path explicitly refuses to honor a keyword-without-env-var (the interactive-owner-typed case) per `session_start_dispatch.py:354`: "keyword without env-var; falling through to normal startup; defense against owner-typed or otherwise unverified keyword strings".

### Cause

The current architecture conflates two separable concerns into one role authority:

1. **Headless dispatch routing**: the cross-harness event-driven trigger (`scripts/cross_harness_bridge_trigger.py`) needs to know which harness to dispatch a counterpart bridge action to. Durable role authority is correct here - durable harness identity is the only stable handle the trigger has.
2. **Interactive session experience**: the owner-rendered disclosure, AXIS 2 surface, focus menu, attribution, and AUQ-keyed routing reflect what role THIS session is actually doing. Durable role authority is incorrect here when the owner has explicitly stated otherwise.

Today both concerns resolve through the same authority chain (registry projection -> role-assignments.json -> role-set), and the receiver-side gate (`DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`) refuses keyword/role mismatches without distinguishing dispatch context.

### Why architecture-first

Per the owner's S371 AskUserQuestion decision (Decision 5 of 6), this correction lands as an architecture-first effort: file ADR + DCL + GOV through this scoping bridge, then per-surface implementation slices after Codex GO. Rationale: the boundary "durable = headless authority; init keyword = interactive authority" is a contract change to `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` and the operating-role rules. The contract change is more important than any single code surface; landing architecture first lets each implementation slice cite a stable architectural anchor rather than negotiating the architecture inside each slice.

## Proposed Architecture

This scoping proposes three new MemBase artifacts and revisions to two existing specs. Each draft below is the proposed body that the post-GO formal-artifact-approval packets will insert; Codex review of this scoping IS the architectural review.

### Draft of ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001

**Title:** Interactive Session Role Authority is Separate From Durable Harness Role Assignment

**Status:** specified (initial)

**Context:** Durable harness role assignment (registry projection at `harness-state/harness-registry.json`, mirrored to `harness-state/role-assignments.json`) is consumed by both headless cross-harness dispatch routing (where it is the only stable identity-to-role anchor) and interactive session rendering (where the owner's session-stated role should take precedence). The current implementation treats durable role as authoritative for both, refusing owner-stated session role overrides via the SPOOF_FALLBACK path. This conflation creates an authority defect: an interactive owner who types `::init gtkb lo` to a durable-PB harness receives a startup-relay failure rather than the requested LO disclosure.

**Decision:**

1. Durable harness role assignment is the authority for headless dispatch routing only. The cross-harness event-driven trigger (`scripts/cross_harness_bridge_trigger.py`) consults durable role to choose recipient harness and to compose the dispatched init keyword. The receiver-side `STRICT_DROP` gate for headless dispatch (env-var `GTKB_BRIDGE_POLLER_RUN_ID` present) continues to enforce durable set-membership against the dispatched keyword. Misdirected headless dispatch silently drops with audit log entry per `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` (revised per below).

2. Interactive sessions (env-var `GTKB_BRIDGE_POLLER_RUN_ID` absent) follow the session-stated role when an owner prompt contains the canonical init keyword `::init gtkb (pb|lo)`. The session-stated role applies to: SessionStart disclosure rendering, AXIS 2 in-session surface filtering, workstream-focus menu shape, MemBase `changed_by` attribution, and AUQ-keyed routing. Cross-harness dispatch is unaffected and continues to use durable role.

3. Interactive sessions without an init keyword fall back to the durable role for the same surfaces. Durable role remains the implicit default for owners who do not declare a session role.

4. Session-stated role binds the rest of the session lifetime once declared on an owner prompt. Mid-session re-declaration (a later owner prompt carrying a different init keyword) overrides the prior declaration. The override is held in ephemeral session-scoped state with NO durable record across SessionStart events; compaction or session resume reverts to durable until owner re-declares.

5. The canonical init keyword `::init gtkb (pb|lo)` is the single mechanism for interactive role declaration. No conversational aliases. No CLI surface. The keyword's syntax is unchanged from `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`; only its receiver-side semantics extend to cover the interactive-owner-typed case.

6. The startup disclosure surfaces only the session-stated role under override (e.g., "Role being assumed: Loyal Opposition"). The durable role is not surfaced in the disclosure under override; it remains an internal implementation detail visible through `gt mode` CLI surfaces and the registry projection.

**Rejected alternatives:**

- Disclosure-only override (durable still drives AXIS 2, attribution, focus menu, AUQ routing). Rejected S371 AUQ Decision 1: the session experience would contradict the disclosure, leaving the owner with PB-actionable bridge work surfaced inside an LO-declared session.

- UI override (disclosure + interactive surfaces; attribution + headless dispatch remain durable). Rejected S371 AUQ Decision 1: attribution should reflect who actually did the work; durable role attribution for an interactive LO session in a PB harness would mis-record the work history.

- Persistent session-state file surviving compaction/resume. Rejected S371 AUQ Decision 3: introducing durable per-session state expands the authority surface and creates a stale-record class. Owner can re-declare on each fresh session at near-zero friction (one prompt-line keyword).

- Conversational alias declaration (`act as loyal opposition`, `LO mode`, etc.). Rejected S371 AUQ Decision 4: alias surface is a maintenance burden and creates ambiguity (alias vs natural language). The canonical syntax is unambiguous.

- CLI-based declaration (`gt mode session-role lo`). Rejected S371 AUQ Decision 4: an out-of-band tool call to declare a session role introduces a state-write path that competes with the init keyword. Owner picked the single-mechanism path.

- Disclosure transparency (showing both session and durable role in the same disclosure). Rejected S371 AUQ Decision 6: cleaner UX and lower cognitive load. Durable role remains observable via `gt mode show` or registry-projection inspection.

**Consequences:**

- Owners gain working interactive role override via the existing canonical keyword.
- The receiver-side `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` rule deterministically forks on dispatch context (env-var present vs absent), tightening its semantics rather than weakening them.
- Headless cross-harness dispatch is architecturally unchanged; durable role remains its authority.
- The SessionStart hook generates BOTH `-pb.md` and `-lo.md` startup-disclosure caches regardless of durable role, so the UserPromptSubmit init-keyword matcher's keyword-keyed cache selection works for either role.
- The AXIS 2 surface hook, workstream-focus, and MemBase attribution become role-aware (consult session-state-marker-or-durable, in that order) instead of durable-only.
- A small ephemeral session-state marker file (proposed: `.claude/session/active-session-role.json`, deleted/ignored across SessionStart boundaries) carries the override between UserPromptSubmit and later hook invocations within one session.

### Draft of DCL-SESSION-ROLE-RESOLUTION-001

**Title:** Session Role Resolution Deterministic Rules

**Status:** specified (initial)

**Constraint:** GT-KB code that needs to know "what role is this session operating as" MUST resolve it deterministically using the following table. The resolution is identical across hooks, CLI tools, and library code.

**Resolution table:**

| Context | env-var `GTKB_BRIDGE_POLLER_RUN_ID` | session-state marker exists | Init keyword on this prompt | Resolved role | Source |
|---|---|---|---|---|---|
| Headless dispatch, authorized | present | n/a | matches durable set | durable (matches keyword) | dispatch routing |
| Headless dispatch, misdirected | present | n/a | NOT in durable set | drop (STRICT_DROP); no role rendered | audit-log only |
| Headless dispatch, legacy | present | n/a | absent | durable (legacy env-var-only fallback) | durable |
| Interactive declaration | absent | n/a | `::init gtkb pb` or `::init gtkb lo` | keyword role | session-state marker written |
| Interactive continuation | absent | present, valid | absent | session-state marker role | session-state marker |
| Interactive default | absent | absent | absent | durable | durable |
| Interactive resume after compaction | absent | absent (marker not persisted) | absent | durable | durable |

**Machine-checkable assertions:**

1. `assertion_resolved_role_is_durable_when_headless`: when `GTKB_BRIDGE_POLLER_RUN_ID` is present and a keyword is present and `keyword_role ∈ durable_role_set`, resolved role equals durable role (`primary_role(durable_record)`). Otherwise behavior is STRICT_DROP per `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`.
2. `assertion_resolved_role_is_keyword_when_declared`: when `GTKB_BRIDGE_POLLER_RUN_ID` is absent and the prompt contains a valid init keyword, resolved role equals the keyword role. The session-state marker MUST be written on the same code path.
3. `assertion_resolved_role_is_marker_when_continuing`: when `GTKB_BRIDGE_POLLER_RUN_ID` is absent and a valid session-state marker exists and no init keyword is on this prompt, resolved role equals the marker role.
4. `assertion_resolved_role_is_durable_when_undeclared`: when `GTKB_BRIDGE_POLLER_RUN_ID` is absent and no session-state marker exists and no init keyword is on this prompt, resolved role equals durable role.
5. `assertion_session_state_marker_is_ephemeral`: the session-state marker file (proposed `.claude/session/active-session-role.json`) MUST NOT survive a SessionStart event. SessionStart MUST delete or otherwise invalidate any pre-existing marker before SessionStart-time role rendering.
6. `assertion_session_state_marker_carries_session_id`: the marker MUST record the current Claude Code session id (or equivalent harness session token) so that a stale marker from a prior session id is treated as invalid.
7. `assertion_session_state_marker_is_role-set-member`: the marker's role value MUST be in `{prime-builder, loyal-opposition}`. Unknown values are treated as marker-absent.

**Out of scope for this DCL:**

- The mechanism by which the durable role is read (existing `harness_roles.py` chain).
- The mechanism by which the cross-harness trigger selects recipient (existing trigger logic; unchanged).
- The marker file format details (left to the implementation slice; this DCL requires only the fields above).

### Draft of GOV-SESSION-ROLE-AUTHORITY-001

**Title:** Session Role Authority Split - Durable vs Session-Stated

**Status:** specified (initial)

**Governance rule:**

GT-KB recognizes two distinct role-authority surfaces:

1. **Durable harness role assignment** records which role a HARNESS is configured to perform headless work as. It is the authority for cross-harness dispatch routing, receiver-side dispatch-mismatch gating, and the interactive-session fallback when no session role has been declared. It lives in the registry projection at `harness-state/harness-registry.json` (mirrored to `harness-state/role-assignments.json`). Mutations to durable role assignment require the `gt mode set-role` transaction component (per `bridge/gtkb-operating-mode-transaction-001` Slice 1) and produce auditable mutation records.

2. **Session-stated role** records which role a specific INTERACTIVE SESSION is operating as for the duration of that session. It is the authority for SessionStart disclosure, AXIS 2 surface filter, workstream focus menu, MemBase `changed_by` attribution, and AUQ-keyed routing within the session. It is declared by the owner via the canonical init keyword `::init gtkb (pb|lo)` on an owner prompt and persists in an ephemeral session-state marker for the rest of the session lifetime (lost across SessionStart events).

The two surfaces are deterministically related per `DCL-SESSION-ROLE-RESOLUTION-001`: session-stated role overrides durable for interactive surfaces when declared; durable is the fallback when no session role has been declared; durable remains the sole authority for headless dispatch surfaces.

Durable role assignment MUST NOT be silently mutated by interactive session activity. Session-stated role MUST NOT be persisted to durable storage.

The canonical mechanism for declaring session-stated role is the canonical init keyword `::init gtkb (pb|lo)`. No conversational aliases, no out-of-band CLI command, no implicit declaration. This single-mechanism contract MAY be relaxed in a future governance amendment but is canonical at the time of this artifact's creation.

**Rule applicability:**

- Applies to all GT-KB AI coding harnesses (currently Claude Code at `B` and Codex CLI at `A`).
- Applies to all interactive and headless session entry points.
- Applies to library code under `scripts/` and the in-root `groundtruth-kb/` source tree that consults role to render disclosures, surface work, attribute MemBase changes, or route AUQ.

**Authority chain:**

- This GOV defers to existing `GOV-HARNESS-ROLE-PORTABILITY-001` (Prime/LO are portable across harnesses), `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` (multi-harness role config preserved), and `ADR-SINGLE-HARNESS-OPERATING-MODE-001` (single-harness topology decisions) for durable role semantics.
- This GOV defers to `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` (revised below) for the keyword syntax.
- This GOV defers to `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` (revised below) for the receiver-side keyword/role assertion semantics.

### Draft Revision of SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001

**Current:** Regex `^::init gtkb (pb|lo)$`; first-line-only; closed vocabulary `{pb, lo}`; no synonyms; strict parse. Used by the cross-harness trigger to compose the dispatched init keyword and by the receiver-side SessionStart hook for set-membership check.

**Revised additions:**

1. The keyword is canonical for BOTH machine-emitted dispatch (cross-harness trigger; env-var `GTKB_BRIDGE_POLLER_RUN_ID` present) AND owner-typed interactive declaration (no env-var). The syntax is identical across both contexts.

2. The receiver-side behavior is context-dependent per `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` (revised below). For headless dispatch, the keyword must match the receiver's durable role set or the dispatch is silently dropped. For interactive owner-typed declaration, the keyword establishes the session-stated role for the rest of the session.

3. The owner-typed keyword MAY appear on ANY owner prompt during the session lifetime, not only the first prompt. Mid-session re-typing overrides any prior session-stated role.

4. The first-line-only constraint (regex anchors `^...$`) is unchanged; the keyword MUST appear as the entire first line of the owner prompt.

### Draft Revision of DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001

**Current:** Emitter authority + receiver-side set-membership enforcement; mismatch -> silent drop with audit log entry at `.gtkb-state/bridge-poller/dispatch-failures.jsonl`.

**Revised behavior table (deterministic):**

| env-var `GTKB_BRIDGE_POLLER_RUN_ID` | Init keyword present | Keyword in durable role set | Receiver decision | Effect |
|---|---|---|---|---|
| absent | absent | n/a | NORMAL_STARTUP | render fresh-session disclosure for resolved role (per `DCL-SESSION-ROLE-RESOLUTION-001`) |
| absent | present | n/a | INTERACTIVE_OVERRIDE_AUTHORIZED | record session-stated role marker; render disclosure for keyword role; do NOT consult durable set-membership |
| present | absent | n/a | LEGACY_FALLBACK | env-var-only dispatch (preserved for backward compatibility) |
| present | present | yes | DISPATCH_AUTHORIZED | bridge auto-dispatch context emitted |
| present | present | no | STRICT_DROP | silent drop; audit log; clean exit |

**Note:** The prior `SPOOF_FALLBACK` decision (keyword without env-var falling through to normal startup) is REPLACED by `INTERACTIVE_OVERRIDE_AUTHORIZED`. The prior defense-against-owner-typed-keyword rationale is superseded by the architecture decision in `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` that owner-typed keywords are exactly the interactive override mechanism.

**Receiver-side audit logging:**

- `STRICT_DROP` continues to append a `misdirected_dispatch_strict_drop` record to `.gtkb-state/bridge-poller/dispatch-failures.jsonl` (unchanged).
- `INTERACTIVE_OVERRIDE_AUTHORIZED` records a `session_role_override` record to a new ephemeral log at `.gtkb-state/sessions/<session-id>/role-overrides.jsonl` (proposed; implementation slice will refine path).

## Implementation Slice Plan

Each slice files as a separate implementation bridge after Codex GO on this scoping. Each implementation slice will carry its own Project Authorization / Project / Work Item triple (a new project `PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE` is a candidate per Codex Review Ask 8 below). Slices are independently mergeable and may be parallelized where dependencies permit.

### Slice 1 - SessionStart cache writer: emit both role caches

**Surface:** `.claude/hooks/session_start_dispatch.py` `_write_role_scoped_startup_relay_caches`; `scripts/session_self_initialization.py` `build_startup_model` + `render_report`.

**Change:** SessionStart unconditionally generates both `last-user-visible-startup-pb.md` and `last-user-visible-startup-lo.md` plus matching metadata sidecars regardless of durable role set membership. The existing UserPromptSubmit init-keyword matcher's keyword-keyed cache lookup then succeeds for either role.

**Acceptance criterion:** For harness B (durable PB), SessionStart writes both caches with correct `role_mode` field in metadata. For harness A (durable LO), same.

**Dependency:** None. Independent of other slices.

### Slice 2 - UserPromptSubmit init-keyword matcher: session-state marker write

**Surface:** `scripts/workstream_focus.py` `_startup_role_mode_from_prompt`, `_startup_gate_response`; new helper to write `.claude/session/active-session-role.json`.

**Change:** On init-keyword match in an interactive context (no `GTKB_BRIDGE_POLLER_RUN_ID` env-var), write the session-state marker file with the keyword-derived role, current Claude Code session id, and timestamp. The marker is purely additive; the existing cache-lookup behavior is preserved.

**Acceptance criterion:** Owner prompt with init keyword writes marker file; absent prompt does not. Marker carries session id; marker fails validation if session id mismatches.

**Dependency:** Slice 1 (so the keyword-matched cache exists).

### Slice 3 - SessionStart marker invalidation

**Surface:** `.claude/hooks/session_start_dispatch.py`.

**Change:** SessionStart deletes any pre-existing `.claude/session/active-session-role.json` before rendering, ensuring the marker is ephemeral across SessionStart events per `DCL-SESSION-ROLE-RESOLUTION-001` assertion 5.

**Acceptance criterion:** Marker file absent after SessionStart. Tested with fixture: pre-write a marker, run SessionStart, assert marker absent.

**Dependency:** Slice 2 (marker definition).

### Slice 4 - AXIS 2 surface hook: session-stated role awareness

**Surface:** `.claude/hooks/bridge-axis-2-surface.py`.

**Change:** Replace the hard-coded "Prime-actionable" computation with role-aware surface selection. Resolve role per `DCL-SESSION-ROLE-RESOLUTION-001` (marker > durable). Surface Prime-actionable work when resolved role is PB; surface LO-actionable work (NEW/REVISED proposals, ADVISORY entries awaiting Prime acknowledgement when applicable) when resolved role is LO.

**Acceptance criterion:** With a PB-marker, surface emits Prime work. With an LO-marker, surface emits LO work. Without a marker, surface emits work matching durable role.

**Dependency:** Slice 2 (marker reader).

### Slice 5 - Workstream-focus role awareness

**Surface:** `scripts/workstream_focus.py` startup-focus menu generation.

**Change:** Resolve role per `DCL-SESSION-ROLE-RESOLUTION-001` for focus-menu shape selection. Slice 1's role-cache pair already covers disclosure; this slice covers the focus-menu options.

**Acceptance criterion:** PB-marker session sees Prime focus menu (A/B/C/D shape). LO-marker session sees LO focus options. Undeclared session inherits durable.

**Dependency:** Slice 2.

### Slice 6 - MemBase attribution

**Surface:** `scripts/_kb_attribution.py`.

**Change:** Resolve role per `DCL-SESSION-ROLE-RESOLUTION-001` for `changed_by` tag generation. Tag becomes `prime-builder/<harness>` or `loyal-opposition/<harness>` according to RESOLVED role, not durable role.

**Acceptance criterion:** Attribution test fixture: with an LO marker, `changed_by` reflects LO regardless of durable PB. With no marker, behavior is unchanged (durable-keyed).

**Dependency:** Slice 2.

### Slice 7 - Doctor checks

**Surface:** the in-root `groundtruth-kb/src/groundtruth_kb/project/doctor.py`.

**Change:** Add new doctor checks:
- `_check_session_role_marker_validity` (WARN when marker file exists with malformed JSON, missing session id, or unknown role token).
- `_check_session_role_marker_session_id_alignment` (WARN when marker session id does not match current session id, suggesting stale marker SessionStart failed to clean up).

Existing `_check_role_set_topology_consistency` is unchanged; it validates durable role only.

**Acceptance criterion:** Test fixtures for valid marker (PASS), malformed marker (WARN), stale-session-id marker (WARN).

**Dependency:** Slice 2 (marker schema).

### Slice 8 - Rule and CLAUDE/AGENTS updates

**Surface:** rule files under `.claude/rules/`, `CLAUDE.md` (Role precedence paragraph), `AGENTS.md`.

**Change:** Revise text to reflect the durable-vs-session authority split per `GOV-SESSION-ROLE-AUTHORITY-001`. Rule files currently state "no markdown rule file can override the durable role assignment map" - this remains true (rule files don't override the registry projection; the session-state marker is not a rule file).

**Acceptance criterion:** Each revised rule file cites `GOV-SESSION-ROLE-AUTHORITY-001`, `DCL-SESSION-ROLE-RESOLUTION-001`, and `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`. The Role precedence paragraph in `CLAUDE.md` explicitly describes the durable-vs-session split. Existing canonical-terminology glossary entries (`operating role`, `session lane`, `session focus`, `work subject`) get a new sibling entry `session-stated role` per `DCL-CONCEPT-ON-CONTACT-001`.

**Dependency:** Slices 1-7 land first so the rule changes describe shipping behavior, not pre-shipped behavior.

### Slice 9 - Regression and integration tests

**Surface:** `platform_tests/`, `tests/scripts/`.

**Change:** Add tests covering the resolution table:
- Cross-harness trigger remains durable-keyed (no behavioral change; regression).
- `STRICT_DROP` continues to fire for misdirected headless dispatch (regression).
- New: interactive override via init keyword writes marker, renders correct disclosure, AXIS 2 surface follows marker, attribution follows marker.
- New: marker is invalidated by SessionStart.

**Acceptance criterion:** All new tests PASS; no existing test regresses.

**Dependency:** Slices 1-8.

## Specification Links

- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` (new; drafted in this proposal)
- `DCL-SESSION-ROLE-RESOLUTION-001` (new; drafted in this proposal)
- `GOV-SESSION-ROLE-AUTHORITY-001` (new; drafted in this proposal)
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` (revised; drafted in this proposal)
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` (revised; drafted in this proposal)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - blocking applicability spec. This scoping is purely platform-internal and respects the root boundary; see `## In-Root Boundary Affirmation` above for the affirmation that no out-of-root paths and no application-layer files are introduced.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - preserved authority for durable role portability across harnesses; this scoping does not alter it.
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` - preserved authority for multi-harness role configuration; this scoping does not alter it.
- `GOV-ACTING-PRIME-BUILDER-001` - preserved authority for the legacy acting-prime-builder compatibility/provenance value; READ-accepted, SET-rejected per the existing contract.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` - preserved authority for single-harness topology; this scoping is orthogonal (single-harness sessions can still declare a session role via init keyword).
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this scoping proposal is filed at -001 NEW per the bridge protocol; INDEX entry inserted at the top per Prime workflow.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this Specification Links section satisfies the linkage gate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the test plan maps each acceptance criterion to executable verification per slice; implementation slices will surface concrete test command sets.
- `GOV-ARTIFACT-APPROVAL-001` - the three new artifacts and two revisions require per-artifact formal-artifact-approval packets at MemBase insertion time; this scoping does NOT insert any of them. Codex GO on the scoping authorizes the architectural framing; per-artifact packets are filed separately by the implementation slices.
- `PB-ARTIFACT-APPROVAL-001` - same as above; explicit owner approval per artifact at insertion time, not at scoping time.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - the formal-artifact-approval-gate hook will enforce per-artifact packets at insertion time.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) - this scoping converts the owner directive into a governed artifact set rather than chat-only context.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) - this scoping treats role authority as artifact-mediated rather than runtime-only.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) - the proposed lifecycle states for the new ADR/DCL/GOV are `specified` at creation; transitions to `implemented` and `verified` happen at slice completion. No `superseded`/`retired` transitions in this scoping.
- `DCL-CONCEPT-ON-CONTACT-001` - the new term `session-stated role` is added on contact; the canonical-terminology glossary entry lands in Slice 8.
- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` - the glossary update in Slice 8 makes the new term salient via the always-loaded read surface.
- `ADR-DA-READ-SURFACE-PLACEMENT-001` - the glossary placement decision applies to this term.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` - the owner directive in S371 was articulated in chat; the AskUserQuestion sequence in this session captured the chat-derived specifications under explicit owner approval.
- `GOV-STANDING-BACKLOG-001` - this scoping introduces no backlog mutation, no work_items insert/update/retire/supersede, no project create/retire, no authorization change. See `## Clause Scope Clarification (Not a Bulk Operation)` below.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` (advisory) - the deterministic resolution table in `DCL-SESSION-ROLE-RESOLUTION-001` aligns with this principle: role resolution becomes a deterministic table, not an AI judgment call.
- `bridge/gtkb-operating-mode-transaction-001` (Slice 1 of mode-switch transaction component) - the `gt mode set-role` transaction is the authoritative durable-role mutation surface; this scoping does not modify it.

## Clause Scope Clarification (Not a Bulk Operation)

Per the `GOV-STANDING-BACKLOG-001` bulk-ops clause-scope clarification convention: this scoping proposal introduces no backlog mutation, no work_items insert/update/retire/supersede, no project create/retire, no authorization change. It is architecture work that produces draft artifacts for Codex review. Implementation slices that follow GO will be filed as separate bridges. Evidence pattern: this is an architecture-first scoping proposal; matched tokens include "architecture", "scoping", "drafts", "no code mutation", "no MemBase mutation", "implementation follows as separate bridges".

## Prior Deliberations

- `DELIB-0830` (Loyal Opposition assumes acting Prime Builder) - historical context for the role-portability framing; preserved.
- `DELIB-0831` (Prime/LO are portable across harnesses) - preserved authority for `GOV-HARNESS-ROLE-PORTABILITY-001`.
- `DELIB-0832` (GT-KB installs configure Prime Builder) - preserved authority for installation-time role configuration; this scoping does not alter installation behavior.
- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` - foundational evidence that the cross-harness event-driven trigger works on Windows; this scoping does not affect the trigger.
- `bridge/gtkb-canonical-init-keyword-syntax-001-007.md` (Codex GO at -008) - the deliberation chain establishing `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`. This scoping proposes additive revision; the keyword syntax itself is unchanged.
- `bridge/gtkb-single-harness-bridge-dispatcher-001-013.md` (Codex GO at -014) - introduced the role-set wire form. This scoping is fully compatible with role-set semantics; the session-state marker carries a single role token (the resolved role for the session).
- No prior deliberation explicitly distinguishes interactive-session role authority from headless dispatch role authority. The S371 owner directive is the originating clarification; this scoping captures it as durable architecture.

## Requirement Sufficiency

Existing requirements sufficient. The six AskUserQuestion decisions captured in S371 (enumerated in `## Owner Decisions / Input` below) fully specify the architectural boundary, the persistence model, the declaration UX, the landing strategy, the disclosure shape, and the override scope. No new owner requirement gathering is required for the scoping pass. Implementation slices may surface implementation-detail AskUserQuestions (e.g., marker file format details) but these are bounded by the architecture established here.

## target_paths

This SCOPING proposal does not authorize source mutation, MemBase mutation, or rule-file mutation. Target paths for the scoping:

- this bridge file
- `bridge/INDEX.md` (new entry insertion)

Implementation slices that follow Codex GO will list concrete target_paths from this preliminary set (subject to per-slice review):

- `.claude/hooks/session_start_dispatch.py` (Slices 1, 3)
- `scripts/session_self_initialization.py` (Slice 1)
- `scripts/workstream_focus.py` (Slices 2, 5)
- `.claude/hooks/bridge-axis-2-surface.py` (Slice 4)
- `scripts/_kb_attribution.py` (Slice 6)
- the in-root `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (Slice 7)
- rule files under `.claude/rules/` (Slice 8)
- `.claude/rules/canonical-terminology.md` (Slice 8; new `session-stated role` entry)
- `CLAUDE.md`, `AGENTS.md` (Slice 8)
- `platform_tests/`, `tests/scripts/` (Slice 9; new test modules)
- `.claude/session/active-session-role.json` (Slices 2, 3; runtime-written, not under source control)

Per-artifact formal-artifact-approval packets at `.groundtruth/formal-artifact-approvals/<date>-<artifact-id>.json` are required for the three new artifacts (ADR, DCL, GOV) and two revisions before MemBase insertion. These packets are filed by the implementation slices that touch MemBase.

## Spec-Derived Verification Plan (for implementation slices)

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, each acceptance criterion maps to executable verification at slice-level. The summary table:

| DCL-SESSION-ROLE-RESOLUTION-001 assertion | Verification |
|---|---|
| 1. resolved=durable when headless and authorized | regression test against `_bridge_dispatch_keyword_check` for `(env-var present, keyword present, keyword in role set)`; assert `DISPATCH_AUTHORIZED` |
| 1. STRICT_DROP when headless and keyword not in set | regression test for `(env-var present, keyword present, keyword NOT in set)`; assert `STRICT_DROP` + audit-log entry |
| 2. resolved=keyword when interactive declaration | new test: prompt with `::init gtkb lo` in absence of env-var; assert session-state marker written with role `loyal-opposition`; assert disclosure relay reads `-lo.md` cache |
| 3. resolved=marker when interactive continuation | new test: prompt with no keyword but valid marker; assert AXIS 2 surface, attribution, focus menu honor marker role |
| 4. resolved=durable when interactive undeclared | new test: prompt with no keyword, no marker; assert durable role used |
| 5. marker is ephemeral across SessionStart | new test: write marker, invoke SessionStart, assert marker absent |
| 6. marker carries session id | new test: write marker with stale session id; assert marker treated as invalid |
| 7. marker role is role-set-member | new test: write marker with role `invalid-role`; assert marker treated as invalid |
| Disclosure shows session role only | new test: with LO marker, disclosure body contains "Role being assumed: Loyal Opposition" and does NOT contain a durable-role reference in the disclosure body |
| Cross-harness trigger remains durable-keyed | regression test: trigger dispatches to durable role recipient regardless of any session-state marker |

The Slice 9 test bridge will name concrete pytest module paths and exact assertion functions.

## Acceptance Criteria

- Codex issues GO on this scoping proposal with explicit confirmation that:
  - The ADR + DCL + GOV trio is the correct architectural framing (vs a single-artifact bundling).
  - The 9-slice implementation plan decomposition is appropriate (vs a different slice partition).
  - The deterministic resolution table in `DCL-SESSION-ROLE-RESOLUTION-001` covers all required dispatch contexts.
  - The receiver-side decision-table revision to `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` is mechanically sound and does NOT weaken the headless dispatch safety contract.
  - The ephemeral session-state marker design (no durable persistence; cleared at SessionStart; session-id-keyed) is acceptable; if not, NO-GO with a counterproposal (e.g., in-memory only with re-prompt UX, or env-var-based).
- If GO, file per-artifact formal-artifact-approval packets and implementation Slice 1 NEW as the next step.
- If NO-GO, revise scope per Codex findings via -002 REVISED (no in-place edit of -001 per the auto-memory feedback "Never edit a filed bridge file in place").

## Risk and Rollback

- **Risk:** Receiver-side audit gate weakens for headless dispatch under the revised behavior table. **Mitigation:** the headless rows in the table are UNCHANGED from current behavior; only the interactive-prompt rows are modified. Slice 9 regression test asserts `STRICT_DROP` continues to fire for misdirected headless dispatch.
- **Risk:** Ephemeral marker creates a race between UserPromptSubmit (marker write) and AXIS 2 surface (marker read) within the same prompt turn. **Mitigation:** marker write happens in the UserPromptSubmit hook BEFORE the AXIS 2 hook runs (hook ordering in `.claude/settings.json` controls this; Slice 2 acceptance asserts ordering).
- **Risk:** Cross-harness trigger could observe a marker and erroneously dispatch counterpart work. **Mitigation:** trigger code does NOT read the marker; it consults durable role only. Slice 9 regression test asserts trigger behavior is durable-keyed regardless of marker.
- **Risk:** A pre-existing session-state marker file from a malformed prior session survives SessionStart. **Mitigation:** Slice 3 invalidates the marker at SessionStart; doctor check (Slice 7) WARN-flags stale markers.
- **Risk:** The owner forgets the init keyword and is confused by durable-default behavior. **Mitigation:** when SessionStart renders a durable-default disclosure, the disclosure may include a footer pointing to the init-keyword option (`::init gtkb (pb|lo)` to override). This is a Slice 1 UX choice flagged for Codex review.
- **Risk:** A future change reintroduces durable-role rendering on the interactive path. **Mitigation:** Slice 9 regression tests cover the contract; doctor checks fail on regressions.
- **Rollback (scoping):** scoping introduces no system state changes. Withdrawal is via a WITHDRAWN status on -002 if needed.
- **Rollback (post-implementation):** each slice can be reverted independently. Slice 8 rule-text reverts to pre-revision text; runtime slices revert to durable-keyed behavior. The session-state marker file is deleted on revert.

## Owner Decisions / Input

This scoping proceeds on six AskUserQuestion decisions captured in session S371 (2026-05-29), all answered via the canonical AskUserQuestion tool. The AskUserQuestion turn-by-turn evidence is the durable owner-approval record per `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` and the AUQ-only enforcement stack. The owner-decision-tracker hook (`.claude/hooks/owner-decision-tracker.py`) recorded each decision to `memory/pending-owner-decisions.md` with `detected_via: ask_user_question`.

1. **Decision 1 - Override scope:** "Full session override (everything but headless dispatch)". The session-stated role applies to disclosure, AXIS 2 surface, focus menu, MemBase attribution, AUQ-keyed routing. Headless dispatch remains durable-keyed. Source: AskUserQuestion in S371, question header "Override scope".

2. **Decision 2 - Undeclared interactive default:** "Fall back to durable role assignment". Sessions without an init keyword inherit the durable role as the fallback. Source: AskUserQuestion in S371, question header "Undeclared default".

3. **Decision 3 - Role persistence:** "Session-scoped lifetime - keyword declares for the rest of this session, no persistence file" (corrected from the initial mis-selection per the owner's re-ask request). Override held in ephemeral session-scoped marker; compaction/resume loses the override; mid-session re-typing overrides. No durable record. Source: AskUserQuestion in S371, question header "Role persistence" (re-asked after the owner reported a selection error).

4. **Decision 4 - Declaration UX:** "Canonical init keyword only - `::init gtkb (pb|lo)` is the single declarator". No conversational aliases. No CLI surface. Source: AskUserQuestion in S371, question header "Declaration UX".

5. **Decision 5 - Landing path:** "Architecture-first - ADR + DCL + GOV scoping bridge, then implementation slices". This proposal IS the scoping bridge per that decision. Source: AskUserQuestion in S371, question header "Landing path".

6. **Decision 6 - Disclosure presentation:** "Session role only - show 'Role being assumed: Loyal Opposition'; durable role not mentioned". The startup disclosure under override surfaces only the session-stated role. Durable role remains observable via CLI surfaces and the registry projection. Source: AskUserQuestion in S371, question header "Disclosure transparency".

Owner-directive context (S371 originating message, verbatim above in `## Problem Statement`) is the chat-derived origin that triggered the AskUserQuestion sequence. Per `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`, the chat-derived text was converted into specific structured decisions via the AskUserQuestion tool; the AskUserQuestion answers are the durable approval evidence.

## Codex Review Asks

1. Confirm or NO-GO the three-artifact framing (`ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` + `DCL-SESSION-ROLE-RESOLUTION-001` + `GOV-SESSION-ROLE-AUTHORITY-001`). Alternative framings to consider: single ADR with inline constraints, or separate ADRs per dispatch context.
2. Confirm or NO-GO the 9-slice implementation plan decomposition. Are any slices missing? Are any slices over-bundled?
3. Scrutinize the receiver-side decision-table revision to `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`. Does the `INTERACTIVE_OVERRIDE_AUTHORIZED` decision in the absent-env-var row weaken any safety property that today's `SPOOF_FALLBACK` provides?
4. Scrutinize the ephemeral session-state marker design. Is session-id-keying sufficient for staleness detection? Should the marker carry a process id or pid hash to detect cross-process leakage?
5. Flag any specification this proposal should cite but does not. The Specification Links section is comprehensive to the author's knowledge; an applicability preflight run after filing will surface gaps.
6. Flag any scope element that belongs in a sibling scoping proposal rather than the implementation slices. Candidate split: should the `CLAUDE.md` / `AGENTS.md` / rule-file updates (Slice 8) be a separate documentation-scoping bridge rather than a slice of this thread? Owner preference is for unified threads; flagging for Codex judgment.
7. Confirm or NO-GO the disclosure-only-shows-session-role decision (S371 AUQ Decision 6). The alternative (transparently showing both) is rejected by owner decision; this ask is to confirm the architecture is internally consistent given that decision.
8. Flag whether a new MemBase project (e.g., `PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE`) with project-scoped implementation authorization should be created to cover the 9 implementation slices, or whether per-slice direct AUQ approval is sufficient. The owner did not pre-decide this; flagging for Codex recommendation.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
