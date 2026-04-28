GO

# Harness-State Preferences Path CLI Override - Codex Review

**Status:** GO
**Date:** 2026-04-28
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/harness-state-preferences-path-cli-2026-04-28-001.md`

## Claim

GO for the narrow CLI override proposal, with corrected verification pathing.

The proposal targets the right defect class: the dashboard rehearsal lane
threads sandbox-relative role-record and lifecycle-guard paths into the legacy
startup generator, but it does not thread a sandbox-relative startup
preferences path. Because `session_self_initialization.py` is invoked from the
canonical checkout, its default preferences path resolves under canonical
`E:\GT-KB\applications\Agent_Red\harness-state\...`, causing the audit-hook
read violation.

## Evidence

- `scripts/session_self_initialization.py` defines
  `DEFAULT_USER_STARTUP_PREFERENCES_PATH` under
  `AGENT_RED_HARNESS_STATE_ROOT / "codex" / "session-startup-preferences.json"`.
- `_user_startup_preferences_path()` already supports
  `GTKB_STARTUP_PREFERENCES_PATH`, so the proposed CLI argument can reuse an
  existing override channel instead of inventing a new preferences reader.
- `scripts/rehearse/_dashboard_regen.py:_build_generator_argv()` currently
  passes `--role-record-path` and `--lifecycle-guard-path` into the sandbox,
  but has no equivalent `--user-preferences-path`.
- The proposed fix is smaller and more stable than copying additional modules
  into the sandbox or widening audit-hook allowances.

## GO Conditions

1. Add `--user-preferences-path` to `scripts/session_self_initialization.py`.
2. Preserve default production behavior when the CLI argument is omitted:
   existing `GTKB_STARTUP_PREFERENCES_PATH` override first, then the canonical
   harness-state default.
3. When the CLI argument is supplied, it must affect both dashboard-opening
   model generation and startup dashboard-opening behavior.
4. `scripts/rehearse/_dashboard_regen.py:_build_generator_argv()` must pass a
   sandbox-relative preferences path under:
   `applications/Agent_Red/harness-state/codex/session-startup-preferences.json`.
5. Do not add audit-hook allowlist entries for the canonical preferences file;
   the lane should stop reading it.
6. Verification artifacts must stay under `E:\GT-KB`. Do not use `C:/temp` or
   any other outside-root output directory for the implementation evidence.

## Candidate B Disposition

Candidate B is acceptable because it reuses the existing environment override
surface and keeps implementation scope small. If implemented by setting
`GTKB_STARTUP_PREFERENCES_PATH` inside `main()`, set it only after argument
parsing and before startup model generation or dashboard-open checks. Avoid
module-import-time mutation.

If Prime Builder chooses an explicit parameter-threading implementation instead,
that is also acceptable provided it remains narrow and satisfies the GO
conditions above. No broader harness-state redesign belongs in this bridge.

## Required Tests

1. A `session_self_initialization.py` test proving `--user-preferences-path`
   overrides the default preferences path.
2. A fallback test proving omitted CLI arg + omitted env var preserves default
   behavior.
3. A `_dashboard_regen.py` argv test proving the lane passes the sandbox-local
   `--user-preferences-path`.
4. A Slice 11 dashboard rehearsal lane re-run with output under `E:\GT-KB`
   showing `status: ok`, `audit_hook_violations: 0`, and empty
   `violations.json`.

## Decision Needed From Owner

None.

