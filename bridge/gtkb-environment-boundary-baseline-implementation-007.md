REVISED

# GTKB Environment Boundary Baseline — Revised Post-Implementation Report (Rev 3)

bridge_kind: post_implementation_report
scope: protocol
work_item_ids: [GTKB-ISOLATION-011]
target_paths: ["scripts/check_environment_isolation.py", "tests/scripts/test_check_environment_isolation.py"]

## Summary

Addresses the blocking finding in `bridge/gtkb-environment-boundary-baseline-implementation-006.md`:
Windows drive-letter absolute host binds (e.g. `C:/temp/config:/app/config:ro`) were
bypassing the compose boundary check because the regex could not represent a drive-
letter prefix and `_is_host_path()` did not recognize `<letter>:/<path>` as a host path.

Revision 3 fixes both layers and adds focused regression coverage for `C:/`, `D:/`, and
`C:\\` forms.

## Change From Revision 2 (-005)

### `scripts/check_environment_isolation.py`

Two coordinated changes:

1. **Regex update** — `_COMPOSE_VOLUME_PATTERN` rewritten with alternation so the host
   group can match either a Windows drive-letter path (`[A-Za-z]:[/\\][^:\"]*`) or a
   regular colonless path. The alternation order matters: the drive-letter branch must
   appear first because its captured text contains a `:` that would otherwise be
   consumed as the host/container separator.

2. **Host recognition + out-of-app classification** — new
   `_WINDOWS_DRIVE_LETTER_PATTERN` module constant (`^[A-Za-z]:[/\\]`) is consulted in
   two places:
   - `_is_host_path()` now returns `True` for drive-letter prefixes (so those binds are
     not silently treated as named volumes).
   - The `COMPOSE_HOST_BIND_OUT_OF_APP` classifier in `check_compose()` now flags
     drive-letter paths as out-of-app, alongside the existing `/` and `..` rules.

Together these ensure every Windows drive-letter absolute bind produces the same
`COMPOSE_HOST_BIND_OUT_OF_APP` finding that a POSIX-absolute `/foo/bar` bind would
produce. The `:ro` option is irrelevant to the out-of-app policy (absolute paths are
rejected regardless).

### `tests/scripts/test_check_environment_isolation.py`

Three new focused regression tests (32 → 35 tests in the checker module):

1. **`test_compose_rejects_windows_drive_letter_bind`** — verifies
   `C:/temp/config:/app/config:ro` (with `:ro`) is rejected as out-of-app.
2. **`test_compose_rejects_windows_drive_letter_bind_without_ro`** — verifies
   `D:/data:/app/data` (without `:ro`) is rejected as out-of-app, confirming the
   drive-letter path triggers the higher-severity policy regardless of options.
3. **`test_compose_rejects_windows_drive_letter_bind_with_backslash`** — verifies
   `C:\\temp\\config:/app/config:ro` (backslash separator) is also rejected.

## Live Verification

### Focused pytest lane

```
$ python -m pytest tests/scripts/test_check_environment_isolation.py tests/scripts/test_release_candidate_gate.py -q --tb=short
...
44 passed in 0.96s
```

Was `41 passed` on `-005`; now `44 passed` (the three new Windows drive-letter tests).
Release-gate ordering test still green.

### Live checker on current repo

```
$ python scripts/check_environment_isolation.py --json
{
  "cwd": "E:\\Claude-Playground\\CLAUDE-PROJECTS\\Agent Red Customer Engagement",
  ...
  "findings": [],
  "git_branch": "main",
  ...
}
```

Zero findings on the live repo. No regression introduced into live operation.

### Direct repro of the `-006` scenario

Created a temp directory with `docker-compose.yml` containing
`- C:/temp/config:/app/config:ro` and ran the checker against it:

```
findings: [
  {'code': 'DOCKERIGNORE_MISSING_FILE', 'message': '.dockerignore not found at repository root', ...},
  {'code': 'COMPOSE_HOST_BIND_OUT_OF_APP',
   'message': "host bind 'C:/temp/config:/app/config' must stay within the app repository (use './<path>')",
   'path': 'docker-compose.yml:4',
   'severity': 'error'}
]
```

The targeted `COMPOSE_HOST_BIND_OUT_OF_APP` finding fires exactly as required by
`-006`'s required action items. (The dockerignore finding is orthogonal — it reflects
the minimal temp-dir layout, not the compose fix.)

## Files Changed (Commit-Local Delta)

```
 scripts/check_environment_isolation.py         | ~20 lines (regex + constant + 4-line if clause)
 tests/scripts/test_check_environment_isolation.py | +40 lines (3 new tests)
```

No other files modified. All prior `-003` baseline work (`.dockerignore` hardening,
release-gate wiring, 30-test module) and all prior `-005` generalization work
(`_SOURCE_BIND_PREFIXES` removal, 2 config-path tests) remain in place and unchanged;
this revision only adds Windows drive-letter handling.

## Required Action Items From -006

1. **Update compose volume parsing / host-path detection so Windows drive-letter
   absolute host binds are recognized as host binds and rejected by
   `COMPOSE_HOST_BIND_OUT_OF_APP`** — DONE via the regex alternation and the
   `_WINDOWS_DRIVE_LETTER_PATTERN` additions to `_is_host_path()` and the
   out-of-app classifier.
2. **Add focused regression coverage for Windows absolute host bind forms
   (`C:/...` at minimum, plus any additional form the checker intends to support)** —
   DONE via three new tests: forward-slash with `:ro`, forward-slash without `:ro`,
   backslash form.
3. **Re-run the live checker and focused pytest suite and submit a revised
   post-implementation report for verification** — DONE (this file).

## Non-Scope Confirmation

- No other files in the Phase 3 baseline scope were modified.
- `.dockerignore` hardening from `-003` unchanged.
- Release-gate wiring from `-003` unchanged.
- No `.devcontainer` / Codespaces changes, workflow-file edits, or startup/hook work.

## Requested Verdict

VERIFIED.

## Prior Deliberations (per deliberation-protocol.md)

- `DELIB-0877` — GTKB application-isolation planning context.
- NO-GO at `-004` and `-006` are the direct priors for this thread. `-006` specifically
  identified the Windows drive-letter gap that this revision closes.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
