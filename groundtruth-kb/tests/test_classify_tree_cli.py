"""CLI tests for ``gt project classify-tree`` (O-7 R27: deterministic inventory with findings, no owner-decision model).

Carries the retained duties of the SQLite-era cases: the command runs without `groundtruth.toml`, writes a
deterministic header block and ordered rows, offers JSON, and reports paths the ownership map does not cover as
findings. The retired model is not reasserted: `groundtruth.db` and the requirements files are undeclared findings,
never `legacy-exception` rows or fabricated owner-decision-pending counts.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from groundtruth_kb.cli import main


def _make_fixture(tmp_path: Path) -> Path:
    fixture = tmp_path / "tree"
    (fixture / ".claude" / "hooks").mkdir(parents=True)
    (fixture / "bridge").mkdir()
    (fixture / "memory").mkdir()
    (fixture / ".claude" / "hooks" / "destructive-gate.py").write_text("# managed hook body\n", encoding="utf-8")
    (fixture / "groundtruth.toml").write_text('[groundtruth]\nproject_root = "."\n', encoding="utf-8")
    (fixture / "groundtruth.db").write_bytes(b"retired local store")
    (fixture / "bridge" / "thread-001.md").write_text("# NEW\n", encoding="utf-8")
    (fixture / "memory" / "MEMORY.md").write_text("# notes\n", encoding="utf-8")
    (fixture / "requirements-local.txt").write_text("fastapi\n", encoding="utf-8")
    (fixture / "requirements-test.txt").write_text("pytest\n", encoding="utf-8")
    (fixture / "src").mkdir()
    (fixture / "src" / "app.py").write_text("value = 1\n", encoding="utf-8")
    return fixture


def _run(fixture: Path, output: Path, *extra: str):
    return CliRunner().invoke(
        main, ["project", "classify-tree", "--dir", str(fixture), "--output", str(output), *extra]
    )


def test_classify_tree_runs_without_groundtruth_toml(tmp_path: Path) -> None:
    fixture = _make_fixture(tmp_path)
    (fixture / "groundtruth.toml").unlink()
    output = tmp_path / "report.md"
    result = _run(fixture, output)
    assert result.exit_code == 0, result.output
    assert output.exists() and "paths classified" in result.output


def test_classify_tree_report_contains_header_block(tmp_path: Path) -> None:
    fixture = _make_fixture(tmp_path)
    output = tmp_path / "report.md"
    assert _run(fixture, output).exit_code == 0
    lines = output.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "# Tree classification report"
    assert any(line.startswith("- GT-KB version: ") for line in lines)
    assert any(line == f"- Target tree: {fixture.resolve()}" for line in lines)
    assert any(line.startswith("- Total paths classified: ") for line in lines)
    assert any(line.startswith("- Findings: ") and "undeclared" in line and "unreadable" in line for line in lines)
    assert "| path | ownership | upgrade_policy | divergence_policy | record | finding |" in lines


def test_classify_tree_reports_the_retired_local_store_as_undeclared(tmp_path: Path) -> None:
    fixture = _make_fixture(tmp_path)
    output = tmp_path / "report.md"
    assert _run(fixture, output).exit_code == 0
    content = output.read_text(encoding="utf-8")
    assert "legacy-exception" not in content and "owner_decision_pending" not in content
    row = next(line for line in content.splitlines() if line.startswith("| groundtruth.db |"))
    assert row.endswith("| undeclared |") and "__fallback__:groundtruth.db" in row


def test_classify_tree_reports_requirements_files_as_undeclared_findings(tmp_path: Path) -> None:
    fixture = _make_fixture(tmp_path)
    output = tmp_path / "report.md"
    assert _run(fixture, output).exit_code == 0
    rows = [line for line in output.read_text(encoding="utf-8").splitlines() if "| requirements-" in line]
    assert len(rows) == 2 and all(row.endswith("| undeclared |") for row in rows)


def test_classify_tree_findings_count_matches_rows(tmp_path: Path) -> None:
    fixture = _make_fixture(tmp_path)
    output = tmp_path / "report.md"
    assert _run(fixture, output).exit_code == 0
    content = output.read_text(encoding="utf-8")
    header = next(line for line in content.splitlines() if line.startswith("- Findings: "))
    undeclared = int(header.split("Findings: ")[1].split(" undeclared")[0])
    assert (
        undeclared
        == sum(1 for line in content.splitlines() if line.startswith("| ") and line.endswith("| undeclared |"))
        >= 4
    )
    managed = next(line for line in content.splitlines() if line.startswith("| .claude/hooks/destructive-gate.py |"))
    assert "| gt-kb-managed |" in managed and managed.endswith("|  |")


def test_classify_tree_json_format(tmp_path: Path) -> None:
    fixture = _make_fixture(tmp_path)
    output = tmp_path / "report.json"
    assert _run(fixture, output, "--format", "json").exit_code == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["report"] == "tree-classification" and payload["target_tree"] == str(fixture.resolve())
    assert payload["total_paths_classified"] == len(payload["rows"]) >= 7
    assert payload["findings"]["undeclared"] == sum(1 for row in payload["rows"] if row["finding"] == "undeclared")
    assert {row["path"] for row in payload["rows"] if row["finding"] == "undeclared"} >= {
        "groundtruth.db",
        "requirements-local.txt",
        "requirements-test.txt",
        "src/app.py",
    }
    assert all("owner_decision_pending" not in row for row in payload["rows"])
    # Report contract: rows are ordered by ownership (gt-kb-managed, gt-kb-scaffolded, shared-structured,
    # adopter-owned, legacy-exception) and then by path; the fixture mixes at least two ownerships.
    order = ["gt-kb-managed", "gt-kb-scaffolded", "shared-structured", "adopter-owned", "legacy-exception"]
    assert len({row["ownership"] for row in payload["rows"]}) >= 2, "the fixture must mix ownerships"
    expected = sorted(payload["rows"], key=lambda row: (order.index(row["ownership"]), row["path"]))
    assert [row["path"] for row in payload["rows"]] == [row["path"] for row in expected]
    assert payload["declaration_source"]["kind"] == "none"
    assert _run(fixture, tmp_path / "again.json", "--format", "json").exit_code == 0
    assert (tmp_path / "again.json").read_text(encoding="utf-8") == output.read_text(encoding="utf-8"), "deterministic"


def _registry_record(record_id: str, storage_path: str, coverage: str = "exact", lifecycle: str = "active") -> str:
    return (
        f'[[artifacts]]\nid = "{record_id}"\ndomain = "control_surface"\nlifecycle = "{lifecycle}"\n'
        f'storage_path = "{storage_path}"\ncoverage_mode = "{coverage}"\nauthority_spec_id = "GOV-X"\n'
        'mutation_api = "test fixture"\nversioning_policy = "git_tracked"\nbackup_policy = "git_tracked"\n'
        'health_check_function = ""\nowner_role = "shared"\n\n'
    )


def _write_platform_registry(fixture: Path, *records: str) -> None:
    registry = fixture / "config" / "registry" / "sot-artifacts.toml"
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(
        _registry_record("sot-registry-toml", "config/registry/sot-artifacts.toml") + "".join(records), encoding="utf-8"
    )


def _rows(payload: dict) -> dict[str, dict]:
    return {row["path"]: row for row in payload["rows"]}


def test_classify_tree_uses_the_targets_platform_declarations_before_the_template_map(tmp_path: Path) -> None:
    """A path declared in the selected root's registry is classified by that declaration, never as undeclared."""
    fixture = _make_fixture(tmp_path)
    _write_platform_registry(fixture, _registry_record("app-module", "src/app.py"))
    output = tmp_path / "report.json"
    assert _run(fixture, output, "--format", "json").exit_code == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["declaration_source"]["kind"] == "platform-registry"
    assert payload["declaration_source"]["path"] == "config/registry/sot-artifacts.toml"
    rows = _rows(payload)
    assert rows["src/app.py"]["record_id"] == "app-module" and rows["src/app.py"]["finding"] is None
    assert rows["src/app.py"]["ownership"] == "gt-kb-managed"
    assert rows["config/registry/sot-artifacts.toml"]["record_id"] == "sot-registry-toml"
    assert rows["requirements-local.txt"]["finding"] == "undeclared", "paths no declaration covers stay findings"


