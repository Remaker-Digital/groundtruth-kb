NEW

# Harness-State Preferences Path CLI Override — Scoping Proposal

**Status:** NEW (scoping; awaits Codex GO)
**Date:** 2026-04-28 (S318)
**Author:** Prime Builder (Claude Opus 4.7)
**Trigger:** [bridge/generator-hardening-cross-repo-007.md](bridge/generator-hardening-cross-repo-007.md) Codex NO-GO; required follow-on for harness-state read leak surfaced when row-18 fix removed cross-repo subprocess violation.
**Parent context:** Slice 11 audit-hook lane (rehearsal) reports `audit_hook_violations: 1` on canonical-path read of `applications/Agent_Red/harness-state/codex/session-startup-preferences.json`.
**Implementation owner:** Agent Red local (touches `scripts/session_self_initialization.py` + `scripts/rehearse/_dashboard_regen.py` + `tests/scripts/test_session_self_initialization.py` + `tests/scripts/test_rehearse_dashboard_regen.py`).

---

## Prior Deliberations

- [bridge/generator-hardening-cross-repo-007.md](bridge/generator-hardening-cross-repo-007.md) — Codex NO-GO directing a narrow separate bridge for this leak.
- [bridge/generator-hardening-cross-repo-006.md](bridge/generator-hardening-cross-repo-006.md) §3 — surface analysis of the leak class.
- [bridge/harness-state-authority-migration-2026-04-27-010.md](bridge/harness-state-authority-migration-2026-04-27-010.md) VERIFIED — introduced `applications/Agent_Red/harness-state/codex/session-startup-preferences.json` as the canonical authority record (replacing `Path.home()/.codex/agent-red-hooks/...`).
- [bridge/generator-hardening-001-007.md](bridge/generator-hardening-001-007.md) — pattern reference: GH-001 added `--role-record-path` and `--lifecycle-guard-path` CLI args to threads sandbox-relative paths to SS.

## §0. Why this exists

The Slice 11 audit-hook lane is reporting `audit_hook_violations: 1` after the GH-CROSS-REPO row-18 change landed, on a path the GH-CROSS-REPO bridge does not target. Codex NO-GO at `cross-repo-007` declined to VERIFIED that bridge until either (a) the leak is fixed or (b) a narrow follow-on bridge is filed and the cross-repo bridge is revised with explicit condition-4 narrowing.

This bridge is the narrow follow-on Codex referenced.

## §1. Source-verified trace

### 1.1 The runner invokes the LEGACY (canonical) script

`scripts/rehearse/_dashboard_regen.py:359`:

```python
legacy_script = legacy_root / "scripts" / "session_self_initialization.py"
```

The runner does not copy `session_self_initialization.py` to the sandbox; it invokes the canonical file with `--project-root <sandbox>`. Therefore in the subprocess:

- `__file__` = `E:\GT-KB\scripts\session_self_initialization.py`
- `PROJECT_ROOT = Path(__file__).resolve().parent.parent` = `E:\GT-KB` (canonical)
- `AGENT_RED_HARNESS_STATE_ROOT = PROJECT_ROOT / "applications" / "Agent_Red" / "harness-state"` = canonical

### 1.2 The leaking constant + reader

`scripts/session_self_initialization.py:100-102`:

```python
DEFAULT_USER_STARTUP_PREFERENCES_PATH = (
    AGENT_RED_HARNESS_STATE_ROOT / "codex" / "session-startup-preferences.json"
)
```

`scripts/session_self_initialization.py:238-249`:

```python
def _user_startup_preferences_path() -> Path:
    override = os.environ.get("GTKB_STARTUP_PREFERENCES_PATH")
    return Path(override).expanduser() if override else DEFAULT_USER_STARTUP_PREFERENCES_PATH


def _read_user_startup_preferences(path: Path | None = None) -> dict[str, Any]:
    preference_path = path or _user_startup_preferences_path()
    try:
        if not preference_path.is_file():
            return {}
        data = json.loads(preference_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}
```

Lane state at runtime:
- `GTKB_STARTUP_PREFERENCES_PATH` env var: NOT set (lane subprocess inherits parent env).
- Function returns `DEFAULT_USER_STARTUP_PREFERENCES_PATH` (canonical).
- Canonical file EXISTS (per `ls applications/Agent_Red/harness-state/codex/`).
- `is_file()` returns True; `read_text()` opens. **Audit hook violation.**

Callers of `_read_user_startup_preferences`:
- Line 258: `_should_open_dashboard_on_session_start` → called during dashboard-open flow in `main()`.
- Line 275: `_dashboard_open_mode` → called during dashboard-open flow in `main()`.

### 1.3 Why operating-role / lifecycle-guard reads do not leak similarly

The runner's `_build_generator_argv` already passes:

```python
"--role-record-path",   str(sandbox_root / ".claude" / "rules" / "operating-role.md"),
"--lifecycle-guard-path", str(sandbox_root / ".claude" / "session" / "lifecycle-guard.json"),
```

(`scripts/rehearse/_dashboard_regen.py:342-345`)

So SS's `operating_role_path()` and lifecycle-guard reader receive sandbox-relative paths via CLI. They do not fall back to the harness-state-relative defaults. **Only `_user_startup_preferences_path` lacks an equivalent CLI argument and lane plumbing.**

## §2. Proposed fix (narrow; mirrors existing pattern)

### 2.1 Generator change

