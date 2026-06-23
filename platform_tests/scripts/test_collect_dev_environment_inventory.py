"""Tests for the GT-KB development environment inventory collector."""

from __future__ import annotations

import importlib.util
import json
import sys
import types
from datetime import UTC, datetime
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "collect_dev_environment_inventory.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("collect_dev_environment_inventory", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["collect_dev_environment_inventory"] = module
    spec.loader.exec_module(module)
    return module


def _make_project(root: Path) -> None:
    (root / "scripts").mkdir(parents=True)
    (root / "scripts" / "release_candidate_gate.py").write_text("# gate\n", encoding="utf-8")
    (root / "groundtruth-kb" / "src" / "groundtruth_kb").mkdir(parents=True)
    (root / "groundtruth-kb" / "src" / "groundtruth_kb" / "__init__.py").write_text(
        '__version__ = "0.7.0rc1"\n',
        encoding="utf-8",
    )
    (root / "groundtruth.toml").write_text(
        '[project]\nproject_name = "Synthetic"\nprofile = "dual-agent"\nscaffold_version = "0.7.0rc1"\n',
        encoding="utf-8",
    )
    (root / "harness-state").mkdir()
    (root / "harness-state" / "harness-identities.json").write_text(
        json.dumps({"harnesses": {"codex": {"id": "A"}, "claude": {"id": "B"}}}),
        encoding="utf-8",
    )
    (root / "harness-state" / "role-assignments.json").write_text(
        json.dumps(
            {
                "harnesses": {
                    "A": {"harness_type": "codex", "role": "prime-builder"},
                    "B": {"harness_type": "claude", "role": "loyal-opposition"},
                }
            }
        ),
        encoding="utf-8",
    )
    (root / ".codex" / "gtkb-hooks").mkdir(parents=True)
    (root / ".codex" / "config.toml").write_text("[features]\nhooks = true\n", encoding="utf-8")
    (root / ".codex" / "hooks.json").write_text(json.dumps({"hooks": {"SessionStart": []}}), encoding="utf-8")
    (root / ".codex" / "gtkb-hooks" / "session_start_dispatch.py").write_text("# hook\n", encoding="utf-8")
    (root / ".claude" / "rules").mkdir(parents=True)
    (root / ".claude" / "rules" / "canonical-terminology.md").write_text("# terms\n", encoding="utf-8")
    (root / ".claude" / "hooks").mkdir()
    (root / ".claude" / "hooks" / "formal-artifact-approval-gate.py").write_text("# gate\n", encoding="utf-8")
    (root / ".claude" / "hooks" / "credential-scan.py").write_text("# scan\n", encoding="utf-8")
    (root / ".claude" / "settings.json").write_text(json.dumps({"hooks": {"SessionStart": []}}), encoding="utf-8")
    for skill in ["zeta", "alpha"]:
        (root / ".claude" / "skills" / skill).mkdir(parents=True)
        (root / ".claude" / "skills" / skill / "SKILL.md").write_text(f"# {skill}\n", encoding="utf-8")
    (root / ".claude" / "commands").mkdir()
    (root / ".claude" / "commands" / "registry.json").write_text(
        json.dumps({"commands": {"check": {}}}),
        encoding="utf-8",
    )
    (root / ".githooks").mkdir()
    (root / ".githooks" / "pre-commit").write_text("python -m groundtruth_kb secrets scan --staged\n", encoding="utf-8")
    (root / ".github" / "workflows").mkdir(parents=True)
    (root / ".github" / "workflows" / "python-tests.yml").write_text("name: tests\n", encoding="utf-8")
    (root / "bridge").mkdir()
    (root / "bridge" / "INDEX.md").write_text("# Bridge Index\n", encoding="utf-8")


def _stub_toolchain(monkeypatch, module) -> None:
    public = {
        "python": {
            "command": "python --version",
            "status": "verified",
            "version": "3.12.0",
            "classification": "verified",
            "evidence": "test",
        }
    }
    private = {"python": {**public["python"], "resolved_executable": "python", "raw_output": "Python 3.12.0"}}
    monkeypatch.setattr(module, "_toolchain_inventory", lambda: (public, private))