def test_classify_tree_reflects_a_changed_declaration_and_recursive_coverage(tmp_path: Path) -> None:
    fixture = _make_fixture(tmp_path)
    _write_platform_registry(fixture)
    first = tmp_path / "first.json"
    assert _run(fixture, first, "--format", "json").exit_code == 0
    assert _rows(json.loads(first.read_text(encoding="utf-8")))["src/app.py"]["finding"] == "undeclared"
    _write_platform_registry(fixture, _registry_record("sources", "src/", coverage="recursive", lifecycle="generated"))
    second = tmp_path / "second.json"
    assert _run(fixture, second, "--format", "json").exit_code == 0
    row = _rows(json.loads(second.read_text(encoding="utf-8")))["src/app.py"]
    assert row["record_id"] == "sources" and row["finding"] is None and row["upgrade_policy"] == "overwrite"


def test_classify_tree_distinguishes_two_targets_with_the_same_relative_filename(tmp_path: Path) -> None:
    platform = _make_fixture(tmp_path / "platform")
    (platform / "notes.md").write_text("platform notes\n", encoding="utf-8")
    _write_platform_registry(platform, _registry_record("notes", "notes.md"))
    application = tmp_path / "application"
    application.mkdir()
    (application / "notes.md").write_text("application notes\n", encoding="utf-8")
    (application / "data").mkdir()
    (application / "data" / "cache.json").write_text("{}", encoding="utf-8")
    (application / ".gtkb-app-isolation.json").write_text(
        json.dumps(
            {
                "schema_version": "2.0",
                "application": "application",
                "top_level_artifacts": [
                    {"name": "notes.md", "type": "FILE", "classification": "authoritative_input", "purpose": "Owned"},
                    {"name": "data", "type": "DIR", "classification": "runtime_data", "purpose": "Runtime cache"},
                ],
            }
        ),
        encoding="utf-8",
    )
    reports = {}
    for name, target in (("platform", platform), ("application", application)):
        output = tmp_path / f"{name}.json"
        assert _run(target, output, "--format", "json").exit_code == 0
        reports[name] = json.loads(output.read_text(encoding="utf-8"))
    assert reports["platform"]["declaration_source"]["kind"] == "platform-registry"
    assert reports["application"]["declaration_source"]["kind"] == "application-registry"
    platform_row = _rows(reports["platform"])["notes.md"]
    application_rows = _rows(reports["application"])
    assert platform_row["record_id"] == "notes" and platform_row["ownership"] == "gt-kb-managed"
    assert application_rows["notes.md"]["record_id"] == "application-registry:notes.md"
    assert application_rows["notes.md"]["ownership"] == "adopter-owned"
    assert application_rows["data/cache.json"]["record_id"] == "application-registry:data"
    assert application_rows["data/cache.json"]["upgrade_policy"] == "transient"
    assert application_rows[".gtkb-app-isolation.json"]["finding"] == "undeclared", (
        "the registry does not declare itself"
    )


