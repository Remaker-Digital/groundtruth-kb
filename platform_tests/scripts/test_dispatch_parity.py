# (c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
"""Tests for the WI-4848 slice-1 shadow-decision parity harness.

The pure ``compare_decisions`` core is unit-tested directly (match, multi-role,
divergence detection). ``compute_parity`` is exercised against a synthetic project
to confirm it runs read-only (no spawn) end-to-end. The live parity number is
produced by the module's real-state smoke run, not asserted here.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_OPS_DIR = _REPO_ROOT / "scripts" / "ops"
if str(_OPS_DIR) not in sys.path:
    sys.path.insert(0, str(_OPS_DIR))

import dispatch_parity as dp  # noqa: E402


def _dec(role: str, recipient: str, signature: str, selected: list[str]) -> dict:
    return {
        "role": role,
        "recipient": recipient,
        "harness_id": "X",
        "signature": signature,
        "selected": list(selected),
    }


def _make_project(root: Path) -> Path:
    (root / "groundtruth.toml").write_text(
        '[project]\nproject_name = "TestSynthetic"\nprofile = "dual-agent"\n', encoding="utf-8"
    )
    (root / "bridge").mkdir(exist_ok=True)
    hs = root / "harness-state"
    hs.mkdir(exist_ok=True)
    (hs / "harness-identities.json").write_text(
        json.dumps({"schema_version": 1, "harnesses": {"claude": {"id": "B"}, "codex": {"id": "A"}}}),
        encoding="utf-8",
    )
    (hs / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": [
                    {
                        "id": "A",
                        "harness_name": "codex",
                        "harness_type": "codex",
                        "status": "active",
                        "role": ["loyal-opposition"],
                    },
                    {
                        "id": "B",
                        "harness_name": "claude",
                        "harness_type": "claude",
                        "status": "active",
                        "role": ["prime-builder"],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    return root


def _write_bridge(root: Path, stem: str, status: str, version: int) -> None:
    body = f"{status}\n\n# {stem} v{version}\nauthor_session_context_id: fixture-author-session\n"
    (root / "bridge" / f"{stem}-{version:03d}.md").write_text(body, encoding="utf-8")


# --- pure comparison core -------------------------------------------------


def test_parity_single_target_matches() -> None:
    decisions = [_dec("loyal-opposition", "lo:F", "sigA", ["doc-001"])]
    report = dp.compare_decisions(decisions, list(decisions))
    assert report.overall_match is True
    assert report.per_role["loyal-opposition"]["match"] is True
    assert not report.per_role["loyal-opposition"]["divergences"]


def test_parity_multi_role() -> None:
    trig = [
        _dec("prime-builder", "pb:B", "sP", ["p-001"]),
        _dec("loyal-opposition", "lo:F", "sL", ["l-001"]),
    ]
    report = dp.compare_decisions(trig, list(trig))
    assert report.overall_match is True
    assert set(report.roles_compared) == {"prime-builder", "loyal-opposition"}


def test_parity_reports_divergence() -> None:
    # The multi-target divergence class: trigger shrinks remaining_items so the
    # second target sees only doc-002; the daemon feeds the full items so it
    # re-selects doc-001+doc-002 with a different signature.
    trig = [
        _dec("loyal-opposition", "lo:F", "sigA", ["doc-001"]),
        _dec("loyal-opposition", "lo:G", "sigB", ["doc-002"]),
    ]
    daemon = [
        _dec("loyal-opposition", "lo:F", "sigA", ["doc-001"]),
        _dec("loyal-opposition", "lo:G", "sigX", ["doc-001", "doc-002"]),
    ]
    report = dp.compare_decisions(trig, daemon)
    assert report.overall_match is False
    divergences = report.per_role["loyal-opposition"]["divergences"]
    assert divergences and any(item["index"] == 1 for item in divergences)


# --- read-only integration ------------------------------------------------


def test_parity_is_read_only(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _make_project(tmp_path)
    _write_bridge(root, "pb-go-thread", "GO", 2)
    monkeypatch.setenv("GTKB_HARNESS_REGISTRY_PATH", str(root / "harness-state" / "harness-registry.json"))

    def _no_spawn(*_args, **_kwargs):
        raise AssertionError("compute_parity must not spawn a subprocess")

    monkeypatch.setattr(subprocess, "Popen", _no_spawn)
    report = dp.compute_parity(root)
    assert isinstance(report.overall_match, bool)
    # synthetic single-thread state never diverges (single-target or no-target)
    assert report.overall_match is True
