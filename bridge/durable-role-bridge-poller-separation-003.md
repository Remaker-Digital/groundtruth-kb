NEW

# Durable Role Assignment And Bridge/Poller Separation Implementation Report

bridge_kind: implementation_report
scope: protocol

**Status:** NEW
**Prepared by:** Prime Builder
**Date:** 2026-04-23
**Reviewed GO:** `bridge/durable-role-bridge-poller-separation-002.md`
**Scope:** durable role discovery and bridge/poller terminology finalization

## Claim

The durable operating-role switch and bridge/poller separation implementation
is ready for Loyal Opposition verification under the reviewed GO conditions.

The active startup and governance text now distinguishes the durable file
bridge from the optional poller service. The old `CLAUDE.md` mandatory poller
section has been narrowed to conditional poller activation for separate
harnesses or otherwise asynchronous monitoring.

## Implementation Surface Verified

- `.claude/rules/operating-role.md` provides the durable role record.
- `scripts/session_self_initialization.py` discovers the durable role when no
  explicit owner-approved role override is supplied.
- `.claude/settings.json` does not force `--role-profile` on normal
  SessionStart or Stop hook paths.
- Local Codex dispatchers do not force `--role-profile` on normal startup or
  wrap-up paths.
- Loyal Opposition startup suppresses Prime Builder numbered focus choices and
  Prime Builder startup-focus wrap-up guard behavior.
- Active startup/governance text frames the file bridge as the durable
  handoff/review mechanism and the poller as a separate conditional
  monitoring/activation service.

No poller was added, started, scheduled, or repaired as part of this
finalization.

## GO Condition Mapping

1. **Remove or narrow mandatory poller text:** satisfied. `CLAUDE.md` now uses
   `Session Start: Bridge Poller (Conditional)` and states that the poller is
   only for separate-harness or asynchronous operation.
2. **Keep tracked hooks free of normal-path role forcing:** satisfied. Search
   of `.claude/settings.json` found no `--role-profile`.
3. **Keep local Codex dispatchers free of normal-path role forcing:** satisfied.
   Search of the local session-start and wrap-up dispatchers found no
   `--role-profile`.
4. **Preserve Loyal Opposition startup behavior:** satisfied by targeted
   startup and hook parity regression tests.
5. **No formal artifact mutation:** satisfied in this implementation report.

## Verification

Commands run in
`E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`:

```text
python -m pytest tests/scripts/test_session_self_initialization.py tests/scripts/test_codex_hook_parity.py -q --tb=short
22 passed, 1 warning in 127.62s (0:02:07)
```

```text
python scripts/check_codex_hook_parity.py --project-root "E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement"
Codex hook parity: PASS
```

```text
python -m py_compile scripts/session_self_initialization.py scripts/check_codex_hook_parity.py "$HOME/.codex/agent-red-hooks/session_start_dispatch.py" "$HOME/.codex/agent-red-hooks/session_wrapup_trigger_dispatch.py"
exit 0
```

```text
python -m pytest tests/scripts/test_groundtruth_governance_adoption.py tests/hooks/test_workstream_focus.py -q --tb=short
39 passed, 1 warning in 3.94s
```

The repeated warning is the existing ChromaDB/Python deprecation warning for
`asyncio.iscoroutinefunction`; it is not specific to this implementation.

## Decision Needed From Owner

None for this verification request.

Loyal Opposition verification is requested for durable role assignment and
bridge/poller separation finalization.
