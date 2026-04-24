# Agent Red - Durable Role Assignment And Bridge/Poller Separation Proposal

## Claim

Prime Builder should implement the durable operating-role switch for fresh
sessions, and should clarify that the file bridge is the control-passing
mechanism while any poller is an optional service used only when Prime Builder
and Loyal Opposition are separate harnesses.

This proposal asks Loyal Opposition to review the implementation plan before
any further implementation or finalization work continues.

## Owner Direction

Mike approved using Codex for both Prime Builder and Loyal Opposition while
Claude Code is unavailable, because that is better than suspending the normal
development process.

Mike further directed that:

- session start should discover the operating mode for that session from a
  durable record
- the durable record may be toggled for the next session
- before continuing implementation, Prime Builder should file an implementation
  proposal for Loyal Opposition review
- this situation does not require a bridge poller
- future project language should distinguish the bridge mechanism from the
  poller service

## Problem

The current project language has two related but distinct concepts that can be
blurred:

1. The Prime Builder / Loyal Opposition bridge: shared versioned markdown files
   plus `bridge/INDEX.md`, used to transfer review control.
2. The bridge poller: an optional automation layer that periodically scans the
   bridge when Prime Builder and Loyal Opposition are separate running
   harnesses.

For a single harness toggling roles across fresh sessions, the bridge remains
necessary as the durable control-transfer record, but an active poller is not
necessary. Treating the poller as inherent to the bridge risks extra automation
complexity and misleading startup requirements.

## Proposed Implementation

### 1. Durable role record

Add a durable role assignment record at:

- `.claude/rules/operating-role.md`

The record should include a machine-readable line:

```text
active_role: loyal-opposition
```

Allowed values should be:

- `prime-builder`
- `loyal-opposition`
- `acting-prime-builder`

Fresh-session startup should read this durable record when no explicit
owner-approved role override is provided.

### 2. Startup role discovery

Update `scripts/session_self_initialization.py` so:

- `build_startup_model(..., role_profile=None)` discovers the role from
  `.claude/rules/operating-role.md`
- explicit `--role-profile` remains available for tests and owner-approved
  one-off command invocations
- default CLI startup and wrap-up behavior does not force Prime Builder
- Loyal Opposition startup suppresses Prime Builder numbered focus choices
- Loyal Opposition startup does not arm the Prime Builder startup-focus wrap-up
  suppression guard

### 3. Claude Code compatibility

Keep `.claude/settings.json` free of `--role-profile` in both `SessionStart`
and `Stop` hooks so Claude Code uses the shared durable discovery path.

Add regression coverage that fails if Claude Code hooks force a role profile.

### 4. Codex compatibility

Update the local Codex desktop dispatchers under:

- `C:\Users\micha\.codex\agent-red-hooks\session_start_dispatch.py`
- `C:\Users\micha\.codex\agent-red-hooks\session_wrapup_trigger_dispatch.py`

The dispatchers should:

- read `.claude/rules/operating-role.md`
- avoid passing `--role-profile` for normal startup/wrap-up
- render Loyal Opposition first-response instructions without Prime Builder
  numbered focus choices
- arm the Prime Builder startup-focus guard only when the active role is not
  Loyal Opposition

### 5. Bridge/poller terminology separation

Update project governance and bootstrap text so it uses this distinction:

- Bridge: `bridge/INDEX.md` plus versioned bridge files; this is the durable
  control-transfer mechanism.
- Poller: optional automation that scans the bridge when separate harnesses
  need asynchronous handoff.

The implementation should not add, require, or start a bridge poller for the
single-harness role-toggle case.

### 6. Cached startup report

Refresh the cached startup report after the durable role record is set so the
next fresh Codex session does not briefly present stale Prime Builder startup
text before asynchronous refresh completes.

## Current Draft State

Prime Builder has local draft changes in the workspace for the durable role
record, startup discovery, hook parity checks, cached startup report, and local
Codex dispatcher behavior. Those changes should be treated as draft
implementation pending Loyal Opposition review of this proposal.

No further implementation finalization should proceed until Loyal Opposition
returns `GO` or `NO-GO` on this bridge entry.

## Scope In

- Durable operating-role record.
- Session startup and wrap-up role discovery.
- Claude Code and Codex hook compatibility checks.
- Tests proving unforced role discovery.
- Documentation updates that distinguish bridge from poller.
- Cached startup report refresh.

## Scope Out

- Adding a new bridge poller.
- Starting, scheduling, or repairing an external poller service.
- Changing the core bridge file format.
- Replacing `bridge/INDEX.md` as the authoritative review queue.
- Mutating formal GOV/SPEC/PB/ADR/DCL artifacts as part of this implementation
  without separate required approval evidence.

## Proposed Verification

Run targeted tests:

```powershell
python -m pytest tests/scripts/test_session_self_initialization.py tests/scripts/test_codex_hook_parity.py -q --tb=short
python scripts/check_codex_hook_parity.py --project-root "e:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement"
python -m py_compile scripts/session_self_initialization.py scripts/check_codex_hook_parity.py "$HOME/.codex/agent-red-hooks/session_start_dispatch.py" "$HOME/.codex/agent-red-hooks/session_wrapup_trigger_dispatch.py"
```

Optional broader governance regression:

```powershell
python -m pytest tests/scripts/test_groundtruth_governance_adoption.py tests/hooks/test_workstream_focus.py -q --tb=short
```

## Risks

- If a local Claude Code settings override forces `--role-profile`, the shared
  durable role record can be bypassed. The tracked settings and parity tests
  should prevent this in the project baseline, but workstation-local settings
  may still need manual inspection if behavior differs.
- If bridge protocol documentation continues to describe polling as inherent to
  the bridge, future agents may reintroduce unnecessary poller work. The
  documentation update should make the poller explicitly optional.
- Because Codex is serving both roles while Claude Code is unavailable, review
  independence is weaker than two separate harnesses. The bridge artifact still
  preserves role separation and review timing, but not model/vendor diversity.

## Loyal Opposition Review Asks

1. Is the durable role record approach acceptable for both Claude Code and Codex?
2. Is the bridge/poller distinction precise enough to prevent unnecessary
   poller work in the single-harness role-toggle case?
3. Are the proposed verification commands sufficient before finalizing the
   implementation?
4. Are there any blockers that require a `NO-GO` before Prime Builder continues?

## Requested Verdict

`GO` if this implementation plan is acceptable, or `NO-GO` with required
changes before Prime Builder continues implementation.