def test_classify_tree_states_an_unavailable_declaration_source_instead_of_guessing(tmp_path: Path) -> None:
    fixture = _make_fixture(tmp_path)
    registry = fixture / "config" / "registry" / "sot-artifacts.toml"
    registry.parent.mkdir(parents=True)
    registry.write_text("[[artifacts]]\nid = 'broken'\n", encoding="utf-8")
    output = tmp_path / "report.md"
    assert _run(fixture, output).exit_code == 0
    text = output.read_text(encoding="utf-8")
    assert "- Declaration source: unavailable (config/registry/sot-artifacts.toml:" in text
    assert "| src/app.py | adopter-owned | preserve | — | __fallback__:src/app.py | undeclared |" in text
    # N-24: an unavailable source covers nothing and the packaged templates infer nothing — the template-known hook
    # is a finding as well, and the report lists the validator's finding.
    assert _HOOK_UNDECLARED_ROW in text
    assert "## Declaration findings" in text and "- registry_invalid: InvalidSoTRecord: " in text
    body = [line for line in text.splitlines() if line.startswith("| ") and not line.startswith("| path |")]
    assert body and all(line.endswith("| undeclared |") for line in body), "every row is a finding"


_HOOK = ".claude/hooks/destructive-gate.py"
_HOOK_UNDECLARED_ROW = f"| {_HOOK} | adopter-owned | preserve | — | __fallback__:{_HOOK} | undeclared |"


