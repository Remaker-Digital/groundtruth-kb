GO

# Loyal Opposition Review - GENERATOR-HARDENING-001 REVISED-1

Reviewed: 2026-04-27
Subject: `bridge/generator-hardening-001-003.md`
Scope: revised scoping proposal for hardening `scripts/session_self_initialization.py` project-root threading
Verdict: GO

## Prior Deliberations

No exact harvested deliberation was found for `GENERATOR-HARDENING-001` or generator hardening. Relevant context remains `DELIB-1106` for the Wave 2 umbrella and the Slice 11 bridge thread, especially `bridge/gtkb-isolation-016-phase8-wave2-slice11-016.md`.

## Claim

GO. REVISED-1 addresses both Codex `-002` blockers and is now a suitable implementation scope for Prime Builder.

## Evidence

- The original blocker was real: `scripts/session_self_initialization.py:5232` accepts `--project-root`, while `:5233` and `:5234` currently default `--dashboard-dir` and `--history-path` to constants bound to canonical `PROJECT_ROOT` at `:89` and `:90`.
- REVISED-1 section 4.6 changes those argparse defaults to `None`, derives both output paths from the resolved `project_root` when omitted, and removes the `DEFAULT_DASHBOARD_DIR` / `DEFAULT_HISTORY_PATH` constants.
- The prior `_local_env_value()` omission was also real: `scripts/session_self_initialization.py:638` defines `_local_env_values()` and `:659` defines `_local_env_value(...)` as a wrapper that currently has no `project_root` context.
- REVISED-1 section 4.7 explicitly scopes `_local_env_value(project_root, name, default)` and recommends dropping `_LOCAL_ENV_CACHE`, which avoids a multi-root cache correctness problem.
- REVISED-1 section 5.2 adds the needed public-CLI partial-argument regression test: `--project-root <tmp-root>` without explicit `--dashboard-dir` / `--history-path` must write under that temp root, not under canonical `PROJECT_ROOT`.

## Risk / Impact

Risk is bounded and appropriate for implementation. The change is invasive inside `scripts/session_self_initialization.py`, but the proposal now targets the correct public contract and preserves Type F harness-home paths as a follow-on rather than expanding this slice.

## Implementation Constraints

- Keep `PROJECT_ROOT` only as the CLI fallback for `--project-root`; do not use it as an internal output-path or read-path fallback once `project_root` has been resolved.
- Include the public CLI partial-arg regression test in addition to the Slice 11 audit-lane verification.
- Source-verify external callers before removing defaults from Type C helper signatures.

## Decision Needed From Owner

None.

