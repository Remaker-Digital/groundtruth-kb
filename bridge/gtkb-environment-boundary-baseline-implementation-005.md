NEW

# GTKB Environment Boundary Baseline — Revised Post-Implementation Report

bridge_kind: post_implementation_report
scope: protocol
work_item_ids: [GTKB-ISOLATION-011]
target_paths: ["scripts/check_environment_isolation.py", "tests/scripts/test_check_environment_isolation.py"]

## Summary

Addresses the blocking finding in `bridge/gtkb-environment-boundary-baseline-implementation-004.md`:
the compose read-only enforcement was narrower than the approved Phase 3 policy (limited to
`./src`, `./app`, `./scripts` prefixes). Revision 2 generalizes the rule to all repo-local
host binds by default, per the NO-GO's recommended-action path 1.

## Change From Revision 1 (-003)

### Single-file code change: `scripts/check_environment_isolation.py`

- Removed the `_SOURCE_BIND_PREFIXES` allowlist (`("./src", "./app", "./scripts")`).
- Removed the outer `if any(host.startswith(prefix) for prefix in _SOURCE_BIND_PREFIXES):`
  gate in `check_compose()`.
- The read-only enforcement now runs unconditionally for every bind that passes the
  `_is_host_path()` filter AND the `COMPOSE_HOST_BIND_OUT_OF_APP` check.
- Refined the finding message from `source bind` to `repo-local bind` to reflect the
  generalized scope.
- Finding code preserved as `COMPOSE_SOURCE_BIND_NOT_READONLY` to keep the existing
  regression test assertion stable.

After this change, any `./<path>` host bind without `:ro` produces a finding. Named
volumes (e.g. `mydata:/var/lib/mysql`) and absolute paths continue to be handled by the
existing `_is_host_path()` filter and `COMPOSE_HOST_BIND_OUT_OF_APP` check respectively —
no regression there.

### New regression coverage: `tests/scripts/test_check_environment_isolation.py`

Two new tests added (30 → 32 tests in the checker module):

1. **`test_compose_requires_any_repo_local_bind_read_only`** — verifies that a
   `./config:/app/config` bind (outside the legacy `./src`/`./app`/`./scripts` prefix
   list) now produces `COMPOSE_SOURCE_BIND_NOT_READONLY`. Direct regression guard for
   `-004` F1.
2. **`test_compose_accepts_repo_local_bind_with_read_only_opt`** — verifies that a
   `./config:/app/config:ro` bind is accepted with zero findings, confirming the `:ro`
   option satisfies the policy regardless of path prefix.

Both tests use the same `_load_checker_module()` + `tmp_path` pattern as the other
tests in the module.

## Live Verification

### Focused pytest lane

```
$ python -m pytest tests/scripts/test_check_environment_isolation.py tests/scripts/test_release_candidate_gate.py -q --tb=short
...
41 passed in 0.85s
```

Was `39 passed` on `-003`; now `41 passed` (the two new tests from this revision).
Release-gate ordering test (`test_release_candidate_gate.py`) still green — the new
checker invocation between `check_codex_hook_parity.py` and the pytest lane is
preserved.

### Live checker on current repo

```
$ python scripts/check_environment_isolation.py --json
{
  "cwd": "E:\\Claude-Playground\\CLAUDE-PROJECTS\\Agent Red Customer Engagement",
  "default_gtkb_dependency_mode": "released_package",
  "findings": [],
  "git_branch": "main",
  "git_remote": "https://github.com/Remaker-Digital/agent-red-customer-engagement.git",
  "repo_root": "E:/Claude-Playground/CLAUDE-PROJECTS/Agent Red Customer Engagement"
}
```

Zero findings on the live repo. The existing `docker-compose.yml` has no writable
repo-local binds, so no regression was introduced into live operation.

### Direct repro of the `-004` F1 scenario

The repro case cited in `-004` was a writable `./config:/app/config` bind. Under the
revised checker, that case now produces `COMPOSE_SOURCE_BIND_NOT_READONLY`, as verified
by the `test_compose_requires_any_repo_local_bind_read_only` test added in this
revision.

## Files Changed (Commit-Local Delta)

```
 scripts/check_environment_isolation.py         | ~10 lines
 tests/scripts/test_check_environment_isolation.py | +27 lines (2 new tests)
```

No other files modified. The baseline implementation from `-003` (the checker skeleton,
`.dockerignore` hardening, release-gate wiring, original 30-test module) remains in
place and unchanged; this revision only corrects the compose rule scope and adds the
regression coverage called out in `-004`.

## Required Action Items From -004

1. **Generalize the read-only compose rule to all repo-local host binds by default** —
   DONE via the `_SOURCE_BIND_PREFIXES` removal. No writable allowlist was introduced
   (matches the simpler option from the `-004` recommended action).
2. **Add regression coverage showing a writable repo-local bind outside the current
   prefix list fails the checker** — DONE via
   `test_compose_requires_any_repo_local_bind_read_only`.
3. **Re-run the live checker and focused pytest suite and submit a revised
   post-implementation report** — DONE (this file).

## Non-Scope Confirmation

- No other files in the Phase 3 baseline scope were modified.
- The `.dockerignore` hardening from `-003` remains unchanged.
- The release-gate wiring from `-003` remains unchanged (the new checker invocation
  between `check_codex_hook_parity.py` and the pytest lane still runs; no ordering
  change).
- No `.devcontainer` / Codespaces changes, no workflow-file edits, no startup/hook
  guardrails, no service-boundary logic, no overlay mechanics.

## Requested Verdict

VERIFIED.

## Prior Deliberations (per deliberation-protocol.md)

- `DELIB-0877` — GTKB application-isolation planning context (carried forward from
  `-001` / `-003`).
- NO-GO at `-004` is the direct prior for this revision.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
