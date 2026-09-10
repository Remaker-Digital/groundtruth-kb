from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from groundtruth_kb.inventory import (
    InventoryScanError,
    build_refresh_report,
    emit_markdown_ledger,
    load_match_file,
    scan_inventory_strings,
    string_scan,
)
from groundtruth_kb.project.registry_control_plane import load_registry_snapshot


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


def _artifact_toml(
    artifact_id: str,
    domain: str,
    lifecycle: str,
    storage_path: str,
    *,
    mutation_api: str = "approved test mutation",
) -> str:
    versioning = (
        "immutable_archive"
        if lifecycle == "archive"
        else "regenerated_from_source"
        if lifecycle == "generated"
        else "git_tracked"
    )
    backup = "regenerable_from_source" if lifecycle == "generated" else "git_tracked"
    coverage_mode = (
        "virtual"
        if ":" in storage_path
        else "glob"
        if any(character in storage_path for character in "*?[")
        else "recursive"
        if storage_path.endswith(("/", "\\"))
        else "exact"
    )
    restore = (
        "regenerate_from_source" if lifecycle == "generated" else "noop" if lifecycle == "archive" else "git_restore"
    )
    return f'''[[artifacts]]
id = "{artifact_id}"
domain = "{domain}"
lifecycle = "{lifecycle}"
storage_path = "{storage_path}"
authority_spec_id = "GOV-PLATFORM-SOT-REGISTRY-001"
coverage_mode = "{coverage_mode}"
mutation_api = "{mutation_api}"
versioning_policy = "{versioning}"
backup_policy = "{backup}"
restore_action = "{restore}"
health_check_function = ""
owner_role = "shared"
'''


def _validate_registry(root: Path) -> None:
    load_registry_snapshot(project_root=root)


def _write_project(root: Path) -> None:
    (root / "config" / "registry").mkdir(parents=True)
    (root / "docs").mkdir()
    (root / "runtime").mkdir()
    (root / "docs" / "rule.md").write_text("Legacy bridge/INDEX.md reference\n", encoding="utf-8")
    (root / "runtime" / "state.txt").write_text("runtime bridge/INDEX.md reference\n", encoding="utf-8")
    (root / "config" / "registry" / "sot-artifacts.toml").write_text(
        _artifact_toml("critical-rule", "narrative_authority", "active", "docs/rule.md")
        + "\n"
        + _artifact_toml("runtime-state", "runtime_state", "active", "runtime/*.txt"),
        encoding="utf-8",
    )
    _validate_registry(root)


def test_scan_inventory_strings_includes_gitignored_registered_artifact(tmp_path: Path) -> None:
    _write_project(tmp_path)
    registry = tmp_path / "config" / "registry" / "sot-artifacts.toml"
    registry.write_text(
        registry.read_text(encoding="utf-8")
        + "\n"
        + _artifact_toml("owner-local-env", "runtime_state", "active", ".env.local"),
        encoding="utf-8",
    )
    _validate_registry(tmp_path)
    (tmp_path / ".gitignore").write_text(".env.local\n", encoding="utf-8")
    (tmp_path / ".env.local").write_text("REGISTERED_LOCAL_SENTINEL\n", encoding="utf-8")
    _git(tmp_path, "init")
    _git(tmp_path, "add", ".gitignore", "config/registry/sot-artifacts.toml", "docs/rule.md", "runtime/state.txt")

    payload = scan_inventory_strings(tmp_path, ["REGISTERED_LOCAL_SENTINEL"])

    assert payload["summary"]["total_hits"] == 1
    assert payload["hits"][0]["path"] == ".env.local"
    assert payload["hits"][0]["artifact_id"] == "owner-local-env"


def test_scan_inventory_strings_reports_critical_and_warn_hits(tmp_path: Path) -> None:
    _write_project(tmp_path)

    payload = scan_inventory_strings(tmp_path, ["bridge/INDEX.md"])

    assert payload["mutated"] is False
    assert payload["summary"] == {"critical": 1, "total_hits": 2, "warn": 1}
    paths = {(hit["path"], hit["severity"], hit["remediation_status"]) for hit in payload["hits"]}
    assert ("docs/rule.md", "critical", "untriaged") in paths
    assert ("runtime/state.txt", "warn", "untriaged") in paths
    assert {hit["matched_string_id"] for hit in payload["hits"]} == {"M001"}


