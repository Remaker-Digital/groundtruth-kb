"""FAB-21 / WI-4360 (HYG-025): tests for the always-loaded .claude/rules/*.md payload profiler.

The profiler reports the exact byte total and an estimated token total of the
auto-loaded ``.claude/rules/*.md`` payload against ``STARTUP_PRUNING_TOTAL_WARN_BYTES``
so the startup-budget overage is visible and trackable. These tests verify the
byte/token math, the budget logic, edge cases, and the scan/render integration.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "session_self_initialization.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("session_self_initialization", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["session_self_initialization"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def ssi():
    return _load_module()


def _write_rule(rules_dir: Path, name: str, size: int) -> None:
    rules_dir.mkdir(parents=True, exist_ok=True)
    (rules_dir / name).write_text("x" * size, encoding="utf-8")


def test_profile_sums_bytes_and_estimates_tokens(ssi, tmp_path):
    rules_dir = tmp_path / ".claude" / "rules"
    _write_rule(rules_dir, "a.md", 1000)
    _write_rule(rules_dir, "b.md", 2000)
    _write_rule(rules_dir, "c.md", 3000)
    _write_rule(rules_dir, "ignore.txt", 9999)  # non-.md must be excluded

    result = ssi._rules_payload_profile(tmp_path)

    assert result["scope"] == "claude_rules_md_payload"
    assert result["glob"] == ".claude/rules/*.md"
    assert result["file_count"] == 3
    assert result["total_bytes"] == 6000
    assert result["bytes_per_token_estimate"] == ssi.RULES_PAYLOAD_BYTES_PER_TOKEN
    assert result["estimated_tokens"] == 6000 // ssi.RULES_PAYLOAD_BYTES_PER_TOKEN


def test_profile_under_budget(ssi, tmp_path):
    rules_dir = tmp_path / ".claude" / "rules"
    _write_rule(rules_dir, "a.md", 100)

    result = ssi._rules_payload_profile(tmp_path)

    assert result["over_budget"] is False
    assert result["overage_bytes"] == 0
    assert result["overage_pct"] == 0.0
    assert result["budget_bytes"] == ssi.STARTUP_PRUNING_TOTAL_WARN_BYTES


def test_profile_over_budget(ssi, tmp_path):
    rules_dir = tmp_path / ".claude" / "rules"
    over = ssi.STARTUP_PRUNING_TOTAL_WARN_BYTES + 10_000
    _write_rule(rules_dir, "big.md", over)

    result = ssi._rules_payload_profile(tmp_path)

    assert result["over_budget"] is True
    assert result["total_bytes"] == over
    assert result["overage_bytes"] == over - ssi.STARTUP_PRUNING_TOTAL_WARN_BYTES
    assert result["overage_pct"] > 0


def test_profile_empty_rules_dir(ssi, tmp_path):
    # No .claude/rules directory at all: fail-soft to a zeroed profile.
    result = ssi._rules_payload_profile(tmp_path)

    assert result["file_count"] == 0
    assert result["total_bytes"] == 0
    assert result["estimated_tokens"] == 0
    assert result["over_budget"] is False
    assert result["overage_pct"] == 0.0
    assert result["largest_files"] == []


def test_profile_largest_files_sorted_and_capped(ssi, tmp_path):
    rules_dir = tmp_path / ".claude" / "rules"
    for i in range(10):
        _write_rule(rules_dir, f"r{i:02d}.md", (i + 1) * 100)

    result = ssi._rules_payload_profile(tmp_path)
    largest = result["largest_files"]

    assert len(largest) == 8  # capped at 8 even though 10 rule files exist
    sizes = [int(profile["bytes"]) for profile in largest]
    assert sizes == sorted(sizes, reverse=True)
    assert sizes[0] == 1000  # the largest file (i == 9)


def test_startup_pruning_scan_includes_rules_payload(ssi, tmp_path):
    rules_dir = tmp_path / ".claude" / "rules"
    _write_rule(rules_dir, "a.md", 500)

    scan = ssi._startup_pruning_scan(tmp_path)

    assert "rules_payload" in scan
    assert scan["rules_payload"]["file_count"] == 1
    assert scan["rules_payload"]["total_bytes"] == 500


def test_render_startup_pruning_includes_baseline_line(ssi, tmp_path):
    rules_dir = tmp_path / ".claude" / "rules"
    over = ssi.STARTUP_PRUNING_TOTAL_WARN_BYTES + 5_000
    _write_rule(rules_dir, "big.md", over)

    scan = ssi._startup_pruning_scan(tmp_path)
    rendered = ssi._render_startup_pruning({"startup_pruning": scan})

    assert "Rules payload baseline" in rendered
    assert "OVER budget" in rendered