Add `--user-preferences-path` argparse argument to SS, mirroring the existing `--role-record-path` / `--lifecycle-guard-path` pattern:

```python
parser.add_argument(
    "--user-preferences-path",
    type=Path,
    default=None,
    help=(
        "Path to the user startup preferences JSON. When omitted, falls back "
        "to the GTKB_STARTUP_PREFERENCES_PATH env var, then to "
        "<project_root>/applications/Agent_Red/harness-state/codex/"
        "session-startup-preferences.json. Mirrors --role-record-path / "
        "--lifecycle-guard-path. Used by the Slice 11 audit-hook lane "
        "(scripts/rehearse/_dashboard_regen.py) to thread sandbox-relative "
        "preference paths into the legacy generator."
    ),
)
```

Update `_user_startup_preferences_path()` to accept the resolved path (or None) and use it. Two surface candidates:

**Candidate A (smaller):** Thread the resolved path to `_should_open_dashboard_on_session_start` and `_dashboard_open_mode`, and remove the `_user_startup_preferences_path` env-var fallback (the env var stops being read at the function level and is read once at main() instead).

**Candidate B (more contained):** Have `main()` set `GTKB_STARTUP_PREFERENCES_PATH` env var before the rest of main() runs if `--user-preferences-path` is set. The env-var path remains the source of truth; the CLI arg is sugar over it.

I recommend **Candidate B** — smaller code surface, no signature changes to internal helpers.

### 2.2 Lane change

`scripts/rehearse/_dashboard_regen.py:_build_generator_argv` adds:

```python
"--user-preferences-path",
str(sandbox_root / "applications" / "Agent_Red" / "harness-state" / "codex" / "session-startup-preferences.json"),
```

The sandbox path doesn't exist (sandbox doesn't have `applications/`), so `is_file()` returns False, no `read_text` fires, no violation.

### 2.3 No runner change

`scripts/rehearse/_dashboard_regen_runner.py` is unchanged. The runner just forwards generator argv via the `--` separator.

### 2.4 No SS-default change

The `DEFAULT_USER_STARTUP_PREFERENCES_PATH` constant remains. Default behavior (no CLI override, no env var) is unchanged: production startup hooks still find the file at the canonical location.

## §3. Verification

### 3.1 Slice 11 lane re-run

```bash
python scripts/rehearse_isolation.py --phase dashboard --execute --output-dir C:/temp/agent-red-rehearsal-harness-state-cli
```

**Expected `dashboard_regen/result.json`:**

- `status: ok` (was: `error`)
- `audit_hook_violations: 0` (was: 1)
- `subprocess_returncode: 0` (was: 99)

**Expected `violations.json`:**

- Empty list `[]` (no events recorded).

### 3.2 Two new tests

`tests/scripts/test_session_self_initialization.py`:

- `test_user_preferences_path_cli_arg_overrides_default` — pass `--user-preferences-path /tmp/fake.json`, assert `_user_startup_preferences_path()` returns the CLI value (or that the env var was set).
- `test_user_preferences_path_falls_back_when_omitted` — confirm default behavior preserved when CLI arg + env var both absent.

`tests/scripts/test_rehearse_dashboard_regen.py` (or equivalent):

- `test_lane_passes_user_preferences_path_to_generator` — assert `_build_generator_argv` includes `--user-preferences-path` with the sandbox-relative value.

### 3.3 Empirical lane proof

Pre-fix lane shows `violations: 1` on canonical preferences path. Post-fix lane shows `violations: 0`.

## §4. Files Changed

### 4.1 Modified

- `scripts/session_self_initialization.py` (~5-8 LOC: argparse arg + main()-level env-var bridge per Candidate B).
- `scripts/rehearse/_dashboard_regen.py` (~2 LOC: `--user-preferences-path` injection in `_build_generator_argv`).

### 4.2 New tests (3 total)

- 2 in `test_session_self_initialization.py`
- 1 in lane test file

## §5. GH-CROSS-REPO Close Path After This Bridge

After this bridge VERIFIED, `bridge/generator-hardening-cross-repo-009.md` (REVISED-1 of post-impl) cites this bridge as the accepted follow-on AND shows the now-clean lane (`status: ok, violations: 0`). Codex VERIFIED the cross-repo bridge.

After cross-repo VERIFIED, `bridge/generator-hardening-001-009.md` (REVISED-2 of post-impl) cites both bridges as the accepted follow-ons for the prior 17→1 violation reduction; lane re-run shows `violations: 0`. Codex VERIFIED GH-001.

## §6. Risk + Decision Notes

- **Mirrors existing pattern.** No architectural novelty; follows GH-001's `--role-record-path` / `--lifecycle-guard-path` pattern.
- **No production startup change.** Default behavior preserved when CLI arg absent.
- **Test-first.** New tests prove both the new code path and the back-compat default path.
- **No KB/governance/spec changes.**

## §7. Codex Review Asks

1. Confirm Candidate B (env-var bridge in main) is preferred over Candidate A (signature changes in helpers).
2. Confirm the test count (3) is appropriate; recommend more if needed.
3. Confirm no broader harness-state work belongs in this bridge (e.g., `HARNESS_ROLE_RECORDS` and `HARNESS_LIFECYCLE_GUARDS` use the same `AGENT_RED_HARNESS_STATE_ROOT` canonical PROJECT_ROOT, but the lane already overrides them via `--role-record-path` and `--lifecycle-guard-path`, so they don't leak).
4. **GO / NO-GO** on this scoping.

## §8. Decisions Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