def test_scan_inventory_strings_accepts_path_and_class_overrides(tmp_path: Path) -> None:
    _write_project(tmp_path)

    payload = scan_inventory_strings(
        tmp_path,
        ["runtime"],
        critical_classes={"runtime_state"},
        warn_paths=("docs/*",),
    )

    assert payload["summary"]["critical"] == 1
    assert payload["hits"][0]["artifact_id"] == "runtime-state"


def test_match_file_supports_json_and_newline_lists(tmp_path: Path) -> None:
    json_file = tmp_path / "matches.json"
    json_file.write_text(json.dumps({"matches": ["one", "two"]}), encoding="utf-8")
    txt_file = tmp_path / "matches.txt"
    txt_file.write_text("# comment\nthree\n\nfour\n", encoding="utf-8")

    assert load_match_file(json_file) == ["one", "two"]
    assert load_match_file(txt_file) == ["three", "four"]


def test_scan_inventory_strings_requires_match_input(tmp_path: Path) -> None:
    _write_project(tmp_path)

    with pytest.raises(InventoryScanError, match="at least one"):
        scan_inventory_strings(tmp_path, [])


def test_markdown_ledger_groups_hits_by_severity(tmp_path: Path) -> None:
    _write_project(tmp_path)
    payload = scan_inventory_strings(tmp_path, ["bridge/INDEX.md"])

    ledger = emit_markdown_ledger(payload)

    assert "## Critical Hits" in ledger
    assert "## Warn Hits" in ledger
    assert "docs/rule.md:1:8 [M001]" in ledger


def test_refresh_uses_declared_coverage_for_generated_tree(tmp_path: Path) -> None:
    registry_dir = tmp_path / "config" / "registry"
    registry_dir.mkdir(parents=True)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "rule.md").write_text("canonical\n", encoding="utf-8")
    generated = tmp_path / "runtime-cache"
    generated.mkdir()
    for index in range(50):
        (generated / f"large-{index}.json").write_text("{}\n", encoding="utf-8")
    registry_dir.joinpath("sot-artifacts.toml").write_text(
        "\n".join(
            (
                _artifact_toml("specs", "specifications", "active", "membase:specifications"),
                _artifact_toml(
                    "dispatcher-task",
                    "runtime_state",
                    "active",
                    "windows-scheduled-task:GTKB-DispatcherDaemon",
                ),
                _artifact_toml("retired-index", "retired", "archive", "bridge/INDEX.md", mutation_api=""),
                _artifact_toml("generated-state", "runtime_state", "generated", "runtime-cache/"),
                _artifact_toml("docs-tree", "narrative_authority", "active", "docs/"),
                _artifact_toml("missing-active", "control_surface", "active", "config/missing.toml"),
            )
        ),
        encoding="utf-8",
    )
    _validate_registry(tmp_path)

    report = build_refresh_report(tmp_path)

    by_id = {item["artifact_id"]: item for item in report["artifact_statuses"]}
    assert report["mutated"] is False
    assert report["scanned_file_count"] == 51
    assert report["blocking"] is True
    assert report["summary"]["blocking_finding_count"] == 1
    assert report["summary"]["path_class_counts"] == {
        "archive": 1,
        "directory": 1,
        "external": 1,
        "file": 1,
        "generated": 1,
        "membase": 1,
    }
    assert by_id["generated-state"]["expanded_file_count"] == 50
    assert by_id["generated-state"]["status"] == "generated_present"
    assert by_id["dispatcher-task"]["status"] == "declared_external"
    assert by_id["retired-index"]["blocking"] is False
    assert by_id["missing-active"]["status"] == "missing_active_file"
    assert report["missing_artifacts"] == [by_id["missing-active"]]


def test_typed_registry_rejects_incomplete_records(tmp_path: Path) -> None:
    registry_dir = tmp_path / "config" / "registry"
    registry_dir.mkdir(parents=True)
    registry_dir.joinpath("sot-artifacts.toml").write_text(
        '[[artifacts]]\nid = "broken"\ndomain = "runtime_state"\n',
        encoding="utf-8",
    )
    with pytest.raises(InventoryScanError, match="missing required field"):
        build_refresh_report(tmp_path)