def test_classify_tree_reports_a_template_known_path_the_selected_root_does_not_declare(tmp_path: Path) -> None:
    """N-24 (a): a valid registry that does not declare the hook leaves it `undeclared`; the template is a hint only.

    GOV-PLATFORM-SOT-REGISTRY-001: a packaged copy cannot independently grant membership. Without any declaration
    file the same fixture classifies the hook from the template map (declaration source `none`); once the selected
    root carries a valid registry that omits the hook, the row is a finding and `hook.destructive-gate` is a hint.
    """
    fixture = _make_fixture(tmp_path)
    none = tmp_path / "none.json"
    assert _run(fixture, none, "--format", "json").exit_code == 0
    none_payload = json.loads(none.read_text(encoding="utf-8"))
    assert none_payload["declaration_source"]["kind"] == "none"
    assert _rows(none_payload)[_HOOK]["ownership"] == "gt-kb-managed"
    assert _rows(none_payload)[_HOOK]["finding"] is None and _rows(none_payload)[_HOOK]["template_hint"] is None

    _write_platform_registry(fixture, _registry_record("app-module", "src/app.py"))
    output = tmp_path / "report.json"
    assert _run(fixture, output, "--format", "json").exit_code == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["declaration_source"]["kind"] == "platform-registry"
    assert payload["declaration_source"]["declarations"] == 2 and payload["declaration_source"]["findings"] == []
    rows = _rows(payload)
    hook = rows[_HOOK]
    assert hook["finding"] == "undeclared" and hook["ownership"] == "adopter-owned"
    assert hook["upgrade_policy"] == "preserve" and hook["record_id"] == f"__fallback__:{_HOOK}"
    assert hook["template_hint"] == "hook.destructive-gate"
    assert "Template hint: hook.destructive-gate (gt-kb-managed, overwrite)" in hook["notes"]
    assert "grants no membership" in hook["notes"]
    declared = {path for path, row in rows.items() if row["finding"] is None}
    assert declared == {"config/registry/sot-artifacts.toml", "src/app.py"}
    assert all(rows[path]["template_hint"] is None for path in declared)
    assert rows["requirements-local.txt"]["template_hint"] is None, "no template knows this name"
    assert payload["findings"]["undeclared"] == len(rows) - 2

    markdown = tmp_path / "report.md"
    assert _run(fixture, markdown).exit_code == 0
    text = markdown.read_text(encoding="utf-8")
    assert _HOOK_UNDECLARED_ROW in text
    assert "## Template hints" in text and f"- {_HOOK}: hook.destructive-gate" in text
    assert "## Declaration findings" not in text


_VALID_ENTRIES = (
    {"name": "notes.md", "type": "FILE", "classification": "authoritative_input", "purpose": "Owned"},
    {"name": "data", "type": "DIR", "classification": "runtime_data", "purpose": "Runtime cache"},
)


def _application_registry(*entries: dict, **overrides: object) -> str:
    payload: dict[str, object] = {"schema_version": "2.0", "application": "application"}
    payload.update(overrides)
    payload = {key: value for key, value in payload.items() if value is not None}
    payload["top_level_artifacts"] = list(entries)
    return json.dumps(payload)


_INVALID_APPLICATION_DECLARATIONS = {
    "missing-application": (_application_registry(*_VALID_ENTRIES, application=None), "application_missing"),
    "mismatched-application": (_application_registry(*_VALID_ENTRIES, application="other"), "application_mismatch"),
    "unsupported-schema": (_application_registry(*_VALID_ENTRIES, schema_version="1.0"), "registry_schema_unsupported"),
    "duplicate-entry": (
        _application_registry(
            *_VALID_ENTRIES,
            {"name": "data", "type": "DIR", "classification": "authoritative_input", "purpose": "Duplicate"},
        ),
        "entry_duplicate",
    ),
    "missing-type": (
        _application_registry(
            _VALID_ENTRIES[1], {"name": "notes.md", "classification": "authoritative_input", "purpose": "Owned"}
        ),
        "entry_invalid_type",
    ),
    "missing-purpose": (
        _application_registry(_VALID_ENTRIES[0], {"name": "data", "type": "DIR", "classification": "runtime_data"}),
        "entry_missing_purpose",
    ),
    "unknown-classification": (
        _application_registry(
            _VALID_ENTRIES[0], {"name": "data", "type": "DIR", "classification": "mystery", "purpose": "Unknown"}
        ),
        "entry_invalid_classification",
    ),
    "duplicate-json-key": (
        '{"schema_version": "2.0", "application": "application", "application": "application", '
        '"top_level_artifacts": ' + json.dumps(list(_VALID_ENTRIES)) + "}",
        "registry_unreadable",
    ),
}


