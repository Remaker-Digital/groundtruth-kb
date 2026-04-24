GO

# Loyal Opposition Review: Durable Role Assignment And Bridge/Poller Separation

## Verdict

GO, with required finalization conditions.

Prime Builder may continue implementation of the durable operating-role switch
and bridge/poller terminology cleanup. The proposal is directionally correct,
has enough concrete implementation scope, and the current draft evidence shows
the core startup and hook behavior is already testable.

## Rationale

The durable role record approach is acceptable for both Claude Code and Codex.
The active role is stored in `.claude/rules/operating-role.md`, with
`active_role: loyal-opposition` and documented allowed values at lines 5 and
11-15. The startup generator discovers that record when no explicit
`--role-profile` is supplied: `scripts/session_self_initialization.py:2185-2205`
reads `active_role`, validates it against `ROLE_PROFILES`, and
`build_startup_model(...)` resolves the role at lines 2208-2212.

The role-specific startup behavior is separated cleanly enough for this plan.
`scripts/session_self_initialization.py:2786-2807` renders the Loyal Opposition
startup task instead of Prime Builder session-focus choices when the model is
Loyal Opposition, and `scripts/session_self_initialization.py:4363-4371` avoids
arming the startup-focus wrap-up guard for Loyal Opposition.

The hook compatibility plan is acceptable. Claude Code project hooks call
`session_self_initialization.py` without `--role-profile` in both SessionStart
and Stop commands at `.claude/settings.json:21-38`. The local Codex
SessionStart dispatcher reads `.claude/rules/operating-role.md` at
`C:\Users\micha\.codex\agent-red-hooks\session_start_dispatch.py:15` and
`46-55`, suppresses Prime Builder numbered focus choices for Loyal Opposition
at lines 104-110, avoids arming the wrap-up guard for Loyal Opposition at
lines 162-165, and launches startup without `--role-profile` at lines 169-177.
The Codex explicit wrap-up dispatcher launches wrap-up without forcing a role
profile at `C:\Users\micha\.codex\agent-red-hooks\session_wrapup_trigger_dispatch.py:103-110`
and the subsequent subprocess argument list.

The bridge/poller distinction is acceptable as an implementation target, but it
must be completed before finalization. Current project text still contains
mandatory poller language in `CLAUDE.md:169-177`, including a recurring
`CronCreate` instruction. That is not a blocker to approving the proposal,
because the proposal explicitly includes terminology cleanup, but it is a
required completion condition.

## Findings

### P2 - Legacy mandatory poller text must be removed or narrowed

Evidence:

- `CLAUDE.md:169-177` still says "Session Start: Bridge Poller (Mandatory)" and
  instructs creation of a recurring in-session poller.
- The proposal's Scope In includes documentation updates that distinguish the
  durable file bridge from an optional poller service.

Risk/impact:

If this text remains after implementation, a fresh Prime Builder session may
still treat poller creation as mandatory even in the single-harness
role-toggle case, contradicting Mike's direction and the durable-role design.

Required action:

Before finalizing, update startup/governance/bootstrap text so the file bridge
is the durable control-transfer mechanism and any poller is optional automation
for separate live harnesses. At minimum, include the active startup files that
still say the poller is mandatory.

### P3 - Explicit role override remains a policy-controlled escape hatch

Evidence:

- `scripts/session_self_initialization.py:4351-4356` keeps `--role-profile`
  available.
- `scripts/session_self_initialization.py:2202-2205` gives explicit
  `role_profile` precedence over durable discovery.

Risk/impact:

This matches the proposal for tests and owner-approved one-off invocations, but
it remains possible for a manual command to bypass the durable record.

Required action:

Keep regression checks that tracked hooks do not pass `--role-profile`, and
document that manual role overrides require owner-approved one-off use.

## Verification

Commands run from `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`:

```powershell
python -m pytest tests/scripts/test_session_self_initialization.py tests/scripts/test_codex_hook_parity.py -q --tb=short
```

Result: `17 passed, 1 warning` in 106.23 seconds. The warning was a third-party
`chromadb` deprecation warning for Python 3.14.

```powershell
python scripts/check_codex_hook_parity.py --project-root "E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement"
```

Result: `Codex hook parity: PASS`.

```powershell
python -m py_compile scripts/session_self_initialization.py scripts/check_codex_hook_parity.py "$HOME/.codex/agent-red-hooks/session_start_dispatch.py" "$HOME/.codex/agent-red-hooks/session_wrapup_trigger_dispatch.py"
```

Result: exit code 0.

Optional broader governance regression:

```powershell
python -m pytest tests/scripts/test_groundtruth_governance_adoption.py tests/hooks/test_workstream_focus.py -q --tb=short
```

Result: `33 passed, 1 warning` in 3.32 seconds. The warning was the same
third-party `chromadb` deprecation warning.

## Required Conditions Before Finalization

1. Complete bridge/poller terminology cleanup in active startup and governance
   text, including current mandatory poller wording in `CLAUDE.md`.
2. Keep `.claude/settings.json` and local Codex dispatchers free of normal-path
   `--role-profile` forcing.
3. Preserve Loyal Opposition startup behavior: no Prime Builder numbered focus
   choices and no Prime Builder startup-focus wrap-up guard.
4. Do not mutate formal GOV, SPEC, PB, ADR, DCL, or Deliberation Archive
   records without separate approval evidence.

## Owner Decision Needed

None.
