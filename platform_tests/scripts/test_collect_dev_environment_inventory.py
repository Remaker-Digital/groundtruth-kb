"""Tests for the GT-KB development environment inventory collector."""

from __future__ import annotations

import importlib.util
import json
import sys
import types
from datetime import UTC, datetime
from pathlib import Path

import pytest
from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError

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
    for skill in ["zeta", "alpha"]:
        folder = root / ".harness-baseline-configuration/skills" / skill
        folder.mkdir(parents=True)
        (folder / "SKILL.md").write_text(f"# {skill}\n", encoding="utf-8")
    for path in ("rules/canonical-terminology.md", "hooks/credential-scan.py", "commands/check.md"):
        target = root / ".harness-baseline-configuration" / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# authored source\n", encoding="utf-8")
    (root / ".githooks").mkdir()
    (root / ".githooks" / "pre-commit").write_text("python -m groundtruth_kb secrets scan --staged\n", encoding="utf-8")
    (root / ".github" / "workflows").mkdir(parents=True)
    (root / ".github" / "workflows" / "python-tests.yml").write_text("name: tests\n", encoding="utf-8")


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
    monkeypatch.setattr(
        module,
        "_native_harness_records",
        lambda _root: [
            {"id": "A", "harness_name": "codex", "harness_type": "codex", "status": "active", "version": 1},
            {"id": "B", "harness_name": "claude", "harness_type": "claude", "status": "active", "version": 1},
            {"id": "G", "harness_name": "goose", "harness_type": "goose-desktop", "status": "suspended", "version": 1},
        ],
    )


def test_collector_writes_public_and_local_inventory(tmp_path, monkeypatch) -> None:
    module = _load_module()
    _make_project(tmp_path)
    _stub_toolchain(monkeypatch, module)

    result = module.write_inventory(
        tmp_path,
        public_json=tmp_path / module.PUBLIC_JSON_RELATIVE_PATH,
        public_markdown=tmp_path / module.PUBLIC_MARKDOWN_RELATIVE_PATH,
        local_json=tmp_path / "explicit-local" / "local.json",
        generated_at="2026-05-06T00:00:00Z",
    )

    public_path = tmp_path / module.PUBLIC_JSON_RELATIVE_PATH
    markdown_path = tmp_path / module.PUBLIC_MARKDOWN_RELATIVE_PATH
    local_path = tmp_path / "explicit-local" / "local.json"
    public = json.loads(public_path.read_text(encoding="utf-8"))
    assert public == result["public"]
    assert markdown_path.is_file()
    assert local_path.is_file()
    assert public["project"]["groundtruth_kb_package_version"] == "0.7.0rc1"
    assert public["repo_configured_surfaces"]["skills"]["items"] == [
        ".harness-baseline-configuration/skills/alpha/SKILL.md",
        ".harness-baseline-configuration/skills/zeta/SKILL.md",
    ]
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

    assert set(rows) == {
        (name, role) for name in ("codex", "claude", "goose") for role in ("prime-builder", "loyal-opposition")
    }
    assert all(row["qualification"] == "unqualified" and "assignment" not in row for row in rows.values())
    assert all(cap["status"] == "unavailable" for row in rows.values() for cap in row["capabilities"].values())
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
    assert first["repo_configured_surfaces"]["skills"]["items"] == [
        ".harness-baseline-configuration/skills/alpha/SKILL.md",
        ".harness-baseline-configuration/skills/zeta/SKILL.md",
    ]


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


def test_native_inventory_pages_exact_authority_and_ignores_private_role_fields(tmp_path, monkeypatch):
    module = _load_module()
    (tmp_path / "groundtruth.toml").write_text(
        '[groundtruth]\nauthority_url="http://127.0.0.1:65432"\n', encoding="utf-8"
    )
    calls = []
    records = [
        {
            "id": name,
            "harness_name": "codex",
            "harness_type": "codex",
            "version": 1,
            "status": "suspended",
            "role": "loyal-opposition",
            "invocation_env": {"key": "private-value"},
        }
        for name in ("A", "Z")
    ]

    def request(client, method, path, *, query):
        calls.append((client.url, method, path, query))
        index = 0 if query["after"] is None else 1
        return {"records": [records[index]], "next_after": "A" if index == 0 else None}

    monkeypatch.setattr(AuthorityClient, "request", request)
    inventory = module._harness_inventory(tmp_path)
    assert [row["id"] for row in inventory["installations"]] == ["A", "Z"]
    assert "private-value" not in json.dumps(inventory) and "role" not in json.dumps(inventory)
    assert [(call[0], call[1], call[2], call[3]["after"]) for call in calls] == [
        ("http://127.0.0.1:65432", "GET", "/v1/harnesses", None),
        ("http://127.0.0.1:65432", "GET", "/v1/harnesses", "A"),
    ]
    matrix = module._compatibility_matrix(inventory)
    assert len(matrix) == 8  # Both installations and missing Claude/Goose, each in both role scenarios.
    assert all(row["qualification"] == "unqualified" for row in matrix)


