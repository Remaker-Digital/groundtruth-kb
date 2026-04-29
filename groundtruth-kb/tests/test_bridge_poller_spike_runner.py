# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for scripts/bridge_poller_verification_spike.py.

Per ``bridge/gtkb-bridge-poller-p2-5-verification-spike-003.md`` section 3 and
``bridge/gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28-003.md``
sections 1.1.2 and 1.2.4, these tests cover:

- Disposable-repo setup creates the expected in-root layout.
- Sentinel strings + minimized governance hooks are seeded.
- Out-of-root workspace override is rejected (StateDirOutOfRootError).
- Default mocked-subprocess mode produces a complete spike-report.md.
- Mocked default does not invoke real CLIs under any path.
- ``--run-live-harnesses`` requires ``--owner-approval-file`` (subprocess test).
- Approval schema is validated before any live subprocess invocation:
  parse failure, missing fields, low token-cost ack, run-id constraint
  mismatch, out-of-root approval path.
- Findings derivation distinguishes sentinel vs. governance-hook firing.
- Findings classify WRITE_CAPABLE / REVIEW_ONLY / OUT_OF_SCOPE.
- spike-report.md includes all required sections.

Bridge imports are lazy per tests/test_bridge_import_hygiene rule.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

_SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "bridge_poller_verification_spike.py"


def _load_spike_module() -> ModuleType:
    """Load scripts/bridge_poller_verification_spike.py as a module.

    Lazy import per test_bridge_import_hygiene rule (the script imports from
    groundtruth_kb.bridge.paths, which is a bridge import). The module must
    be registered in sys.modules before exec_module so that Python 3.14's
    dataclass internals can resolve cls.__module__ for string annotations.
    """
    assert _SCRIPT_PATH.is_file(), f"Expected runner at {_SCRIPT_PATH}"
    module_name = "bridge_poller_verification_spike"
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, _SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _paths() -> SimpleNamespace:
    from groundtruth_kb.bridge.paths import (
        GROUNDTRUTH_MARKER,
        PROJECT_ROOT_ENV_VAR,
        StateDirOutOfRootError,
    )

    return SimpleNamespace(
        GROUNDTRUTH_MARKER=GROUNDTRUTH_MARKER,
        PROJECT_ROOT_ENV_VAR=PROJECT_ROOT_ENV_VAR,
        StateDirOutOfRootError=StateDirOutOfRootError,
    )


@pytest.fixture
def synthetic_gtkb_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    p = _paths()
    synth = tmp_path / "synth_gtkb"
    synth.mkdir()
    (synth / p.GROUNDTRUTH_MARKER).write_text("# synthetic root\n", encoding="utf-8")
    monkeypatch.setenv(p.PROJECT_ROOT_ENV_VAR, str(synth))
    monkeypatch.delenv("GTKB_SPIKE_WORKSPACE", raising=False)

    # Seed the fixture directory so setup_disposable_repo() finds it under the
    # synthetic root, mirroring real package layout.
    fixture_src = Path(__file__).parent / "fixtures" / "bridge_spike_minimized_governance_hooks"
    fixture_dst = synth / "groundtruth-kb" / "tests" / "fixtures" / "bridge_spike_minimized_governance_hooks"
    fixture_dst.mkdir(parents=True, exist_ok=True)
    for f in fixture_src.iterdir():
        if f.is_file():
            (fixture_dst / f.name).write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
    return synth


def test_setup_disposable_repo_creates_layout_in_root(
    synthetic_gtkb_root: Path,
) -> None:
    spike = _load_spike_module()
    runner = spike.SpikeRunner(run_id="test-run-001")
    repo = runner.setup_disposable_repo()

    expected_parent = synthetic_gtkb_root / ".gtkb-state" / "bridge-poller" / "spikes" / "test-run-001"
    assert repo.is_relative_to(expected_parent)
    assert repo.is_relative_to(synthetic_gtkb_root)
    assert (repo / "groundtruth.toml").is_file()