def test_public_inventory_reuses_snapshot_and_preserves_opaque_boundary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry = tmp_path / "config" / "registry" / "sot-artifacts.toml"
    registry.parent.mkdir(parents=True)
    opaque = _artifact_toml("runtime-opaque", "runtime_state", "active", "runtime-cache/").replace(
        'coverage_mode = "recursive"', 'coverage_mode = "opaque_container"'
    )
    registry.write_text(
        opaque + "\n" + _artifact_toml("missing-active", "control_surface", "active", "config/missing.toml"),
        encoding="utf-8",
    )
    disposable = tmp_path / "runtime-cache" / "disposable" / "scratch.txt"
    disposable.parent.mkdir(parents=True)
    disposable.write_text("must not be scanned\n", encoding="utf-8")
    _validate_registry(tmp_path)
    snapshot = load_registry_snapshot(project_root=tmp_path)

    def unexpected_reload(*_args, **_kwargs):
        raise AssertionError("public inventory reloaded an already-coherent snapshot")

    monkeypatch.setattr(string_scan, "load_registry_snapshot", unexpected_reload)
    artifacts, by_path, missing, expansions = string_scan.registered_artifact_inventory(tmp_path, snapshot=snapshot)

    assert {artifact.id for artifact in artifacts} == {"runtime-opaque", "missing-active"}
    assert by_path == {}
    assert [item["artifact_id"] for item in missing] == ["missing-active"]
    opaque_expansion = next(item for item in expansions if item.artifact.id == "runtime-opaque")
    assert opaque_expansion.path_class == "opaque_container"
    assert opaque_expansion.status == "opaque_present"
    assert opaque_expansion.files == ()
    assert string_scan._artifact_inventory is string_scan.registered_artifact_inventory


def _current_inventory(root: Path, *, lifecycle: str = "active", coverage: str = "exact", storage: str = "member"):
    declaration = root / "config/registry/sot-artifacts.toml"
    declaration.parent.mkdir(parents=True, exist_ok=True)
    text = _artifact_toml("member", "control_surface", lifecycle, storage)
    inferred = next(line for line in text.splitlines() if line.startswith("coverage_mode ="))
    declaration.write_text(text.replace(inferred, f'coverage_mode = "{coverage}"'), encoding="utf-8")
    return build_refresh_report(root)


@pytest.mark.parametrize("lifecycle", ["generated", "deprecated"])
def test_current_inventory_refuses_absent_nonactive_members(tmp_path: Path, lifecycle: str) -> None:
    report = _current_inventory(tmp_path, lifecycle=lifecycle)
    assert report["blocking"] is True
    assert report["scanned_file_count"] == 0


def test_current_inventory_does_not_read_archived_surface_that_still_exists(tmp_path: Path) -> None:
    (tmp_path / "member").write_text("must not be scanned", encoding="utf-8")
    report = _current_inventory(tmp_path, lifecycle="archive")
    assert report["blocking"] is True
    assert report["scanned_file_count"] == 0
    assert report["artifact_statuses"][0]["status"] == "archived_surface_present"


def test_current_inventory_exact_directory_does_not_cover_descendants(tmp_path: Path) -> None:
    directory = tmp_path / "member"
    directory.mkdir()
    (directory / "unregistered.py").write_text("must not be scanned", encoding="utf-8")
    report = _current_inventory(tmp_path)
    assert report["blocking"] is False
    assert report["scanned_file_count"] == 0


def test_current_inventory_accepts_opaque_file_without_scanning_payload(tmp_path: Path) -> None:
    (tmp_path / "member").write_bytes(b"service-owned payload")
    report = _current_inventory(tmp_path, coverage="opaque_container")
    assert report["blocking"] is False
    assert report["scanned_file_count"] == 0


@pytest.mark.parametrize("lifecycle", ["active", "generated", "deprecated"])
def test_current_inventory_expands_recursive_membership_independent_of_lifecycle(
    tmp_path: Path, lifecycle: str
) -> None:
    directory = tmp_path / "member/nested"
    directory.mkdir(parents=True)
    (directory / "one.py").write_text("declared descendant", encoding="utf-8")
    report = _current_inventory(tmp_path, lifecycle=lifecycle, coverage="recursive", storage="member/")
    assert report["blocking"] is False
    assert report["scanned_file_count"] == 1


def test_current_inventory_recursive_scan_does_not_follow_linked_directory(tmp_path: Path) -> None:
    outside = tmp_path.parent / (tmp_path.name + "-outside")
    outside.mkdir()
    (outside / "foreign.py").write_text("foreign content", encoding="utf-8")
    directory = tmp_path / "member"
    directory.mkdir()
    (directory / "own.py").write_text("own content", encoding="utf-8")
    linked = directory / "linked"
    if os.name == "nt":
        subprocess.run(["cmd", "/c", "mklink", "/J", str(linked), str(outside)], check=True, capture_output=True)
    else:
        linked.symlink_to(outside, target_is_directory=True)
    report = _current_inventory(tmp_path, coverage="recursive", storage="member/")
    assert report["blocking"] is False
    assert report["scanned_file_count"] == 1


