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
    # Per Codex acceptance target #4 at -006: mocked vs live distinction
    assert "**MOCKED**" in content
    assert "MUST NOT be used as P3 invoker classification evidence" in content


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


def _make_completed(returncode: int = 0, stdout: str = "", stderr: str = ""):
    """Build a subprocess.CompletedProcess-shaped object for fake runners."""
    import subprocess as _sp

    return _sp.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


def test_run_live_calls_real_adapter_not_mocked_synthesis(synthetic_gtkb_root: Path, tmp_path: Path) -> None:
    """Live mode must reach _run_command_live (the real adapter), NOT _run_command_mocked.

    Verifies that the per-result test_id is "LIVE" (set by the real adapter)
    rather than "MOCK" (set by the mocked synthesis path) — this is the
    distinguishing fingerprint Codex's NO-GO at -006 asked us to add.
    """
    spike = _load_spike_module()

    approval_dir = synthetic_gtkb_root / ".gtkb-state" / "bridge-poller"
    approval_dir.mkdir(parents=True, exist_ok=True)
    approval_file = approval_dir / "ok-approval.json"
    approval_file.write_text(
        json.dumps(
            {
                "approval_text": "approved",
                "approval_source_ref": "test",
                "approval_session": "S319",
                "approval_recorded_at": "2026-04-28T00:00:00+00:00",
                "estimated_token_cost": 2_100_000,
                "estimated_token_cost_acknowledgment": "test",
            }
        ),
        encoding="utf-8",
    )

    invocations: list[tuple] = []

    def fake_runner(cmd, **kwargs):
        invocations.append((tuple(cmd), kwargs.get("cwd"), kwargs.get("timeout")))
        return _make_completed(returncode=0, stdout="fake-stdout", stderr="")

    spike.run_spike(
        run_id="live-test-001",
        live=True,
        owner_approval_file=approval_file,
        subprocess_runner=fake_runner,
    )

    assert len(invocations) == 8, f"expected 8 live commands (4 claude modes + 4 codex modes), got {len(invocations)}"
    for cmd_tuple, cwd, timeout in invocations:
        assert cmd_tuple[0] in ("claude", "codex"), f"unexpected cmd: {cmd_tuple}"
        assert cwd is not None, "cwd must be set on the disposable repo"
        assert timeout is not None and isinstance(timeout, int), "timeout must be set"


