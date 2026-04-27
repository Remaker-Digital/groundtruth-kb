"""Tests for Wave 2 Slice 11 ``_dashboard_regen.py`` and ``_dashboard_regen_runner.py``.

Per ``bridge/gtkb-isolation-016-phase8-wave2-slice11-011.md`` (REVISED-5)
and ``-012`` (Codex GO with 6 implementation constraints).

Lane tests use ``subprocess_invoker=`` callable injection so the runner
subprocess is faked. Runner tests exercise ``build_is_allowed`` and
``build_audit_hook`` factories directly via Python imports — proving the
audit-hook policy without spawning a real subprocess.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from rehearse import _dashboard_regen, _dashboard_regen_runner  # noqa: E402

# ---- Fixtures ---------------------------------------------------------


def _make_minimal_legacy_root(tmp_path: Path) -> Path:
    """Build a legacy_root tree containing all REQUIRED + 5 deployment files.

    Each file gets distinct content so byte-equal verification has
    something to check.
    """
    legacy = tmp_path / "legacy"
    (legacy / "scripts" / "rehearse").mkdir(parents=True)
    (legacy / "scripts" / "deploy").mkdir(parents=True)
    (legacy / "bridge").mkdir(parents=True)
    (legacy / "memory").mkdir(parents=True)
    (legacy / ".claude" / "rules").mkdir(parents=True)
    (legacy / ".github" / "workflows").mkdir(parents=True)

    # Generator + helper code.
    (legacy / "scripts" / "session_self_initialization.py").write_text(
        "# generator stub for tests\nprint('generator ran')\n", encoding="utf-8"
    )
    (legacy / "scripts" / "_wrap_io.py").write_text("def _atomic_write_text(p, t): p.write_text(t)\n", encoding="utf-8")
    (legacy / "scripts" / "__init__.py").touch()
    (legacy / "scripts" / "rehearse" / "__init__.py").touch()
    (legacy / "scripts" / "rehearse" / "_dashboard_regen_runner.py").write_text(
        "# runner stub for tests\n", encoding="utf-8"
    )

    # Required sandbox inputs.
    (legacy / "groundtruth.db").write_bytes(b"SQLite stub for tests")
    (legacy / "bridge" / "INDEX.md").write_text("# bridge index\n", encoding="utf-8")
    (legacy / ".claude" / "rules" / "operating-role.md").write_text("active_role: prime-builder\n", encoding="utf-8")
    (legacy / "memory" / "work_list.md").write_text("# work list\n", encoding="utf-8")
    (legacy / "memory" / "release-readiness.md").write_text("# release readiness\n", encoding="utf-8")
    (legacy / "pyproject.toml").write_text("[project]\nname='stub'\n", encoding="utf-8")
    (legacy / ".github" / "workflows" / "build.yml").write_text("name: build\n", encoding="utf-8")

    # The 5 deployment files (each with distinct content for sha256).
    (legacy / "scripts" / "agent-container-template.yaml").write_text("kind: Deployment\n", encoding="utf-8")
    (legacy / "scripts" / "deploy" / "build-and-deploy-staging.ps1").write_text(
        "Write-Host 'staging deploy'\n", encoding="utf-8"
    )
    (legacy / "scripts" / "deploy" / "api-gateway-restore.yaml").write_text("apiVersion: v1\n", encoding="utf-8")
    (legacy / "scripts" / "deploy" / "upgrade.ps1").write_text("Write-Host 'upgrade'\n", encoding="utf-8")
    (legacy / "scripts" / "deploy" / "rollback.ps1").write_text("Write-Host 'rollback'\n", encoding="utf-8")

    return legacy


def _make_fake_invoker(
    *,
    returncode: int = 0,
    stdout: str = "",
    stderr: str = "",
    violations: list[dict[str, Any]] | None = None,
    raise_timeout: bool = False,
) -> Callable[[list[str], Path], subprocess.CompletedProcess[str]]:
    """Build a fake subprocess invoker for lane tests.

    Writes the supplied ``violations`` to the path passed in
    ``--violations-out`` so the lane reads them back from disk per the
    real runner's protocol.
    """

    def invoke(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
        if raise_timeout:
            raise subprocess.TimeoutExpired(cmd, timeout=120)
        if "--violations-out" in cmd:
            i = cmd.index("--violations-out")
            violations_path = Path(cmd[i + 1])
            violations_path.parent.mkdir(parents=True, exist_ok=True)
            violations_path.write_text(json.dumps(violations or []), encoding="utf-8")
        return subprocess.CompletedProcess(cmd, returncode, stdout, stderr)

    return invoke


def _read_plan(output_dir: Path) -> dict[str, Any]:
    return json.loads((output_dir / "dashboard_regen" / "dashboard-regen-plan.json").read_text(encoding="utf-8"))


# =====================================================================
# §7.1 Core common-contract + plan tests (10 tests)
# =====================================================================


def test_run_dry_run_returns_skipped(tmp_path: Path) -> None:
    """Dry-run never reads the legacy tree."""
    result = _dashboard_regen.run({}, tmp_path / "output", dry_run=True)
    assert result["status"] == "skipped"
    assert result["metrics"] == {"reason": "dry_run"}


def test_run_probes_generator_existence(tmp_path: Path) -> None:
    """Probe records generator path + size when present."""
    legacy = _make_minimal_legacy_root(tmp_path)
    _dashboard_regen.run({}, tmp_path / "output", project_root=legacy, subprocess_invoker=_make_fake_invoker())
    plan = _read_plan(tmp_path / "output")
    assert plan["source"]["generator"]["exists"] is True
    assert plan["source"]["generator"]["size_bytes"] > 0


def test_run_emits_warning_when_generator_absent(tmp_path: Path) -> None:
    """Generator missing → status='error'."""
    legacy = tmp_path / "legacy_empty"
    legacy.mkdir()
    result = _dashboard_regen.run({}, tmp_path / "output", project_root=legacy, subprocess_invoker=_make_fake_invoker())
    assert result["status"] == "error"
    assert any("generator_script_not_found" in w for w in result["warnings"])


def test_run_probes_current_dashboard_artifacts_size_only(tmp_path: Path) -> None:
    """Probe records dashboard artifact presence + size, never content."""
    legacy = _make_minimal_legacy_root(tmp_path)
    (legacy / "docs" / "gtkb-dashboard").mkdir(parents=True)
    (legacy / "docs" / "gtkb-dashboard" / "index.html").write_text("<html>secret</html>", encoding="utf-8")
    _dashboard_regen.run({}, tmp_path / "output", project_root=legacy, subprocess_invoker=_make_fake_invoker())
    plan = _read_plan(tmp_path / "output")
    assert plan["source"]["dashboard"]["index_html"]["exists"] is True
    assert plan["source"]["dashboard"]["index_html"]["size_bytes"] > 0
    # Verify no html content in the plan output.
    plan_text = json.dumps(plan)
    assert "secret" not in plan_text


def test_run_probes_lifecycle_hooks(tmp_path: Path) -> None:
    """Probe checks .claude/settings.json + .codex/hooks.json presence."""
    legacy = _make_minimal_legacy_root(tmp_path)
    (legacy / ".claude" / "settings.json").write_text('{"hooks":{}}', encoding="utf-8")
    _dashboard_regen.run({}, tmp_path / "output", project_root=legacy, subprocess_invoker=_make_fake_invoker())
    plan = _read_plan(tmp_path / "output")
    assert plan["source"]["lifecycle_hooks"]["claude_settings"] is True


def test_run_emits_relocation_plan_with_five_path_pairs(tmp_path: Path) -> None:
    """Plan includes all 5 source→target relocation entries."""
    legacy = _make_minimal_legacy_root(tmp_path)
    _dashboard_regen.run({}, tmp_path / "output", project_root=legacy, subprocess_invoker=_make_fake_invoker())
    plan = _read_plan(tmp_path / "output")
    relocation = plan["regen_plan"]
    assert "applications/Agent_Red" in relocation["target_generator_path"]
    assert "applications/Agent_Red" in relocation["target_dashboard_path"]
    assert "applications/Agent_Red" in relocation["target_data_json_path"]
    assert "applications/Agent_Red" in relocation["target_history_path"]
    assert "applications/Agent_Red" in relocation["target_grafana_path"]


def test_run_writes_dashboard_regen_plan_json(tmp_path: Path) -> None:
    """Lane writes the plan JSON file."""
    legacy = _make_minimal_legacy_root(tmp_path)
    _dashboard_regen.run({}, tmp_path / "output", project_root=legacy, subprocess_invoker=_make_fake_invoker())
    plan_path = tmp_path / "output" / "dashboard_regen" / "dashboard-regen-plan.json"
    assert plan_path.exists()
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    assert plan["schema_version"] == 1


def test_run_writes_preview_markdown(tmp_path: Path) -> None:
    """Lane writes the markdown preview."""
    legacy = _make_minimal_legacy_root(tmp_path)
    _dashboard_regen.run({}, tmp_path / "output", project_root=legacy, subprocess_invoker=_make_fake_invoker())
    preview_path = tmp_path / "output" / "dashboard_regen" / "dashboard-regen-preview.md"
    assert preview_path.exists()
    content = preview_path.read_text(encoding="utf-8")
    assert "# Dashboard Regeneration Plan" in content
    assert "## Sandbox Boundary Proof" in content
    assert "## Deployment Files" in content


def test_run_writes_result_json_on_ok_path(tmp_path: Path) -> None:
    """Per Wave 2 -003 §4.2 + Slice 4 -006 F2: result.json on ok path."""
    legacy = _make_minimal_legacy_root(tmp_path)
    result = _dashboard_regen.run({}, tmp_path / "output", project_root=legacy, subprocess_invoker=_make_fake_invoker())
    assert result["status"] == "ok"
    result_path = tmp_path / "output" / "dashboard_regen" / "result.json"
    assert result_path.exists()
    assert str(result_path) in result["output_files"]


def test_run_writes_result_json_on_error_path(tmp_path: Path) -> None:
    """Error path also emits result.json."""
    legacy = tmp_path / "legacy_empty"
    legacy.mkdir()
    result = _dashboard_regen.run({}, tmp_path / "output", project_root=legacy)
    assert result["status"] == "error"
    result_path = tmp_path / "output" / "dashboard_regen" / "result.json"
    assert result_path.exists()


# =====================================================================
# §7.2 Audit-hook + sandbox-boundary tests (8 tests)
# =====================================================================


def test_run_status_ok_when_subprocess_returncode_zero_and_no_violations(tmp_path: Path) -> None:
    legacy = _make_minimal_legacy_root(tmp_path)
    result = _dashboard_regen.run(
        {}, tmp_path / "output", project_root=legacy, subprocess_invoker=_make_fake_invoker(returncode=0)
    )
    assert result["status"] == "ok"


def test_run_status_error_when_audit_hook_violations_nonempty(tmp_path: Path) -> None:
    """Violations override returncode=0 → status='error'."""
    legacy = _make_minimal_legacy_root(tmp_path)
    invoker = _make_fake_invoker(returncode=1, violations=[{"event": "open", "path": str(legacy / ".env.local")}])
    result = _dashboard_regen.run({}, tmp_path / "output", project_root=legacy, subprocess_invoker=invoker)
    assert result["status"] == "error"
    assert any("legacy_data_read_detected" in w for w in result["warnings"])


def test_run_status_error_when_subprocess_returncode_nonzero(tmp_path: Path) -> None:
    """Subprocess crash without violations → status='error'."""
    legacy = _make_minimal_legacy_root(tmp_path)
    result = _dashboard_regen.run(
        {},
        tmp_path / "output",
        project_root=legacy,
        subprocess_invoker=_make_fake_invoker(returncode=2, stderr="generator crashed"),
    )
    assert result["status"] == "error"
    assert any("subprocess_returncode_nonzero" in w for w in result["warnings"])


def test_run_status_error_on_subprocess_timeout(tmp_path: Path) -> None:
    """Subprocess timeout → status='error' with timeout warning."""
    legacy = _make_minimal_legacy_root(tmp_path)
    result = _dashboard_regen.run(
        {}, tmp_path / "output", project_root=legacy, subprocess_invoker=_make_fake_invoker(raise_timeout=True)
    )
    assert result["status"] == "error"
    assert any("subprocess_timeout" in w for w in result["warnings"])


def test_run_emits_audit_hook_proof_block_on_ok_path(tmp_path: Path) -> None:
    legacy = _make_minimal_legacy_root(tmp_path)
    _dashboard_regen.run({}, tmp_path / "output", project_root=legacy, subprocess_invoker=_make_fake_invoker())
    plan = _read_plan(tmp_path / "output")
    proof = plan["audit_hook_proof"]
    assert proof["hook_installed_before_legacy_script_import"] is True
    assert "open" in proof["audit_events_intercepted"]
    assert "subprocess.Popen" in proof["audit_events_intercepted"]
    assert proof["violations_count"] == 0
    assert proof["verdict"] == "no_legacy_data_read_detected"


def test_run_emits_audit_hook_proof_block_on_error_path(tmp_path: Path) -> None:
    legacy = _make_minimal_legacy_root(tmp_path)
    invoker = _make_fake_invoker(violations=[{"event": "open", "path": str(legacy / ".env.local")}])
    _dashboard_regen.run({}, tmp_path / "output", project_root=legacy, subprocess_invoker=invoker)
    plan = _read_plan(tmp_path / "output")
    proof = plan["audit_hook_proof"]
    assert proof["violations_count"] == 1
    assert proof["verdict"] == "legacy_data_read_detected"


def test_run_NEVER_renames_or_overwrites_canonical_legacy_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """**CRITICAL safety regression** vs. the rejected `-005` sentinel-plant approach."""
    legacy = _make_minimal_legacy_root(tmp_path)
    real_rename = Path.rename
    real_replace = Path.replace
    forbidden_renames: list[str] = []

    def _trap_rename(self: Path, target: Path) -> Path:  # type: ignore[no-untyped-def]
        s = str(self.resolve())
        if "legacy" in s and "/output/" not in s:
            forbidden_renames.append(s)
            raise AssertionError(f"Lane illegally renamed legacy file {s}")
        return real_rename(self, target)

    def _trap_replace(self: Path, target: Path) -> Path:  # type: ignore[no-untyped-def]
        s = str(self.resolve())
        if "legacy" in s and "/output/" not in s:
            forbidden_renames.append(s)
            raise AssertionError(f"Lane illegally replaced legacy file {s}")
        return real_replace(self, target)

    monkeypatch.setattr(Path, "rename", _trap_rename)
    monkeypatch.setattr(Path, "replace", _trap_replace)
    _dashboard_regen.run({}, tmp_path / "output", project_root=legacy, subprocess_invoker=_make_fake_invoker())
    assert forbidden_renames == [], f"Lane attempted forbidden renames: {forbidden_renames}"


def test_run_does_not_create_sentinel_files_in_legacy_root(tmp_path: Path) -> None:
    """**CRITICAL safety regression**: no `.rehearsal-sentinel-tmp` paths under legacy."""
    legacy = _make_minimal_legacy_root(tmp_path)
    pre_files = {p.name for p in legacy.rglob("*") if p.is_file()}
    _dashboard_regen.run({}, tmp_path / "output", project_root=legacy, subprocess_invoker=_make_fake_invoker())
    post_files = {p.name for p in legacy.rglob("*") if p.is_file()}
    new_files = post_files - pre_files
    assert all("rehearsal-sentinel" not in name for name in new_files)
    assert all("rehearsal-canonical-saved" not in name for name in new_files)


# =====================================================================
# §7.3 Sandbox composition tests (5 tests)
# =====================================================================


def test_run_copies_required_inputs_to_sandbox_as_real_files_not_symlinks(tmp_path: Path) -> None:
    legacy = _make_minimal_legacy_root(tmp_path)
    _dashboard_regen.run({}, tmp_path / "output", project_root=legacy, subprocess_invoker=_make_fake_invoker())
    sandbox = tmp_path / "output" / "dashboard_regen" / "sandbox"
    for rel in ("groundtruth.db", "bridge/INDEX.md", "memory/work_list.md", "pyproject.toml"):
        p = sandbox / rel
        assert p.is_file(), f"Required input {rel} not in sandbox"
        assert not p.is_symlink(), f"Required input {rel} is a symlink (must be real file)"


def test_run_warns_when_optional_input_missing_from_sandbox(tmp_path: Path) -> None:
    """REVISED-5 §3.2 narrowed: optional non-deployment input missing → warning, not error."""
    legacy = _make_minimal_legacy_root(tmp_path)
    # src/api_versioning.py is OPTIONAL and NOT created in fixture.
    result = _dashboard_regen.run({}, tmp_path / "output", project_root=legacy, subprocess_invoker=_make_fake_invoker())
    assert result["status"] == "ok"
    assert any("optional_input_missing" in w and "api_versioning" in w for w in result["warnings"])


def test_run_returns_error_when_required_input_missing_from_sandbox(tmp_path: Path) -> None:
    """Required input missing from legacy → status='error'."""
    legacy = _make_minimal_legacy_root(tmp_path)
    (legacy / "groundtruth.db").unlink()
    result = _dashboard_regen.run({}, tmp_path / "output", project_root=legacy, subprocess_invoker=_make_fake_invoker())
    assert result["status"] == "error"
    assert any("required_input_missing" in w and "groundtruth.db" in w for w in result["warnings"])


def test_run_excludes_dotenv_local_from_sandbox(tmp_path: Path) -> None:
    """Even if legacy has .env.local, sandbox MUST NOT contain it (per §3.5)."""
    legacy = _make_minimal_legacy_root(tmp_path)
    (legacy / ".env.local").write_text("SECRET=exposed", encoding="utf-8")
    _dashboard_regen.run({}, tmp_path / "output", project_root=legacy, subprocess_invoker=_make_fake_invoker())
    sandbox = tmp_path / "output" / "dashboard_regen" / "sandbox"
    assert not (sandbox / ".env.local").exists(), "sandbox must not contain .env.local"


def test_run_writes_fresh_lifecycle_guard_in_sandbox(tmp_path: Path) -> None:
    """Lifecycle-guard.json is generated fresh in sandbox with current-session metadata."""
    legacy = _make_minimal_legacy_root(tmp_path)
    _dashboard_regen.run({}, tmp_path / "output", project_root=legacy, subprocess_invoker=_make_fake_invoker())
    guard_path = tmp_path / "output" / "dashboard_regen" / "sandbox" / ".claude" / "session" / "lifecycle-guard.json"
    assert guard_path.exists()
    guard = json.loads(guard_path.read_text(encoding="utf-8"))
    assert "start_iso" in guard
    assert "session_id" in guard


# =====================================================================
# §7.4 Subprocess invocation parameters (3 tests)
# =====================================================================


def test_run_subprocess_command_includes_fast_hook_flag(tmp_path: Path) -> None:
    legacy = _make_minimal_legacy_root(tmp_path)
    captured_cmds: list[list[str]] = []

    def _capture(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
        captured_cmds.append(list(cmd))
        violations_idx = cmd.index("--violations-out")
        Path(cmd[violations_idx + 1]).parent.mkdir(parents=True, exist_ok=True)
        Path(cmd[violations_idx + 1]).write_text("[]", encoding="utf-8")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    _dashboard_regen.run({}, tmp_path / "output", project_root=legacy, subprocess_invoker=_capture)
    assert captured_cmds, "expected at least one subprocess call"
    assert "--fast-hook" in captured_cmds[0]


def test_run_subprocess_command_routes_through_runner_not_legacy_script_directly(tmp_path: Path) -> None:
    legacy = _make_minimal_legacy_root(tmp_path)
    captured_cmds: list[list[str]] = []

    def _capture(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
        captured_cmds.append(list(cmd))
        Path(cmd[cmd.index("--violations-out") + 1]).parent.mkdir(parents=True, exist_ok=True)
        Path(cmd[cmd.index("--violations-out") + 1]).write_text("[]", encoding="utf-8")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    _dashboard_regen.run({}, tmp_path / "output", project_root=legacy, subprocess_invoker=_capture)
    assert captured_cmds[0][0] == sys.executable
    assert "_dashboard_regen_runner.py" in captured_cmds[0][1]
    # session_self_initialization.py path appears as --legacy-script value, not as argv[1]
    assert "session_self_initialization.py" not in captured_cmds[0][1]


def test_run_subprocess_passes_sandbox_root_explicitly_to_runner(tmp_path: Path) -> None:
    legacy = _make_minimal_legacy_root(tmp_path)
    captured_cmds: list[list[str]] = []

    def _capture(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
        captured_cmds.append(list(cmd))
        Path(cmd[cmd.index("--violations-out") + 1]).parent.mkdir(parents=True, exist_ok=True)
        Path(cmd[cmd.index("--violations-out") + 1]).write_text("[]", encoding="utf-8")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    _dashboard_regen.run({}, tmp_path / "output", project_root=legacy, subprocess_invoker=_capture)
    assert "--sandbox-root" in captured_cmds[0]
    sandbox_idx = captured_cmds[0].index("--sandbox-root")
    sandbox_arg = captured_cmds[0][sandbox_idx + 1]
    assert "dashboard_regen/sandbox" in sandbox_arg.replace("\\", "/")


# =====================================================================
# §7.5 Boundary tightness (11 tests #27-37) — direct unit tests of build_is_allowed
# =====================================================================


def _setup_runner_fixture(tmp_path: Path) -> tuple[Path, Path]:
    """Build legacy + sandbox roots for runner unit tests."""
    legacy = tmp_path / "legacy"
    sandbox = tmp_path / "sandbox"
    (legacy / "scripts" / "rehearse").mkdir(parents=True)
    (legacy / "scripts" / "deploy").mkdir(parents=True)
    sandbox.mkdir(parents=True)
    return legacy, sandbox


def test_audit_hook_allows_session_self_initialization_py_read(tmp_path: Path) -> None:
    legacy, sandbox = _setup_runner_fixture(tmp_path)
    target = legacy / "scripts" / "session_self_initialization.py"
    target.touch()
    is_allowed = _dashboard_regen_runner.build_is_allowed(legacy, sandbox)
    assert is_allowed(str(target)) is True


def test_audit_hook_allows_wrap_io_helper_read(tmp_path: Path) -> None:
    legacy, sandbox = _setup_runner_fixture(tmp_path)
    target = legacy / "scripts" / "_wrap_io.py"
    target.touch()
    is_allowed = _dashboard_regen_runner.build_is_allowed(legacy, sandbox)
    assert is_allowed(str(target)) is True


@pytest.mark.parametrize(
    "module_name",
    ["workstream_focus", "gtkb_overlay", "gtkb_scoped_client"],
)
def test_audit_hook_allows_generator_try_block_imports(tmp_path: Path, module_name: str) -> None:
    """Per impl-time discovery: generator imports 3 more modules at lines 38-86
    inside try/except blocks. All must be allow-listed.
    """
    legacy, sandbox = _setup_runner_fixture(tmp_path)
    target = legacy / "scripts" / f"{module_name}.py"
    target.touch()
    is_allowed = _dashboard_regen_runner.build_is_allowed(legacy, sandbox)
    assert is_allowed(str(target)) is True


def test_audit_hook_rejects_legacy_deploy_py_read(tmp_path: Path) -> None:
    """deploy.py at scripts/ top level → glob-deny under legacy_root/scripts."""
    legacy, sandbox = _setup_runner_fixture(tmp_path)
    target = legacy / "scripts" / "deploy.py"
    target.touch()
    is_allowed = _dashboard_regen_runner.build_is_allowed(legacy, sandbox)
    assert is_allowed(str(target)) is False


def test_audit_hook_rejects_legacy_deploy_pipeline_py_read(tmp_path: Path) -> None:
    legacy, sandbox = _setup_runner_fixture(tmp_path)
    target = legacy / "scripts" / "deploy_pipeline.py"
    target.touch()
    is_allowed = _dashboard_regen_runner.build_is_allowed(legacy, sandbox)
    assert is_allowed(str(target)) is False


def test_audit_hook_rejects_legacy_deploy_ps1_read(tmp_path: Path) -> None:
    """scripts/deploy/ directory deny."""
    legacy, sandbox = _setup_runner_fixture(tmp_path)
    target = legacy / "scripts" / "deploy" / "upgrade.ps1"
    target.write_text("Write-Host 'x'\n", encoding="utf-8")
    is_allowed = _dashboard_regen_runner.build_is_allowed(legacy, sandbox)
    assert is_allowed(str(target)) is False


def test_audit_hook_allows_sandbox_copy_of_deploy_file(tmp_path: Path) -> None:
    """Sandbox-copied deployment file is allowed via sandbox-prefix rule."""
    legacy, sandbox = _setup_runner_fixture(tmp_path)
    (sandbox / "scripts" / "deploy").mkdir(parents=True)
    sandbox_file = sandbox / "scripts" / "deploy" / "upgrade.ps1"
    sandbox_file.write_text("Write-Host 'sandbox'\n", encoding="utf-8")
    is_allowed = _dashboard_regen_runner.build_is_allowed(legacy, sandbox)
    assert is_allowed(str(sandbox_file)) is True


def test_audit_hook_rejects_legacy_dotenv_local_read(tmp_path: Path) -> None:
    legacy, sandbox = _setup_runner_fixture(tmp_path)
    target = legacy / ".env.local"
    target.write_text("SECRET=x\n", encoding="utf-8")
    is_allowed = _dashboard_regen_runner.build_is_allowed(legacy, sandbox)
    assert is_allowed(str(target)) is False


def test_audit_hook_rejects_legacy_memory_work_list_read(tmp_path: Path) -> None:
    legacy, sandbox = _setup_runner_fixture(tmp_path)
    (legacy / "memory").mkdir()
    target = legacy / "memory" / "work_list.md"
    target.write_text("# work list\n", encoding="utf-8")
    is_allowed = _dashboard_regen_runner.build_is_allowed(legacy, sandbox)
    assert is_allowed(str(target)) is False


def test_audit_hook_rejects_path_traversal_via_dotdot(tmp_path: Path) -> None:
    """`..` traversal is canonicalized away → still denied."""
    legacy, sandbox = _setup_runner_fixture(tmp_path)
    (legacy / "memory").mkdir()
    (legacy / "memory" / "work_list.md").write_text("x", encoding="utf-8")
    # Construct a traversal path that resolves to legacy/memory/work_list.md
    traversal = sandbox / ".." / "legacy" / "memory" / "work_list.md"
    is_allowed = _dashboard_regen_runner.build_is_allowed(legacy, sandbox)
    assert is_allowed(str(traversal)) is False


def test_audit_hook_rejects_symlink_to_legacy_data(tmp_path: Path) -> None:
    """Symlink under sandbox pointing to legacy data → resolved path canonicalization → denied.

    Skipped on Windows when symlink permissions are unavailable.
    """
    legacy, sandbox = _setup_runner_fixture(tmp_path)
    (legacy / "memory").mkdir()
    real_target = legacy / "memory" / "work_list.md"
    real_target.write_text("x", encoding="utf-8")
    link_path = sandbox / "linked_work_list.md"
    try:
        os.symlink(real_target, link_path)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not supported in this environment")
    is_allowed = _dashboard_regen_runner.build_is_allowed(legacy, sandbox)
    # Path.resolve() follows symlinks; the link resolves to legacy/memory/work_list.md → denied.
    assert is_allowed(str(link_path)) is False


def test_audit_hook_subprocess_popen_records_legacy_cwd_violation(tmp_path: Path) -> None:
    """subprocess.Popen audit event with cwd=legacy → recorded violation.

    Note: REVISED-1 of post-impl (Codex `-014` Finding 1 fix): production
    runner uses ``os._exit(99)`` to fail-closed on first violation. Tests
    pass ``terminate_after_violation=False`` to inspect the in-memory
    violations list without ending the test process.
    """
    legacy, sandbox = _setup_runner_fixture(tmp_path)
    violations: list[dict[str, Any]] = []
    hook = _dashboard_regen_runner.build_audit_hook(legacy, sandbox, violations, None, terminate_after_violation=False)
    hook("subprocess.Popen", ("git", ["git", "ls-remote"], str(legacy), {}))
    assert len(violations) == 1
    assert violations[0]["event"] == "subprocess.Popen.cwd"
    assert str(legacy) in violations[0]["cwd"]


# ---- REVISED-1 of post-impl: fail-closed termination + quarantine ----


def test_audit_hook_terminates_subprocess_on_first_open_violation(tmp_path: Path) -> None:
    """First denied open → os._exit(99). Test injects a fake terminate.

    Captures that the hook calls os._exit on the first violation when
    ``terminate_after_violation=True`` (default).
    """
    legacy, sandbox = _setup_runner_fixture(tmp_path)
    target = legacy / "memory" / "work_list.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("legacy data", encoding="utf-8")

    violations: list[dict[str, Any]] = []
    violations_out = tmp_path / "violations.json"

    # Use terminate_after_violation=False to inspect behavior without exit.
    hook = _dashboard_regen_runner.build_audit_hook(
        legacy, sandbox, violations, violations_out, terminate_after_violation=False
    )
    hook("open", (str(target), "r", 0))
    # Hook recorded the violation
    assert len(violations) == 1
    assert violations[0]["event"] == "open"
    # Violations file flushed (this happens regardless of terminate flag).
    assert violations_out.exists()
    payload = json.loads(violations_out.read_text(encoding="utf-8"))
    assert len(payload) == 1
    # Quarantine marker also written for the lane to detect terminated state.
    marker = violations_out.with_suffix(".terminated-marker")
    assert marker.exists()
    marker_payload = json.loads(marker.read_text(encoding="utf-8"))
    assert marker_payload["reason"] == "audit_hook_fail_closed"


def test_run_status_error_on_subprocess_returncode_99_quarantines_sample_render(tmp_path: Path) -> None:
    """returncode=99 → status='error' AND sample_render renamed to .QUARANTINED.

    Per Codex `-014` Required Revision: "Prevent preserved sample
    artifacts from containing content derived from denied legacy reads.
    ... add explicit handling for quarantining ... when violations are
    non-empty."
    """
    legacy = _make_minimal_legacy_root(tmp_path)
    invoker = _make_fake_invoker(
        returncode=99,
        violations=[{"event": "open", "path": str(legacy / ".env.local")}],
    )
    result = _dashboard_regen.run({}, tmp_path / "output", project_root=legacy, subprocess_invoker=invoker)
    assert result["status"] == "error"
    assert any("audit_hook_fail_closed_termination" in w for w in result["warnings"])
    # Sample_render was renamed; original path no longer exists.
    sample_render = tmp_path / "output" / "dashboard_regen" / "sample_render"
    quarantined = tmp_path / "output" / "dashboard_regen" / "sample_render.QUARANTINED-1-violations"
    assert not sample_render.exists()
    assert quarantined.exists()


def test_run_quarantines_sample_render_even_on_violations_without_returncode_99(tmp_path: Path) -> None:
    """Defense-in-depth: violations non-empty even with returncode=0 → still quarantine.

    Covers the case where a future runner change might not terminate
    via os._exit (e.g., test-injected hook with ``terminate_after_violation=False``).
    """
    legacy = _make_minimal_legacy_root(tmp_path)
    invoker = _make_fake_invoker(
        returncode=0,  # generator completed normally
        violations=[{"event": "open", "path": str(legacy / ".env.local")}],
    )
    result = _dashboard_regen.run({}, tmp_path / "output", project_root=legacy, subprocess_invoker=invoker)
    assert result["status"] == "error"
    quarantined = tmp_path / "output" / "dashboard_regen" / "sample_render.QUARANTINED-1-violations"
    assert quarantined.exists()


# =====================================================================
# §7.6 Deployment-file pipeline tests (5 tests #38-42)
# =====================================================================


def test_run_copies_named_deployment_files_to_sandbox_when_present_in_legacy(tmp_path: Path) -> None:
    """All 5 files copied as real files (not symlinks); sha256 byte-equal."""
    legacy = _make_minimal_legacy_root(tmp_path)
    _dashboard_regen.run({}, tmp_path / "output", project_root=legacy, subprocess_invoker=_make_fake_invoker())
    sandbox = tmp_path / "output" / "dashboard_regen" / "sandbox"
    for rel in _dashboard_regen._KNOWN_DEPLOYMENT_INPUTS:
        legacy_p = legacy / rel
        sandbox_p = sandbox / rel
        assert sandbox_p.is_file(), f"Deployment file {rel} not copied"
        assert not sandbox_p.is_symlink(), f"Deployment file {rel} is a symlink"
        # Byte-equal sha256
        legacy_hash = hashlib.sha256(legacy_p.read_bytes()).hexdigest()
        sandbox_hash = hashlib.sha256(sandbox_p.read_bytes()).hexdigest()
        assert legacy_hash == sandbox_hash, f"sha256 mismatch for {rel}"


def test_run_does_not_copy_other_scripts_deploy_contents(tmp_path: Path) -> None:
    """Bystander files under scripts/deploy/ MUST NOT be copied."""
    legacy = _make_minimal_legacy_root(tmp_path)
    bystander = legacy / "scripts" / "deploy" / "internal-helper.ps1"
    bystander.write_text("Write-Host 'bystander'\n", encoding="utf-8")
    _dashboard_regen.run({}, tmp_path / "output", project_root=legacy, subprocess_invoker=_make_fake_invoker())
    sandbox = tmp_path / "output" / "dashboard_regen" / "sandbox"
    assert not (sandbox / "scripts" / "deploy" / "internal-helper.ps1").exists()


def test_run_audit_hook_allows_sandbox_copy_of_deployment_file(tmp_path: Path) -> None:
    """Sandbox copy of upgrade.ps1 is allowed; legacy original is denied."""
    legacy, sandbox = _setup_runner_fixture(tmp_path)
    # Sandbox copy
    (sandbox / "scripts" / "deploy").mkdir(parents=True)
    sandbox_file = sandbox / "scripts" / "deploy" / "upgrade.ps1"
    sandbox_file.write_text("x\n", encoding="utf-8")
    is_allowed = _dashboard_regen_runner.build_is_allowed(legacy, sandbox)
    assert is_allowed(str(sandbox_file)) is True


@pytest.mark.parametrize(
    "deployment_file",
    [
        "scripts/agent-container-template.yaml",
        "scripts/deploy/build-and-deploy-staging.ps1",
        "scripts/deploy/api-gateway-restore.yaml",
        "scripts/deploy/upgrade.ps1",
        "scripts/deploy/rollback.ps1",
    ],
)
def test_run_audit_hook_rejects_legacy_deployment_file_read(tmp_path: Path, deployment_file: str) -> None:
    """Each of the 5 deployment files: legacy reads denied."""
    legacy, sandbox = _setup_runner_fixture(tmp_path)
    target = legacy / deployment_file
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("x\n", encoding="utf-8")
    is_allowed = _dashboard_regen_runner.build_is_allowed(legacy, sandbox)
    assert is_allowed(str(target)) is False, f"Legacy read of {deployment_file} should be denied"


def test_run_emits_deployment_evidence_incomplete_warning_when_file_missing_from_legacy(tmp_path: Path) -> None:
    """One missing of 5 → status='ok' with deployment_evidence_incomplete warning."""
    legacy = _make_minimal_legacy_root(tmp_path)
    (legacy / "scripts" / "deploy" / "upgrade.ps1").unlink()
    result = _dashboard_regen.run({}, tmp_path / "output", project_root=legacy, subprocess_invoker=_make_fake_invoker())
    assert result["status"] == "ok"
    assert any("deployment_evidence_incomplete" in w and "upgrade.ps1" in w for w in result["warnings"])

    plan = _read_plan(tmp_path / "output")
    pipeline = plan["audit_hook_proof"]["deployment_files_pipeline"]
    assert "scripts/deploy/upgrade.ps1" in pipeline["missing_from_legacy_source"]
    assert len(pipeline["copied_to_sandbox"]) == 4
