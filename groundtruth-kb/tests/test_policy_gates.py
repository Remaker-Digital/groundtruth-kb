"""Tests for deterministic AUQ policy gates."""

from __future__ import annotations

import inspect
import json
import time
from pathlib import Path

import pytest
from click.testing import CliRunner

import groundtruth_kb.policy.engine as policy_engine
from groundtruth_kb.cli import main
from groundtruth_kb.policy.engine import check_policy, load_policy_registry, load_receipt, validate_receipt


def test_policy_registry_parses_candidate_actions() -> None:
    registry = load_policy_registry()

    assert registry.schema_version == 1
    assert registry.registry_hash.startswith("sha256:")
    assert set(registry.actions) >= {
        "status",
        "test",
        "build",
        "deploy-staging",
        "deploy-production",
        "requirements-update",
        "commit",
        "push",
        "platform-write",
    }
    assert registry.actions["commit"].adapter_installed is False
    assert registry.actions["push"].adapter_installed is False
    assert registry.actions["platform-write"].adapter_installed is False


def test_policy_outcomes_cover_allow_warn_ask_and_deny() -> None:
    registry = load_policy_registry()

    allow = check_policy(action="status", scope="platform", registry=registry)
    warn = check_policy(action="test", scope="platform", registry=registry)
    ask = check_policy(action="requirements-update", scope="platform", registry=registry)
    deny = check_policy(action="deploy-production", scope="platform", registry=registry)

    assert allow.outcome == "ALLOW"
    assert warn.outcome == "WARN"
    assert ask.outcome == "ASK"
    assert 2 <= len(ask.ask_options) <= 3
    assert deny.outcome == "DENY"
    assert deny.ask_options == ()


def test_valid_receipt_turns_ask_into_allow() -> None:
    registry = load_policy_registry()
    receipt = {
        "action": "requirements-update",
        "scope": "platform",
        "paths": [],
        "registry_hash": registry.registry_hash,
        "expires_at": time.time() + 60,
    }

    decision = check_policy(action="requirements-update", scope="platform", registry=registry, receipt=receipt)

    assert decision.outcome == "ALLOW"
    assert decision.receipt.valid is True
    assert "valid approval receipt" in decision.reasons


def test_receipt_validation_rejects_mismatches_and_expiry() -> None:
    registry = load_policy_registry()
    base = {
        "action": "requirements-update",
        "scope": "platform",
        "paths": [],
        "registry_hash": registry.registry_hash,
        "expires_at": 200.0,
    }

    assert not validate_receipt(
        {**base, "action": "commit"},
        action="requirements-update",
        scope="platform",
        paths=(),
        registry_hash=registry.registry_hash,
        now=100,
    ).valid
    assert not validate_receipt(
        {**base, "scope": "application"},
        action="requirements-update",
        scope="platform",
        paths=(),
        registry_hash=registry.registry_hash,
        now=100,
    ).valid
    assert not validate_receipt(
        {**base, "paths": ["other"]},
        action="requirements-update",
        scope="platform",
        paths=(),
        registry_hash=registry.registry_hash,
        now=100,
    ).valid
    assert not validate_receipt(
        {**base, "registry_hash": "sha256:bad"},
        action="requirements-update",
        scope="platform",
        paths=(),
        registry_hash=registry.registry_hash,
        now=100,
    ).valid
    assert not validate_receipt(
        {**base, "expires_at": 99.0},
        action="requirements-update",
        scope="platform",
        paths=(),
        registry_hash=registry.registry_hash,
        now=100,
    ).valid


def test_receipt_validation_rejects_non_object_values() -> None:
    validation = validate_receipt(
        [],
        action="requirements-update",
        scope="platform",
        paths=(),
        registry_hash="sha256:x",
        now=100,
    )

    assert validation.valid is False
    assert validation.reason == "receipt must be an object"


def test_load_receipt_rejects_non_object_json(tmp_path: Path, runner: CliRunner) -> None:
    receipt_path = tmp_path / "receipt.json"
    receipt_path.write_text("[]", encoding="utf-8")

    with pytest.raises(ValueError, match="must be an object"):
        load_receipt(receipt_path)

    result = runner.invoke(
        main,
        [
            "policy",
            "check",
            "--action",
            "requirements-update",
            "--scope",
            "platform",
            "--receipt",
            str(receipt_path),
            "--json",
        ],
    )

    assert result.exit_code == 1
    assert "must be an object" in result.output
    assert "AttributeError" not in result.output


def test_application_scope_platform_path_is_denied() -> None:
    registry = load_policy_registry()

    decision = check_policy(
        action="platform-write",
        scope="application",
        paths=(Path(__file__).resolve().parent.parent / "src" / "groundtruth_kb" / "cli.py",),
        registry=registry,
    )

    assert decision.outcome == "DENY"
    assert any("platform path" in reason for reason in decision.reasons)


def test_archive_path_is_denied(tmp_path: Path) -> None:
    registry = load_policy_registry()
    archive_path = tmp_path / "Claude-Playground" / "archived.md"

    decision = check_policy(action="status", scope="platform", paths=(archive_path,), registry=registry)

    assert decision.outcome == "DENY"
    assert "Archive paths" in decision.message


def test_policy_cli_json_exit_behavior(runner: CliRunner) -> None:
    allow = runner.invoke(main, ["policy", "check", "--action", "status", "--scope", "platform", "--json"])
    ask = runner.invoke(
        main,
        ["policy", "check", "--action", "requirements-update", "--scope", "platform", "--json"],
    )
    deny = runner.invoke(main, ["policy", "check", "--action", "deploy-production", "--scope", "platform", "--json"])

    assert allow.exit_code == 0, allow.output
    assert json.loads(allow.output)["outcome"] == "ALLOW"
    assert ask.exit_code == 2, ask.output
    assert json.loads(ask.output)["outcome"] == "ASK"
    assert deny.exit_code == 3, deny.output
    assert json.loads(deny.output)["outcome"] == "DENY"


def test_policy_engine_has_no_llm_or_network_dependency() -> None:
    source = inspect.getsource(policy_engine)

    assert "openai" not in source.lower()
    assert "anthropic" not in source.lower()
    assert "api_key" not in source.lower()
    assert "urllib" not in source.lower()
    assert "requests" not in source.lower()


def test_invalid_registry_outcome_rejected(tmp_path: Path) -> None:
    registry = tmp_path / "bad.toml"
    registry.write_text(
        'schema_version = 1\nregistry_id = "bad"\n[actions.status]\noutcome = "MAYBE"\n',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="invalid outcome"):
        load_policy_registry(registry)
