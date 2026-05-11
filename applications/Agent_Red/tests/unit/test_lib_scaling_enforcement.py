"""Unit tests for scripts/lib/scaling_enforcement.py.

These tests exercise the shared scaling enforcement helpers in isolation,
without loading scripts/deploy.py or scripts/deploy_pipeline.py. They
prove that:

- T1: _enforce_one builds the correct `az containerapp update` command.
- T2: _enforce_one returns False on runner failure, never raises.
- T3: enforce_all_scaling calls _enforce_one once per target.
- T4: enforce_all_scaling skips targets missing from scaling_config
      (logs SKIP, marks True — matches WI-3156 behavior).
- T5: enforce_all_scaling continues the loop on per-app failure
      (one failed target does not prevent later targets from being attempted).
- T6: get_scaling_targets returns the expected name lists for both
      production and staging environments (gateway + agents + infra).

Created 2026-04-25 (S308) per
`bridge/canonical-deploy-pipeline-scaling-enforcement-007.md` (Codex GO at -008).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Bootstrap: make `scripts/` importable so `from lib.X import Y` works.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.scaling_enforcement import _enforce_one, enforce_all_scaling  # noqa: E402
from lib.scaling_targets import (  # noqa: E402
    SCALING_CONFIG,
    get_scaling_targets,
)


# Test fixture: a runner that records every command it receives plus a
# canned response. Default response is success (returncode 0).
class RecordingRunner:
    def __init__(self, responses: dict[str, tuple[int, str]] | None = None,
                 default: tuple[int, str] = (0, "")) -> None:
        self.calls: list[tuple[str, int]] = []
        self.responses = responses or {}
        self.default = default

    def __call__(self, cmd: str, timeout: int) -> tuple[int, str]:
        self.calls.append((cmd, timeout))
        for marker, response in self.responses.items():
            if marker in cmd:
                return response
        return self.default


# Test fixture: a logger that records every message.
class RecordingLogger:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def __call__(self, msg: str) -> None:
        self.messages.append(msg)


# T1 — _enforce_one builds the correct az command
def test_enforce_one_builds_correct_az_command() -> None:
    runner = RecordingRunner()
    logger = RecordingLogger()

    ok = _enforce_one(
        app_name="agent-red-api-gateway",
        min_r=2,
        max_r=8,
        resource_group="Agent-Red",
        runner=runner,
        log=logger,
    )

    assert ok is True
    assert len(runner.calls) == 1
    cmd, timeout = runner.calls[0]
    assert "az containerapp update" in cmd
    assert "--name agent-red-api-gateway" in cmd
    assert "--resource-group Agent-Red" in cmd
    assert "--min-replicas 2" in cmd
    assert "--max-replicas 8" in cmd
    assert "--output none" in cmd
    assert timeout == 120


# T2 — _enforce_one returns False on runner failure, never raises
def test_enforce_one_returns_false_on_runner_failure() -> None:
    runner = RecordingRunner(default=(1, "simulated az error"))
    logger = RecordingLogger()

    ok = _enforce_one(
        app_name="agent-red-staging",
        min_r=1,
        max_r=5,
        resource_group="Agent-Red",
        runner=runner,
        log=logger,
    )

    assert ok is False
    # Logger should record the failure
    assert any("WARNING" in m and "agent-red-staging" in m for m in logger.messages)


# T3 — enforce_all_scaling calls _enforce_one once per target
def test_enforce_all_scaling_calls_runner_once_per_target() -> None:
    runner = RecordingRunner()
    logger = RecordingLogger()
    targets = ["agent-red-api-gateway", "agent-red-intent-classifier"]

    results = enforce_all_scaling(
        targets=targets,
        scaling_config=SCALING_CONFIG,
        resource_group="Agent-Red",
        runner=runner,
        log=logger,
    )

    assert results == {
        "agent-red-api-gateway": True,
        "agent-red-intent-classifier": True,
    }
    assert len(runner.calls) == 2
    assert any("agent-red-api-gateway" in cmd for cmd, _ in runner.calls)
    assert any("agent-red-intent-classifier" in cmd for cmd, _ in runner.calls)


# T4 — enforce_all_scaling skips targets missing from scaling_config
def test_enforce_all_scaling_skips_unknown_targets() -> None:
    runner = RecordingRunner()
    logger = RecordingLogger()
    targets = ["agent-red-api-gateway", "unknown-app-xyz"]

    results = enforce_all_scaling(
        targets=targets,
        scaling_config=SCALING_CONFIG,
        resource_group="Agent-Red",
        runner=runner,
        log=logger,
    )

    # Skipped targets are marked True (matches WI-3156 missing-env behavior)
    assert results["unknown-app-xyz"] is True
    assert results["agent-red-api-gateway"] is True
    # Runner was called only for the known target
    assert len(runner.calls) == 1
    assert "agent-red-api-gateway" in runner.calls[0][0]
    # Logger records the SKIP
    assert any("SKIP" in m and "unknown-app-xyz" in m for m in logger.messages)


# T5 — partial failure does not abort the loop
def test_enforce_all_scaling_continues_on_partial_failure() -> None:
    # Make the gateway fail; the agent should still be attempted afterward.
    runner = RecordingRunner(responses={"agent-red-api-gateway": (1, "fail")})
    logger = RecordingLogger()
    targets = [
        "agent-red-api-gateway",          # will fail
        "agent-red-intent-classifier",    # should still be attempted
        "agent-red-knowledge-retrieval",  # should still be attempted
    ]

    results = enforce_all_scaling(
        targets=targets,
        scaling_config=SCALING_CONFIG,
        resource_group="Agent-Red",
        runner=runner,
        log=logger,
    )

    assert results["agent-red-api-gateway"] is False
    assert results["agent-red-intent-classifier"] is True
    assert results["agent-red-knowledge-retrieval"] is True
    # All three targets were attempted (failure didn't short-circuit)
    assert len(runner.calls) == 3


# T6 — get_scaling_targets returns expected lists per environment
@pytest.mark.parametrize(
    "environment,expected_first",
    [
        ("production", "agent-red-api-gateway"),
        ("staging", "agent-red-staging"),
    ],
)
def test_get_scaling_targets_environment_specific_gateway(
    environment: str, expected_first: str
) -> None:
    targets = get_scaling_targets(environment)
    assert targets[0] == expected_first, (
        f"First target for {environment} must be {expected_first}, got {targets[0]}"
    )
    # Both environments include the same shared agent containers
    assert "agent-red-intent-classifier" in targets
    assert "agent-red-knowledge-retrieval" in targets
    assert "agent-red-response-generator" in targets
    assert "agent-red-critic-supervisor" in targets
    assert "agent-red-escalation-handler" in targets
    assert "agent-red-analytics-collector" in targets
    # Both include shared infra
    assert "agent-red-slim" in targets
    # NATS and test-host explicitly excluded
    assert not any("nats" in name.lower() for name in targets)
    assert not any("test-host" in name.lower() for name in targets)