def test_collector_writes_public_and_local_inventory(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _make_project(tmp_path)
    _stub_toolchain(monkeypatch, module)

    result = module.write_inventory(
        tmp_path,
        public_json=tmp_path / "docs" / "release" / "dev-environment-inventory.json",
        public_markdown=tmp_path / "docs" / "release" / "dev-environment-inventory.md",
        local_json=tmp_path / ".gtkb-state" / "dev-environment-inventory" / "local.json",
        generated_at="2026-05-06T00:00:00Z",
    )

    public_path = tmp_path / "docs" / "release" / "dev-environment-inventory.json"
    markdown_path = tmp_path / "docs" / "release" / "dev-environment-inventory.md"
    local_path = tmp_path / ".gtkb-state" / "dev-environment-inventory" / "local.json"
    public = json.loads(public_path.read_text(encoding="utf-8"))
    assert public == result["public"]
    assert markdown_path.is_file()
    assert local_path.is_file()
    assert public["project"]["groundtruth_kb_package_version"] == "0.7.0rc1"
    assert public["repo_configured_surfaces"]["skills"]["items"] == ["alpha", "zeta"]
    assert not module.validate_public_inventory_payload(
        public,
        project_root=tmp_path,
        max_age_hours=24,
        now=datetime(2026, 5, 6, 1, tzinfo=UTC),
    )


def test_public_inventory_redacts_sensitive_environment_values(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _make_project(tmp_path)
    _stub_toolchain(monkeypatch, module)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-testsecretvalue")

    public, private = module.collect_inventory(tmp_path, generated_at="2026-05-06T00:00:00Z")
    rendered_public = json.dumps(public, sort_keys=True)

    assert "OPENAI_API_KEY" not in rendered_public
    assert "sk-testsecretvalue" not in rendered_public
    assert public["redaction"]["sensitive_environment_entry_count"] >= 1
    local_entries = private["local_only"]["sensitive_environment_entries"]
    assert any(entry["key"] == "OPENAI_API_KEY" and entry["value"] == "<redacted>" for entry in local_entries)


def test_role_by_harness_matrix_has_all_required_rows_and_dimensions(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _make_project(tmp_path)
    _stub_toolchain(monkeypatch, module)

    public, _private = module.collect_inventory(tmp_path, generated_at="2026-05-06T00:00:00Z")
    rows = {(row["harness"], row["role"]): row for row in public["role_by_harness_compatibility"]}

    assert set(rows) == set(module.MATRIX_ROWS)
    for row in rows.values():
        assert set(module.CAPABILITY_DIMENSIONS) <= set(row["capabilities"])
        assert all(row["capabilities"][dimension]["evidence"] for dimension in module.CAPABILITY_DIMENSIONS)


def test_collector_output_is_deterministically_sorted(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _make_project(tmp_path)
    _stub_toolchain(monkeypatch, module)

    first, _ = module.collect_inventory(tmp_path, generated_at="2026-05-06T00:00:00Z")
    second, _ = module.collect_inventory(tmp_path, generated_at="2026-05-06T00:00:00Z")

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["repo_configured_surfaces"]["skills"]["items"] == ["alpha", "zeta"]


def test_public_validator_rejects_sensitive_values_absolute_paths_and_stale_inventory(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _make_project(tmp_path)
    _stub_toolchain(monkeypatch, module)
    public, _private = module.collect_inventory(tmp_path, generated_at="2026-05-01T00:00:00Z")
    public["leak"] = "sk-testsecretvalue"
    public["path_leak"] = "C:\\Users\\mike\\secret.txt"

    errors = module.validate_public_inventory_payload(
        public,
        project_root=tmp_path,
        max_age_hours=24,
        now=datetime(2026, 5, 6, tzinfo=UTC),
    )

    assert any("credential-shaped" in error for error in errors)
    assert any("absolute local path" in error for error in errors)
    assert any("stale" in error for error in errors)


def test_extract_version_path_safe_fallback_for_unstructured_output() -> None:
    """DELIB-2522 / Codex NO-GO -004 P1-002 path-safe fallback.

    When a tool's version probe fails (e.g., ``gh`` cannot read its config
    file) the captured first line is unstructured error text. If that text
    contains an absolute local path (Windows ``C:\\Users\\...`` or POSIX
    ``/Users/...``, ``/home/...``, ``/root/...``), the prior implementation
    truncated it to 80 chars and stored it in the public ``version`` field,
    which then tripped ``_validate_public_inventory``'s ``ABSOLUTE_PATH_RE``
    check and aborted the entire inventory write.

    The fix returns the ``fallback`` sentinel ("unknown" by default) for
    path-shaped fallbacks so the public payload remains writable. Failed
    tool diagnostic detail still reaches the private payload via
    ``raw_output``.
    """

    module = _load_module()

    # Windows-style path inside gh failure stderr.
    gh_failure = (
        "failed to create root command: failed to read configuration: "
        "open C:\\Users\\micha\\AppData\\Roaming\\gh\\config.yml"
    )
    assert module._extract_version(gh_failure) == "unknown"

    # POSIX-style path that the validator also rejects.
    posix_failure = "could not open /Users/example/.config/tool/config.yml"
    assert module._extract_version(posix_failure) == "unknown"

    # Non-version /home/ path failure (the validator rejects /home/ too).
    home_failure = "permission denied: /home/example/.config"
    assert module._extract_version(home_failure) == "unknown"

    # Sanity check: well-formed version strings still pass through untouched.
    assert module._extract_version("gh version 2.83.2 (2025-12-10)") == "2.83.2"
    assert module._extract_version("Python 3.14.0") == "3.14.0"

    # Sanity check: a non-version first line WITHOUT a path-shape still
    # returns the truncated first line (existing behavior preserved for
    # unstructured-but-path-safe outputs).
    assert module._extract_version("custom-tool: some diagnostic text") == "custom-tool: some diagnostic text"


def test_run_tool_version_public_evidence_is_stable_for_missing_executable(monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setattr(module.shutil, "which", lambda _executable: None)

    public, private = module._run_tool_version(["gh", "--version"], "gh --version")

    assert public == {
        "command": "gh --version",
        "status": "unsupported",
        "version": "unknown",
        "classification": "unsupported",
        "evidence": "gh --version",
    }
    assert private["resolved_executable"] is None
    assert private["returncode"] is None
    assert private["raw_output"] == ""


def test_run_tool_version_public_evidence_is_stable_for_execution_error(monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setattr(module.shutil, "which", lambda _executable: "C:\\Tools\\gh.exe")

    def fail_run(*_args, **_kwargs):
        raise OSError("config read failed")

    monkeypatch.setattr(module.subprocess, "run", fail_run)

    public, private = module._run_tool_version(["gh", "--version"], "gh --version")

    assert public == {
        "command": "gh --version",
        "status": "unknown",
        "version": "unknown",
        "classification": "unknown",
        "evidence": "gh --version",
    }
    assert private["resolved_executable"] == "C:\\Tools\\gh.exe"
    assert private["returncode"] is None
    assert private["raw_output"] == "config read failed"


def test_run_tool_version_public_evidence_is_stable_for_success_and_nonzero(monkeypatch) -> None:
    module = _load_module()
    results = iter(
        [
            types.SimpleNamespace(stdout="gh version 2.83.2\n", stderr="", returncode=0),
            types.SimpleNamespace(
                stdout="",
                stderr="failed to read configuration: open C:\\Users\\micha\\AppData\\Roaming\\gh\\config.yml",
                returncode=1,
            ),
        ]
    )
    monkeypatch.setattr(module.shutil, "which", lambda _executable: "C:\\Tools\\gh.exe")
    monkeypatch.setattr(module.subprocess, "run", lambda *_args, **_kwargs: next(results))

    success_public, success_private = module._run_tool_version(["gh", "--version"], "gh --version")
    failed_public, failed_private = module._run_tool_version(["gh", "--version"], "gh --version")

    assert success_public["status"] == "verified"
    assert success_public["version"] == "2.83.2"
    assert success_public["evidence"] == "gh --version"
    assert success_private["returncode"] == 0

    assert failed_public["status"] == "unknown"
    assert failed_public["version"] == "unknown"
    assert failed_public["evidence"] == "gh --version"
    assert failed_private["returncode"] == 1