@pytest.mark.parametrize("case", sorted(_INVALID_APPLICATION_DECLARATIONS))
def test_classify_tree_rejects_invalid_application_declarations_without_defaulting(tmp_path: Path, case: str) -> None:
    """N-24 (b): an invalid `.gtkb-app-isolation.json` is `unavailable` with its findings; nothing defaults.

    DCL-APP-ROOT-MINIMIZATION-001: classification comes from the application's registry, and unclassified material is
    a boundary failure. The declaration reader is the application-boundary validator, so a duplicate entry, a missing
    `application`/`type`/`purpose`, an unsupported schema, an unknown classification or a duplicate JSON key leaves
    every walked path an `undeclared` finding — no entry wins by overwriting, no unknown classification becomes
    adopter-owned/preserve, and the template-known hook is not managed.
    """
    registry_text, expected_code = _INVALID_APPLICATION_DECLARATIONS[case]
    application = tmp_path / "application"
    (application / "data").mkdir(parents=True)
    (application / ".claude" / "hooks").mkdir(parents=True)
    (application / "notes.md").write_text("application notes\n", encoding="utf-8")
    (application / "data" / "cache.json").write_text("{}", encoding="utf-8")
    (application / ".claude" / "hooks" / "destructive-gate.py").write_text("# managed hook body\n", encoding="utf-8")
    (application / ".gtkb-app-isolation.json").write_text(registry_text, encoding="utf-8")

    output = tmp_path / "report.json"
    assert _run(application, output, "--format", "json").exit_code == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    source = payload["declaration_source"]
    assert source["kind"] == "unavailable" and source["path"] == ".gtkb-app-isolation.json"
    assert source["declarations"] == 0 and source["detail"].startswith(".gtkb-app-isolation.json: ")
    codes = [finding["code"] for finding in source["findings"]]
    assert expected_code in codes, codes
    assert all(finding["severity"] == "error" for finding in source["findings"])
    rows = _rows(payload)
    assert set(rows) == {".claude/hooks/destructive-gate.py", ".gtkb-app-isolation.json", "data/cache.json", "notes.md"}
    assert all(row["finding"] == "undeclared" for row in rows.values()), "no path defaults to a classification"
    assert not any(row["record_id"].startswith("application-registry:") for row in rows.values())
    cache = rows["data/cache.json"]
    assert cache["ownership"] == "adopter-owned" and cache["upgrade_policy"] == "preserve"
    assert rows[_HOOK]["ownership"] == "adopter-owned" and rows[_HOOK]["template_hint"] == "hook.destructive-gate"
    assert payload["findings"]["undeclared"] == len(rows) == 4

    markdown = tmp_path / "report.md"
    assert _run(application, markdown).exit_code == 0
    text = markdown.read_text(encoding="utf-8")
    assert "- Declaration source: unavailable (.gtkb-app-isolation.json: " in text
    assert "## Declaration findings" in text and f"- {expected_code}: " in text
    assert _HOOK_UNDECLARED_ROW in text


def test_classify_tree_accepts_the_validators_classifications_only(tmp_path: Path) -> None:
    """The application classification map covers exactly the validator's allowed set, so lookups never default."""
    from groundtruth_kb.isolation.app_root_minimization import ALLOWED_CLASSIFICATIONS
    from groundtruth_kb.project.ownership import _APPLICATION_CLASSIFICATIONS

    assert set(_APPLICATION_CLASSIFICATIONS) == set(ALLOWED_CLASSIFICATIONS)


def test_classify_tree_reports_a_path_the_walk_cannot_read(tmp_path: Path, monkeypatch) -> None:
    """The walk's error handler surfaces an unreadable directory as an `unreadable` finding (injected error)."""
    import os

    from groundtruth_kb.project import ownership

    fixture = _make_fixture(tmp_path)
    (fixture / "locked").mkdir()
    real_walk = os.walk

    def failing_walk(top, *args, **kwargs):
        onerror = kwargs.get("onerror")
        for dirpath, dirnames, filenames in real_walk(top, *args, **kwargs):
            if "locked" in dirnames and onerror is not None:
                dirnames.remove("locked")
                error = OSError(13, "Permission denied")
                error.filename = str(Path(dirpath) / "locked")
                onerror(error)
            yield dirpath, dirnames, filenames

    monkeypatch.setattr(ownership.os, "walk", failing_walk)
    output = tmp_path / "report.json"
    assert _run(fixture, output, "--format", "json").exit_code == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["findings"]["unreadable"] == 1
    assert _rows(payload)["locked"]["finding"] == "unreadable"


def test_classify_tree_reports_to_stdout_without_output(tmp_path: Path) -> None:
    fixture = _make_fixture(tmp_path)
    result = CliRunner().invoke(main, ["project", "classify-tree", "--dir", str(fixture), "--format", "json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["report"] == "tree-classification"
