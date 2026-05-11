"""Tests for the GT-KB development environment inventory collector."""

from __future__ import annotations

import importlib.util
import json
import sys
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
    (root / ".codex" / "config.toml").write_text("[features]\ncodex_hooks = true\n", encoding="utf-8")
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
