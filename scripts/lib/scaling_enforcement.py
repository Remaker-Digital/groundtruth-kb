"""Container App scaling enforcement helpers (parameterized).

Pure-library logic for applying min/max replica baselines via the Azure
CLI. Both `scripts/deploy.py` (smoke path) and `scripts/deploy_pipeline.py`
(canonical production path) call into this module so the two paths
produce identical `az containerapp update` invocations against the same
target set.

Created 2026-04-25 (S308) per
`bridge/canonical-deploy-pipeline-scaling-enforcement-007.md` to close
the WI-3031 canonical-path scaling-enforcement gap. Previously this
logic lived only in `scripts/deploy.py` (lines 183-254 pre-S308),
which the documented canonical pipeline never invoked.

The helpers are deliberately parameterized over `runner` and `log` so
the calling script's local subprocess wrapper and logger can be injected.
This avoids re-implementing those primitives here and keeps the module
free of any caller-specific dependencies.

Failure semantics: per the WI-3156 contract, scaling drift on any single
app is a WARNING — `_enforce_one()` returns False and the loop in
`enforce_all_scaling()` continues to the next target. No exception is
raised. Callers are responsible for surfacing the failed-app set to
operators (terminal log lines, summary tables, JSON manifests).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from typing import Callable

# Type alias for the subprocess runner: (command_string, timeout_seconds)
# -> (exit_code, captured_stdout). Matches scripts/deploy.py's _run().
Runner = Callable[[str, int], tuple[int, str]]

# Type alias for the logger callable: log(message_string) -> None.
Logger = Callable[[str], None]


def _enforce_one(
    app_name: str,
    min_r: int,
    max_r: int,
    resource_group: str,
    runner: Runner,
    log: Logger,
) -> bool:
    """Apply min/max replicas to a single Container App via `az` CLI.

    Returns True on success, False on az CLI failure. Failures are logged
    via the injected logger and do not raise — matches the WI-3156 contract
    that scaling drift is a WARNING, not a fatal error.
    """
    cmd = (
        f"az containerapp update "
        f"--name {app_name} "
        f"--resource-group {resource_group} "
        f"--min-replicas {min_r} "
        f"--max-replicas {max_r} "
        f"--output none"
    )
    log(f"Enforcing scaling: min={min_r} max={max_r} on {app_name}...")
    code, output = runner(cmd, 120)
    if code != 0:
        log(f"WARNING: Scaling enforcement failed for {app_name}: {output}")
        return False
    log(f"Scaling enforced on {app_name}.")
    return True


def enforce_all_scaling(
    targets: list[str],
    scaling_config: dict[str, dict[str, int]],
    resource_group: str,
    runner: Runner,
    log: Logger,
) -> dict[str, bool]:
    """Enforce scaling on every container app in `targets`.

    Looks up each app in `scaling_config`. Apps without a config entry
    are skipped (logged, marked True — matches the WI-3156 missing-env
    behavior preserved by `scripts/deploy.py`).

    Returns a dict mapping app_name → bool (True on success or skip).
    Per-app failures are non-fatal; the loop continues so partial
    enforcement is observable to the caller.
    """
    results: dict[str, bool] = {}
    for app_name in targets:
        cfg = scaling_config.get(app_name)
        if cfg is None:
            log(f"SKIP scaling: no SCALING_CONFIG entry for {app_name}")
            results[app_name] = True
            continue
        results[app_name] = _enforce_one(
            app_name,
            cfg["min_replicas"],
            cfg["max_replicas"],
            resource_group,
            runner,
            log,
        )
    return results