@pytest.mark.parametrize(
    "response", [[], {}, {"records": [{}], "next_after": None}, {"records": [], "next_after": "no-progress"}]
)
def test_invalid_native_inventory_response_cannot_become_a_partial_snapshot(tmp_path, monkeypatch, response):
    module = _load_module()
    (tmp_path / "groundtruth.toml").write_text(
        '[groundtruth]\nauthority_url="http://127.0.0.1:65432"\n', encoding="utf-8"
    )
    monkeypatch.setattr(AuthorityClient, "request", lambda *_args, **_kwargs: response)
    with pytest.raises(module.InventoryError):
        module._harness_inventory(tmp_path)


def test_unavailable_authority_does_not_read_old_harness_state_or_write_output(tmp_path, monkeypatch, capsys):
    module = _load_module()
    _make_project(tmp_path)
    config = tmp_path / "groundtruth.toml"
    config.write_text('[groundtruth]\nauthority_url="http://127.0.0.1:65432"\n', encoding="utf-8")
    legacy = tmp_path / "harness-state/harness-registry.json"
    legacy.parent.mkdir()
    legacy.write_text('{"harnesses":[{"id":"old","role":"prime-builder"}]}', encoding="utf-8")

    def refuse(*_args, **_kwargs):
        raise AuthorityClientError("authority_unavailable", "private diagnostic", details={"key": "private-value"})

    monkeypatch.setattr(AuthorityClient, "request", refuse)
    before = {str(path): path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()}
    assert module.main(["--project-root", str(tmp_path)]) == 1
    output = capsys.readouterr().out
    assert "native_harness_authority_unavailable" in output and "private" not in output
    assert before == {str(path): path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()}


def test_missing_root_configuration_never_discovers_a_parent_authority(tmp_path, monkeypatch):
    module = _load_module()
    (tmp_path / "groundtruth.toml").write_text(
        '[groundtruth]\nauthority_url="http://127.0.0.1:65432"\n', encoding="utf-8"
    )
    child = tmp_path / "child"
    child.mkdir()
    monkeypatch.setattr(AuthorityClient, "request", lambda *_args, **_kwargs: pytest.fail("unexpected authority read"))
    with pytest.raises(module.InventoryError, match="native_authority_not_configured"):
        module._harness_inventory(child)


def test_default_writer_emits_only_public_operational_outputs(tmp_path, monkeypatch):
    module = _load_module()
    _make_project(tmp_path)
    _stub_toolchain(monkeypatch, module)
    before = {path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*") if path.is_file()}
    assert module.main(["--project-root", str(tmp_path)]) == 0
    after = {path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*") if path.is_file()}
    assert after - before == {
        ".groundtruth/inventory/dev-environment-inventory.json",
        ".groundtruth/inventory/dev-environment-inventory.md",
    }


@pytest.mark.parametrize(
    "target",
    [
        ".gtkb-state/report.json",
        "harness-state/report.json",
        ".claude/report.json",
        ".harness-baseline-configuration/report.json",
    ],
)
def test_forbidden_output_is_refused_before_any_collection_or_write(tmp_path, monkeypatch, target):
    module = _load_module()
    monkeypatch.setattr(
        module, "collect_inventory", lambda *_args, **_kwargs: pytest.fail("collection before path check")
    )
    with pytest.raises(module.InventoryError, match="invalid_inventory_output_path"):
        module.write_inventory(
            tmp_path,
            public_json=tmp_path / "public.json",
            public_markdown=tmp_path / "public.md",
            local_json=tmp_path / target,
        )
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize(
    "defect", ["missing_primary", "missing_dimension", "invented_pass", "role_assignment", "old_schema"]
)
def test_validator_preserves_coverage_and_refuses_unmeasured_qualification(tmp_path, monkeypatch, defect):
    module = _load_module()
    _make_project(tmp_path)
    _stub_toolchain(monkeypatch, module)
    payload, _ = module.collect_inventory(tmp_path)
    if defect == "missing_primary":
        payload["role_by_harness_compatibility"] = [
            row for row in payload["role_by_harness_compatibility"] if row["harness"] != "goose"
        ]
    elif defect == "missing_dimension":
        del payload["role_by_harness_compatibility"][0]["capabilities"]["native_context_binding"]
    elif defect == "invented_pass":
        payload["role_by_harness_compatibility"][0]["capabilities"]["native_bridge_delivery"]["status"] = "verified"
    elif defect == "role_assignment":
        payload["harnesses"]["role_assignments"] = {"A": "prime-builder"}
    else:
        payload["schema_version"] = 1
    assert module.validate_public_inventory_payload(payload, project_root=tmp_path)


@pytest.mark.parametrize("section", ["redaction", "verification", "harnesses", "collector"])
def test_malformed_nested_inventory_returns_invalid_diagnostics(tmp_path, monkeypatch, section):
    module = _load_module()
    _make_project(tmp_path)
    _stub_toolchain(monkeypatch, module)
    payload, _ = module.collect_inventory(tmp_path)
    payload[section] = ["invalid"]
    assert module.validate_public_inventory_payload(payload)


@pytest.mark.parametrize("key", ["harness_id", "harness", "role"])
def test_malformed_qualification_identity_returns_a_validation_error(tmp_path, monkeypatch, key):
    module = _load_module()
    _make_project(tmp_path)
    _stub_toolchain(monkeypatch, module)
    payload, _ = module.collect_inventory(tmp_path)
    payload["role_by_harness_compatibility"][0][key] = ["invalid"]
    assert module.validate_public_inventory_payload(payload)
