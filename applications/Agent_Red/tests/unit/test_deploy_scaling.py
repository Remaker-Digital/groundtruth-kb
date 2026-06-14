"""Tests for scripts/deploy.py scaling enforcement (WI-3171).

WI-3171 extends scripts/deploy.py scaling enforcement from the single API
gateway (WI-3156) to every container app deploy.py manages. These tests
verify the contract Codex approved in bridge/deploy-scaling-full-coverage-002.md:

  T1. SCALING_CONFIG values align with Terraform main.tf for every
      deploy-managed container app (NOT every "critical" TF app, because NATS
      is critical-in-Terraform but Terraform-managed outside deploy.py).
  T2. Every app deploy.py deploys (gateways + agents + infra) has a SCALING_CONFIG
      entry, so future deploy.py additions can't silently skip scaling.
  T3. _enforce_one builds a correctly formatted `az containerapp update` command.
  T4. _enforce_one handles az failures gracefully (returns False, warns, never raises).
  T5. enforce_all_scaling('production') targets the production gateway + all
      shared agents + SLIM, and skips the staging gateway.
  T6. enforce_all_scaling('staging') targets the staging gateway + all shared
      agents + SLIM (agents are the same Azure apps in both envs per ADR-002).
  T7. Partial scaling failure does not abort the loop — every target is attempted.
  T8. The back-compat enforce_scaling(app_name, environment) shim still works
      for any unmigrated callers.

Test harness note: scripts/deploy.py is not a package. It is loaded via
importlib.util.spec_from_file_location (same pattern as
test_deploy_pipeline_production.py) so these tests do not depend on
scripts/ being on sys.path.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEPLOY_SCRIPT = PROJECT_ROOT / "scripts" / "deploy.py"
if not DEPLOY_SCRIPT.exists():
    DEPLOY_SCRIPT = PROJECT_ROOT.parent.parent / "scripts" / "deploy.py"

TERRAFORM_MAIN = PROJECT_ROOT / "infrastructure" / "terraform" / "main.tf"
if not TERRAFORM_MAIN.exists():
    TERRAFORM_MAIN = PROJECT_ROOT.parent.parent / "infrastructure" / "terraform" / "main.tf"


# Mapping from Terraform container_apps key -> deploy.py Azure Container App name.
# Every entry in this table is a deploy-managed Terraform container app. Any TF
# container app that is NOT in this table (currently only `nats`) is out of scope
# for deploy.py scaling enforcement per WI-3171.
TF_TO_AZURE_NAME: dict[str, str] = {
    "api-gateway": "agent-red-api-gateway",
    "intent-classifier": "agent-red-intent-classifier",
    "knowledge-retrieval": "agent-red-knowledge-retrieval",
    "response-generator": "agent-red-response-generator",
    "critic-supervisor": "agent-red-critic-supervisor",
    "escalation": "agent-red-escalation-handler",
    "analytics": "agent-red-analytics-collector",
    "slim-gateway": "agent-red-slim",
    # "nats" intentionally omitted — TF-managed, not deploy.py-managed.
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_deploy_module():
    """Import scripts/deploy.py as a fresh module for each test.

    Fresh import per call so patches on the module namespace don't leak
    between tests.
    """
    spec = importlib.util.spec_from_file_location("deploy_under_test", DEPLOY_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    # Make argparse, logging, etc. resolvable when the module executes top-level code.
    sys.modules["deploy_under_test"] = mod
    try:
        spec.loader.exec_module(mod)
    finally:
        # Don't leave the stub in sys.modules; each test wants a fresh copy.
        sys.modules.pop("deploy_under_test", None)
    return mod


def _parse_terraform_scaling() -> dict[str, dict[str, int | bool]]:
    """Parse infrastructure/terraform/main.tf for container_apps scaling values.

    Returns a dict keyed by the TF container name (e.g. 'api-gateway') with
    the parsed min_replicas, max_replicas, and critical flag. Used as a
    lightweight source-of-truth check for T1 without pulling in an HCL parser.
    """
    text = TERRAFORM_MAIN.read_text(encoding="utf-8")

    # Grab the container_apps = { ... } block. Matches greedily up to the next
    # top-level "  }" line that closes the locals block. Terraform indentation
    # is stable in this repo (2 spaces for locals, 4 for inner blocks), so the
    # start marker is unambiguous.
    block_match = re.search(
        r"container_apps\s*=\s*\{(.*?)\n  \}\s*\n\n",
        text,
        re.DOTALL,
    )
    if not block_match:
        raise AssertionError("Could not locate container_apps block in main.tf; test needs update.")
    block = block_match.group(1)

    # Each entry looks like:
    #     api-gateway = {
    #       image        = "..."
    #       ...
    #       min_replicas = 2
    #       max_replicas = 8
    #       critical     = true
    #       ...
    #     }
    entry_pattern = re.compile(
        r"(?P<name>[a-z][a-z0-9\-]*)\s*=\s*\{"  # name = {
        r"(?P<body>[^}]*?)"  # body (non-greedy, no nested braces)
        r"\}",
        re.DOTALL,
    )

    parsed: dict[str, dict[str, int | bool]] = {}
    for m in entry_pattern.finditer(block):
        name = m.group("name")
        body = m.group("body")
        min_match = re.search(r"min_replicas\s*=\s*(\d+)", body)
        max_match = re.search(r"max_replicas\s*=\s*(\d+)", body)
        crit_match = re.search(r"critical\s*=\s*(true|false)", body)
        if not (min_match and max_match and crit_match):
            continue
        parsed[name] = {
            "min_replicas": int(min_match.group(1)),
            "max_replicas": int(max_match.group(1)),
            "critical": crit_match.group(1) == "true",
        }
    return parsed


# ---------------------------------------------------------------------------
# T1: SCALING_CONFIG values align with Terraform for deploy-managed apps
# ---------------------------------------------------------------------------


class TestScalingConfigTerraformReconciliation:
    """T1: Every deploy-managed TF container has matching SCALING_CONFIG values."""

    def test_scaling_config_matches_terraform_for_deploy_managed_apps(self) -> None:
        mod = _load_deploy_module()
        tf = _parse_terraform_scaling()

        # Sanity: we actually parsed something.
        assert len(tf) >= 9, f"expected >= 9 TF entries, got {len(tf)}: {sorted(tf)}"

        # Every TF entry that maps into the deploy-managed set must exist in SCALING_CONFIG
        # with identical min/max values. NATS is intentionally excluded.
        for tf_key, azure_name in TF_TO_AZURE_NAME.items():
            assert tf_key in tf, f"TF container {tf_key!r} missing from main.tf — update TF_TO_AZURE_NAME or main.tf"
            tf_cfg = tf[tf_key]
            cfg = mod.SCALING_CONFIG.get(azure_name)
            assert cfg is not None, f"SCALING_CONFIG missing entry for {azure_name!r} (corresponds to TF {tf_key!r})"
            assert cfg["min_replicas"] == tf_cfg["min_replicas"], (
                f"{azure_name}: min_replicas {cfg['min_replicas']} != "
                f"Terraform {tf_cfg['min_replicas']} (TF key {tf_key!r})"
            )
            assert cfg["max_replicas"] == tf_cfg["max_replicas"], (
                f"{azure_name}: max_replicas {cfg['max_replicas']} != "
                f"Terraform {tf_cfg['max_replicas']} (TF key {tf_key!r})"
            )

    def test_nats_excluded_from_scaling_config(self) -> None:
        """NATS is TF-managed; deploy.py must not attempt to enforce its scaling."""
        mod = _load_deploy_module()
        # Any key containing 'nats' (case-insensitive) is a violation.
        nats_keys = [k for k in mod.SCALING_CONFIG if "nats" in k.lower()]
        assert nats_keys == [], f"NATS must be excluded from SCALING_CONFIG (TF-managed); found: {nats_keys}"


# ---------------------------------------------------------------------------
# T2: Every deploy.py-deployed app has a SCALING_CONFIG entry
# ---------------------------------------------------------------------------


class TestScalingConfigCoversDeployedApps:
    """T2: Union of deployed apps is a subset of SCALING_CONFIG keys."""

    def test_scaling_config_covers_all_deployed_apps(self) -> None:
        mod = _load_deploy_module()
        deployed_apps: set[str] = set()
        deployed_apps.update(mod.CONTAINER_APPS.values())  # both gateways
        deployed_apps.update(mod.AGENT_CONTAINER_APPS.values())  # 6 agents
        deployed_apps.update(mod.INFRA_CONTAINER_APPS.values())  # slim

        missing = deployed_apps - set(mod.SCALING_CONFIG.keys())
        assert missing == set(), (
            f"Deployed apps without SCALING_CONFIG entries: {sorted(missing)}. "
            f"Add a scaling entry or explicitly exclude with a comment."
        )

    def test_both_gateway_names_in_scaling_config(self) -> None:
        """Both env-specific gateway names must appear in SCALING_CONFIG."""
        mod = _load_deploy_module()
        assert "agent-red-api-gateway" in mod.SCALING_CONFIG
        assert "agent-red-staging" in mod.SCALING_CONFIG


# ---------------------------------------------------------------------------
# T3 + T4: _enforce_one behavior
# ---------------------------------------------------------------------------


class TestEnforceOne:
    """T3: correct az command. T4: failure handling."""

    def test_enforce_one_constructs_correct_az_command(self) -> None:
        mod = _load_deploy_module()
        captured_commands: list[str] = []

        def fake_run(cmd: str, timeout: int = 120) -> tuple[int, str]:
            captured_commands.append(cmd)
            return 0, ""

        with patch.object(mod, "_run", side_effect=fake_run):
            ok = mod._enforce_one("agent-red-api-gateway", 2, 8)

        assert ok is True
        assert len(captured_commands) == 1
        cmd = captured_commands[0]
        assert "az containerapp update" in cmd
        assert "--name agent-red-api-gateway" in cmd
        assert f"--resource-group {mod.RESOURCE_GROUP}" in cmd
        assert "--min-replicas 2" in cmd
        assert "--max-replicas 8" in cmd
        assert "--output none" in cmd

    def test_enforce_one_handles_az_failure(self) -> None:
        mod = _load_deploy_module()

        with patch.object(mod, "_run", return_value=(1, "simulated az error")):
            ok = mod._enforce_one("agent-red-api-gateway", 2, 8)

        assert ok is False, "_enforce_one must return False when _run reports failure"


# ---------------------------------------------------------------------------
# T5 + T6 + T7: enforce_all_scaling iteration and env selection
# ---------------------------------------------------------------------------


class TestEnforceAllScaling:
    """T5: production coverage. T6: staging gateway selection. T7: partial failures."""

    def test_enforce_all_scaling_production_covers_all_prod_apps(self) -> None:
        mod = _load_deploy_module()
        calls: list[tuple[str, int, int]] = []

        def fake_run(cmd: str, timeout: int = 120) -> tuple[int, str]:
            name = re.search(r"--name (\S+)", cmd).group(1)
            min_r = int(re.search(r"--min-replicas (\d+)", cmd).group(1))
            max_r = int(re.search(r"--max-replicas (\d+)", cmd).group(1))
            calls.append((name, min_r, max_r))
            return 0, ""

        with patch.object(mod, "_run", side_effect=fake_run):
            results = mod.enforce_all_scaling("production")

        called_names = {c[0] for c in calls}
        # Production gateway, not staging gateway.
        assert "agent-red-api-gateway" in called_names
        assert "agent-red-staging" not in called_names
        # All 6 shared agent containers.
        for agent in mod.AGENT_CONTAINER_APPS.values():
            assert agent in called_names, f"{agent} was not scaled in production"
        # SLIM infra container.
        for infra in mod.INFRA_CONTAINER_APPS.values():
            assert infra in called_names, f"{infra} was not scaled in production"

        # Total target count: 1 gateway + 6 agents + 1 slim = 8.
        assert len(calls) == 8, f"expected 8 calls, got {len(calls)}: {calls}"
        # Every call succeeded.
        assert all(results.values()), f"expected all True, got {results}"

        # Production gateway values must match Terraform.
        gw_call = next(c for c in calls if c[0] == "agent-red-api-gateway")
        assert gw_call[1:] == (2, 8), f"production gateway scaled to {gw_call[1:]}, expected (2, 8) per Terraform"

    def test_enforce_all_scaling_staging_uses_staging_gateway(self) -> None:
        mod = _load_deploy_module()
        calls: list[tuple[str, int, int]] = []

        def fake_run(cmd: str, timeout: int = 120) -> tuple[int, str]:
            name = re.search(r"--name (\S+)", cmd).group(1)
            min_r = int(re.search(r"--min-replicas (\d+)", cmd).group(1))
            max_r = int(re.search(r"--max-replicas (\d+)", cmd).group(1))
            calls.append((name, min_r, max_r))
            return 0, ""

        with patch.object(mod, "_run", side_effect=fake_run):
            mod.enforce_all_scaling("staging")

        called_names = {c[0] for c in calls}
        # Staging gateway, not production gateway.
        assert "agent-red-staging" in called_names
        assert "agent-red-api-gateway" not in called_names
        # All 6 agents + slim still covered (shared apps).
        assert len(calls) == 8, f"expected 8 calls, got {len(calls)}: {calls}"

        # Staging gateway preserves the WI-3156 baseline (min=1, max=5) that
        # Codex explicitly instructed us not to change in GO condition 4.
        staging_call = next(c for c in calls if c[0] == "agent-red-staging")
        assert staging_call[1:] == (1, 5), (
            f"staging gateway scaled to {staging_call[1:]}, expected (1, 5) — "
            f"WI-3156 baseline preserved per Codex GO condition 4"
        )

    def test_enforce_all_scaling_partial_failure_continues(self) -> None:
        """Scaling failures must not abort the loop — mirrors WI-3156 behavior."""
        mod = _load_deploy_module()
        call_count = {"n": 0}

        def flaky_run(cmd: str, timeout: int = 120) -> tuple[int, str]:
            call_count["n"] += 1
            # First call fails, all subsequent calls succeed.
            if call_count["n"] == 1:
                return 1, "first call deliberately fails"
            return 0, ""

        with patch.object(mod, "_run", side_effect=flaky_run):
            results = mod.enforce_all_scaling("production")

        # Loop completed — all 8 targets attempted.
        assert call_count["n"] == 8, f"expected 8 attempts despite failure, got {call_count['n']}"
        # Exactly one entry in the result dict is False.
        failed = [name for name, ok in results.items() if not ok]
        succeeded = [name for name, ok in results.items() if ok]
        assert len(failed) == 1, f"expected 1 failure, got {failed}"
        assert len(succeeded) == 7, f"expected 7 successes, got {succeeded}"


# ---------------------------------------------------------------------------
# T8: Back-compat shim
# ---------------------------------------------------------------------------


class TestEnforceScalingBackCompat:
    """T8: the legacy enforce_scaling(app_name, environment) signature still works."""

    def test_enforce_scaling_backcompat_production_gateway(self) -> None:
        mod = _load_deploy_module()
        captured: list[str] = []

        def fake_run(cmd: str, timeout: int = 120) -> tuple[int, str]:
            captured.append(cmd)
            return 0, ""

        with patch.object(mod, "_run", side_effect=fake_run):
            ok = mod.enforce_scaling("agent-red-api-gateway", "production")

        assert ok is True
        assert len(captured) == 1
        # Uses the SCALING_CONFIG lookup, so the Terraform-aligned 2/8 must land.
        assert "--min-replicas 2" in captured[0]
        assert "--max-replicas 8" in captured[0]
        assert "--name agent-red-api-gateway" in captured[0]

    def test_enforce_scaling_backcompat_unknown_app_no_op(self) -> None:
        """Unknown app names return True without invoking az (matches old behavior)."""
        mod = _load_deploy_module()

        with patch.object(mod, "_run") as mock_run:
            ok = mod.enforce_scaling("agent-red-unknown-app", "production")

        assert ok is True
        mock_run.assert_not_called()