def test_current_inventory_reports_unreadable_recursive_tree(tmp_path: Path, monkeypatch) -> None:
    directory = tmp_path / "member"
    directory.mkdir()
    original = Path.iterdir

    def unreadable(path):
        if path == directory:
            raise PermissionError("Unreadable registered tree")
        return original(path)

    monkeypatch.setattr(Path, "iterdir", unreadable)
    report = _current_inventory(tmp_path, coverage="recursive", storage="member/")
    assert report["blocking"] is True
    assert report["scanned_file_count"] == 0


@pytest.mark.parametrize(
    ("pattern", "expected"),
    [
        ("docs/*.md", {"docs/root.md"}),
        ("docs/**/*.md", {"docs/root.md", "docs/nested/leaf.md", "docs/nested/deep/end.md"}),
        ("docs/*/*.md", {"docs/nested/leaf.md"}),
        ("docs/**/l?af.[mt][dx]", {"docs/nested/leaf.md"}),
    ],
)
def test_glob_membership_and_inventory_have_the_same_path_scope(
    tmp_path: Path, pattern: str, expected: set[str]
) -> None:
    from groundtruth_kb.inventory.string_scan import registered_artifact_inventory

    paths = ("docs/root.md", "docs/nested/leaf.md", "docs/nested/deep/end.md", "docs/nested/other.txt")
    for relative in paths:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("current source", encoding="utf-8")
    registry = tmp_path / "config/registry/sot-artifacts.toml"
    registry.parent.mkdir(parents=True)
    registry.write_text(_artifact_toml("glob", "control_surface", "active", pattern), encoding="utf-8")
    snapshot = load_registry_snapshot(project_root=tmp_path)

    _records, by_path, missing, expansions = registered_artifact_inventory(tmp_path, snapshot=snapshot)

    assert not missing
    assert not expansions[0].blocking
    assert {path.relative_to(tmp_path).as_posix() for path in expansions[0].files} == expected
    assert {relative for relative in paths if snapshot.resolver.resolve(relative) is not None} == expected


def test_glob_inventory_does_not_follow_a_junction_in_its_pattern(tmp_path: Path) -> None:
    from groundtruth_kb.inventory.string_scan import registered_artifact_inventory

    current = tmp_path / "docs/current/source.md"
    current.parent.mkdir(parents=True)
    current.write_text("current source", encoding="utf-8")
    private = tmp_path / "private/payload.md"
    private.parent.mkdir()
    private.write_text("not a registered source", encoding="utf-8")
    linked = tmp_path / "docs/linked"
    if os.name == "nt":
        subprocess.run(["cmd", "/c", "mklink", "/J", str(linked), str(private.parent)], check=True, capture_output=True)
    else:
        linked.symlink_to(private.parent, target_is_directory=True)
    registry = tmp_path / "config/registry/sot-artifacts.toml"
    registry.parent.mkdir(parents=True)
    registry.write_text(_artifact_toml("glob", "control_surface", "active", "docs/*/*.md"), encoding="utf-8")

    _records, _by_path, missing, expansions = registered_artifact_inventory(tmp_path)

    assert not missing
    assert not expansions[0].blocking
    assert expansions[0].files == (current,)
    assert private.read_text(encoding="utf-8") == "not a registered source"


def test_glob_inventory_reports_unreadable_matching_directory(tmp_path: Path, monkeypatch) -> None:
    from groundtruth_kb.inventory.string_scan import registered_artifact_inventory

    source = tmp_path / "docs/current.md"
    source.parent.mkdir()
    source.write_text("current source", encoding="utf-8")
    registry = tmp_path / "config/registry/sot-artifacts.toml"
    registry.parent.mkdir(parents=True)
    registry.write_text(_artifact_toml("glob", "control_surface", "active", "docs/*.md"), encoding="utf-8")
    original = Path.iterdir

    def unreadable(path):
        if path == source.parent:
            raise PermissionError("glob source is unreadable")
        return original(path)

    monkeypatch.setattr(Path, "iterdir", unreadable)
    _records, _by_path, _missing, expansions = registered_artifact_inventory(tmp_path)

    assert expansions[0].blocking
    assert expansions[0].files == ()
    assert "glob source is unreadable" in expansions[0].detail
