VERIFIED

# Loyal Opposition Verification: Durable Role Assignment And Bridge/Poller Separation

## Role Authority

- Effective role: Loyal Opposition
- Authority source path: `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\.claude\rules\operating-role.md`
- Required durable role: `active_role: loyal-opposition`
- Observed durable role: `active_role: loyal-opposition`
- Scanner name: Codex automated Loyal Opposition bridge review scan

## Verdict

VERIFIED.

The implementation satisfies the GO conditions from
`bridge/durable-role-bridge-poller-separation-002.md` and the post-implementation
claim in `bridge/durable-role-bridge-poller-separation-003.md`.

## Evidence

- Durable role authority is present: `.claude/rules/operating-role.md:5`
  declares `active_role: loyal-opposition`, and `.claude/rules/operating-role.md:39`
  frames the file bridge as separate from the poller.
- Startup discovers the durable role when no explicit profile is supplied:
  `scripts/session_self_initialization.py:2295` defines durable role discovery,
  `scripts/session_self_initialization.py:2304` parses `active_role`, and
  `scripts/session_self_initialization.py:2318` builds the startup model from
  the discovered role.
- Loyal Opposition startup suppresses Prime Builder focus controls and keeps
  poller activation conditional: `scripts/session_self_initialization.py:2816`
  through `scripts/session_self_initialization.py:2824`.
- Normal Claude Code hook paths do not force a role profile:
  `.claude/settings.json:21` through `.claude/settings.json:38` call
  `session_self_initialization.py` for SessionStart and Stop without
  `--role-profile`.
- Local Codex startup dispatch reads the durable role record and does not pass
  `--role-profile`: `C:\Users\micha\.codex\agent-red-hooks\session_start_dispatch.py:51`
  through `C:\Users\micha\.codex\agent-red-hooks\session_start_dispatch.py:60`
  read the active role, and
  `C:\Users\micha\.codex\agent-red-hooks\session_start_dispatch.py:251`
  through `C:\Users\micha\.codex\agent-red-hooks\session_start_dispatch.py:259`
  launch startup without a forced role profile.
- Local Codex wrap-up dispatch does not force a role profile:
  `C:\Users\micha\.codex\agent-red-hooks\session_wrapup_trigger_dispatch.py:114`
  through `C:\Users\micha\.codex\agent-red-hooks\session_wrapup_trigger_dispatch.py:123`.
- `CLAUDE.md:169` through `CLAUDE.md:177` now describes the bridge poller as
  conditional and limits activation to separate-harness or otherwise
  asynchronous monitoring cases.

## Verification Commands

Commands run from
`E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`:

```powershell
python -m pytest tests/scripts/test_session_self_initialization.py tests/scripts/test_codex_hook_parity.py -q --tb=short
```

Result: `22 passed, 1 warning in 119.01s`. The warning is the existing
ChromaDB/Python `asyncio.iscoroutinefunction` deprecation warning.

```powershell
python scripts/check_codex_hook_parity.py --project-root "E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement"
```

Result: `Codex hook parity: PASS`.

```powershell
python -m py_compile scripts/session_self_initialization.py scripts/check_codex_hook_parity.py "$HOME/.codex/agent-red-hooks/session_start_dispatch.py" "$HOME/.codex/agent-red-hooks/session_wrapup_trigger_dispatch.py"
```

Result: exit code 0.

```powershell
python -m pytest tests/scripts/test_groundtruth_governance_adoption.py tests/hooks/test_workstream_focus.py -q --tb=short
```

Result: `39 passed, 1 warning in 3.60s`. The warning is the same existing
ChromaDB/Python deprecation warning.

## Findings

No blocking findings.

Residual risk: the worktree contains broad uncommitted changes, so this
verification relies on targeted live-file evidence and the regression commands
above rather than git-clean attribution. That does not block verification of
this bridge item.

## Required Action Items Or Conditions

None.

## Decision Needed From Owner

None.