def test_setup_disposable_repo_seeds_sentinel_strings(
    synthetic_gtkb_root: Path,
) -> None:
    spike = _load_spike_module()
    repo = spike.SpikeRunner(run_id="test-run-002").setup_disposable_repo()
    assert "SPIKE-SENTINEL-CLAUDE-XYZ123" in (repo / "CLAUDE.md").read_text(encoding="utf-8")
    assert "SPIKE-SENTINEL-AGENTS-XYZ123" in (repo / "AGENTS.md").read_text(encoding="utf-8")


def test_setup_disposable_repo_seeds_minimized_governance_hooks(
    synthetic_gtkb_root: Path,
) -> None:
    spike = _load_spike_module()
    repo = spike.SpikeRunner(run_id="test-run-003").setup_disposable_repo()
    hooks_dir = repo / ".claude" / "hooks"
    assert (hooks_dir / "sentinel_marker.py").is_file()
    assert (hooks_dir / "formal_artifact_approval_gate.py").is_file()
    assert (hooks_dir / "credential_scan.py").is_file()
    settings = json.loads((repo / ".claude" / "settings.json").read_text(encoding="utf-8"))
    assert "hooks" in settings
    assert "SessionStart" in settings["hooks"]


def test_setup_disposable_repo_refuses_when_path_resolves_outside_root(
    synthetic_gtkb_root: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    p = _paths()
    spike = _load_spike_module()
    out_of_root = tmp_path / "outside-root"
    monkeypatch.setenv("GTKB_SPIKE_WORKSPACE", str(out_of_root))
    with pytest.raises(p.StateDirOutOfRootError):
        spike.SpikeRunner(run_id="test-run-004").setup_disposable_repo()


def test_run_with_mocked_subprocesses_produces_complete_report(
    synthetic_gtkb_root: Path,
) -> None:
    spike = _load_spike_module()
    report_path = spike.run_spike(run_id="test-run-005", live=False)
    assert report_path.is_file()
    content = report_path.read_text(encoding="utf-8")
    assert "Bridge Poller Verification Spike" in content
    assert "Classification matrix" in content
    assert "Per-test evidence" in content
    assert "mocked-subprocess (default)" in content


def test_run_with_mocked_subprocesses_does_not_invoke_real_cli(
    synthetic_gtkb_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spike = _load_spike_module()
    real_run = subprocess.run

    def _fail_if_real_cli(cmd, *args, **kwargs):  # type: ignore[no-untyped-def]
        if cmd and cmd[0] in {"claude", "codex"}:
            raise AssertionError(f"Mocked default mode invoked real CLI: {cmd!r}")
        return real_run(cmd, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", _fail_if_real_cli)
    spike.run_spike(run_id="test-run-006", live=False)


def test_run_live_harnesses_requires_owner_approval_file(
    synthetic_gtkb_root: Path,
) -> None:
    """Subprocess test: invoking the script with --run-live-harnesses but
    without --owner-approval-file fails non-zero with a clear error."""
    p = _paths()
    env = {**os.environ, p.PROJECT_ROOT_ENV_VAR: str(synthetic_gtkb_root)}
    result = subprocess.run(
        [sys.executable, str(_SCRIPT_PATH), "--run-live-harnesses"],
        cwd=str(synthetic_gtkb_root),
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "owner-approval-file" in result.stderr.lower()


def test_run_live_harnesses_validates_approval_schema_missing_fields(
    synthetic_gtkb_root: Path,
) -> None:
    spike = _load_spike_module()
    approval_dir = synthetic_gtkb_root / ".gtkb-state" / "bridge-poller"
    approval_dir.mkdir(parents=True, exist_ok=True)
    bad = approval_dir / "missing-fields.json"
    bad.write_text('{"approval_text": "yep"}', encoding="utf-8")
    with pytest.raises(ValueError) as excinfo:
        spike.run_spike(run_id="test-run-007", live=True, owner_approval_file=bad)
    assert "missing required fields" in str(excinfo.value).lower()


def test_run_live_harnesses_rejects_low_token_cost_acknowledgment(
    synthetic_gtkb_root: Path,
) -> None:
    spike = _load_spike_module()
    approval_dir = synthetic_gtkb_root / ".gtkb-state" / "bridge-poller"
    approval_dir.mkdir(parents=True, exist_ok=True)
    bad = approval_dir / "low-cost.json"
    payload = {
        "approval_text": "approved",
        "approval_source_ref": "test",
        "approval_session": "S319",
        "approval_recorded_at": "2026-04-28T00:00:00+00:00",
        "estimated_token_cost": 1000,  # below floor
        "estimated_token_cost_acknowledgment": "test",
    }
    bad.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError) as excinfo:
        spike.run_spike(run_id="test-run-008", live=True, owner_approval_file=bad)
    assert "below minimum" in str(excinfo.value).lower()


def test_run_live_harnesses_validates_run_id_constraint(
    synthetic_gtkb_root: Path,
) -> None:
    spike = _load_spike_module()
    approval_dir = synthetic_gtkb_root / ".gtkb-state" / "bridge-poller"
    approval_dir.mkdir(parents=True, exist_ok=True)
    bound = approval_dir / "bound.json"
    payload = {
        "approval_text": "approved",
        "approval_source_ref": "test",
        "approval_session": "S319",
        "approval_recorded_at": "2026-04-28T00:00:00+00:00",
        "estimated_token_cost": 2_100_000,
        "estimated_token_cost_acknowledgment": "test",
        "run_id_constraint": "DIFFERENT-RUN-ID",
    }
    bound.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError) as excinfo:
        spike.run_spike(run_id="test-run-009", live=True, owner_approval_file=bound)
    assert "bound to run_id" in str(excinfo.value).lower()


def test_run_live_harnesses_rejects_out_of_root_approval_file(synthetic_gtkb_root: Path, tmp_path: Path) -> None:
    spike = _load_spike_module()
    out_of_root_approval = tmp_path / "out-of-root-approval.json"
    payload = {
        "approval_text": "approved",
        "approval_source_ref": "test",
        "approval_session": "S319",
        "approval_recorded_at": "2026-04-28T00:00:00+00:00",
        "estimated_token_cost": 2_100_000,
        "estimated_token_cost_acknowledgment": "test",
    }
    out_of_root_approval.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError) as excinfo:
        spike.run_spike(
            run_id="test-run-010",
            live=True,
            owner_approval_file=out_of_root_approval,
        )
    assert "outside project root" in str(excinfo.value).lower()


def test_findings_classify_out_of_scope_when_no_hook_fires(
    synthetic_gtkb_root: Path,
) -> None:
    """Classification: neither sentinel nor gov-hook fired → OUT_OF_SCOPE."""
    spike = _load_spike_module()
    test_result = spike.TestResult(
        test_id="C1",
        command=("claude", "-p", "x"),
        exit_code=0,
        stdout="",
        stderr="",
        duration_s=0.1,
        sentinel_hook_fired=False,
        sentinel_gov_hook_fired=False,
        protected_spec_unchanged=True,
    )
    classification = spike._classify("claude", "default", [test_result])
    assert classification.verdict == "OUT_OF_SCOPE"


def test_findings_classify_review_only_when_only_sentinel_fires(
    synthetic_gtkb_root: Path,
) -> None:
    """Classification: sentinel fires but gov-hook doesn't → REVIEW_ONLY."""
    spike = _load_spike_module()
    test_result = spike.TestResult(
        test_id="C5",
        command=("claude", "-p", "x"),
        exit_code=0,
        stdout="",
        stderr="",
        duration_s=0.1,
        sentinel_hook_fired=True,
        sentinel_gov_hook_fired=False,
        protected_spec_unchanged=True,
    )
    classification = spike._classify("claude", "default", [test_result])
    assert classification.verdict == "REVIEW_ONLY"


def test_findings_classify_write_capable_when_both_fire_and_block(
    synthetic_gtkb_root: Path,
) -> None:
    """Classification: both fire AND protected-write blocked → WRITE_CAPABLE."""
    spike = _load_spike_module()
    test_result = spike.TestResult(
        test_id="C6b",
        command=("claude", "-p", "x"),
        exit_code=0,
        stdout="",
        stderr="",
        duration_s=0.1,
        sentinel_hook_fired=True,
        sentinel_gov_hook_fired=True,
        protected_spec_unchanged=True,
    )
    classification = spike._classify("claude", "default", [test_result])
    assert classification.verdict == "WRITE_CAPABLE"