def test_run_live_does_not_invoke_real_subprocess_run_in_test(
    synthetic_gtkb_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When subprocess_runner is injected, the real subprocess.run is never called.

    Hard-fails if any test path falls through to real CLI invocation.
    """
    spike = _load_spike_module()

    approval_dir = synthetic_gtkb_root / ".gtkb-state" / "bridge-poller"
    approval_dir.mkdir(parents=True, exist_ok=True)
    approval_file = approval_dir / "ok-approval.json"
    approval_file.write_text(
        json.dumps(
            {
                "approval_text": "approved",
                "approval_source_ref": "test",
                "approval_session": "S319",
                "approval_recorded_at": "2026-04-28T00:00:00+00:00",
                "estimated_token_cost": 2_100_000,
                "estimated_token_cost_acknowledgment": "test",
            }
        ),
        encoding="utf-8",
    )

    real_run_called = []

    def fail_if_real_run(*args, **kwargs):
        real_run_called.append((args, kwargs))
        raise AssertionError("Real subprocess.run was invoked despite subprocess_runner injection.")

    monkeypatch.setattr(subprocess, "run", fail_if_real_run)

    fake_runner_calls = []

    def fake_runner(cmd, **kwargs):
        fake_runner_calls.append(cmd)
        return _make_completed(returncode=0, stdout="ok", stderr="")

    spike.run_spike(
        run_id="live-test-002",
        live=True,
        owner_approval_file=approval_file,
        subprocess_runner=fake_runner,
    )

    assert real_run_called == [], "subprocess.run was unexpectedly invoked"
    assert len(fake_runner_calls) == 8, "fake runner should receive all 8 command invocations"


def test_run_live_populates_sentinel_fired_via_marker_delta(
    synthetic_gtkb_root: Path,
) -> None:
    """Live adapter detects sentinel-hook firing by comparing pre/post marker globs.

    A fake runner that creates a SENTINEL_HOOK_FIRED-* file should cause the
    resulting TestResult.sentinel_hook_fired to be True.
    """
    spike = _load_spike_module()

    approval_dir = synthetic_gtkb_root / ".gtkb-state" / "bridge-poller"
    approval_dir.mkdir(parents=True, exist_ok=True)
    approval_file = approval_dir / "ok-approval.json"
    approval_file.write_text(
        json.dumps(
            {
                "approval_text": "approved",
                "approval_source_ref": "test",
                "approval_session": "S319",
                "approval_recorded_at": "2026-04-28T00:00:00+00:00",
                "estimated_token_cost": 2_100_000,
                "estimated_token_cost_acknowledgment": "test",
            }
        ),
        encoding="utf-8",
    )

    def fake_runner_that_fires_sentinel(cmd, **kwargs):
        evidence_dir_str = kwargs["env"]["SPIKE_EVIDENCE_DIR"]
        evidence_dir = Path(evidence_dir_str)
        # Simulate the sentinel hook firing during this subprocess invocation.
        marker_path = evidence_dir / f"SENTINEL_HOOK_FIRED-{cmd[0]}-{len(list(evidence_dir.iterdir()))}"
        marker_path.write_text("ok\n", encoding="utf-8")
        return _make_completed(returncode=0, stdout="ok", stderr="")

    report_path = spike.run_spike(
        run_id="live-test-003",
        live=True,
        owner_approval_file=approval_file,
        subprocess_runner=fake_runner_that_fires_sentinel,
    )

    # Read the report and verify it's a LIVE report
    content = report_path.read_text(encoding="utf-8")
    assert "**LIVE**" in content, "live mode report must be tagged LIVE in mode line"
    assert "**MOCKED**" not in content


def test_run_live_report_distinguished_from_mocked_report(
    synthetic_gtkb_root: Path,
) -> None:
    """spike-report.md must clearly mark live vs mocked.

    Per Codex acceptance target #4 at -006: 'The resulting spike-report.md
    distinguishes mocked reports from live evidence.'
    """
    spike = _load_spike_module()

    mocked_report = spike.run_spike(run_id="mocked-test-001", live=False)
    mocked_content = mocked_report.read_text(encoding="utf-8")
    assert "**MOCKED**" in mocked_content
    assert "**LIVE**" not in mocked_content
    assert "MUST NOT be used as P3 invoker classification evidence" in mocked_content


def test_run_live_handles_filenotfound_when_real_cli_absent(
    synthetic_gtkb_root: Path,
) -> None:
    """Live adapter records exit_code=127 when the real CLI binary is missing."""
    spike = _load_spike_module()

    approval_dir = synthetic_gtkb_root / ".gtkb-state" / "bridge-poller"
    approval_dir.mkdir(parents=True, exist_ok=True)
    approval_file = approval_dir / "ok-approval.json"
    approval_file.write_text(
        json.dumps(
            {
                "approval_text": "approved",
                "approval_source_ref": "test",
                "approval_session": "S319",
                "approval_recorded_at": "2026-04-28T00:00:00+00:00",
                "estimated_token_cost": 2_100_000,
                "estimated_token_cost_acknowledgment": "test",
            }
        ),
        encoding="utf-8",
    )

    def fake_runner_missing_binary(cmd, **kwargs):
        raise FileNotFoundError(f"[Errno 2] No such file or directory: {cmd[0]!r}")

    report_path = spike.run_spike(
        run_id="live-test-004",
        live=True,
        owner_approval_file=approval_file,
        subprocess_runner=fake_runner_missing_binary,
    )
    content = report_path.read_text(encoding="utf-8")
    assert "exit_code: 127" in content
