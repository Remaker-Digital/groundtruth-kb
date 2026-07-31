from __future__ import annotations

import csv
import hashlib
import importlib.util
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.registry_control_plane import (
    apply_registry_transaction,
    serialize_registry,
)
from groundtruth_kb.project.sot_registry import (
    SoTArtifact,
    sync_projection,
)

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "gtkb_file_reference_migration.py"
FIXTURES = ROOT / "platform_tests" / "fixtures" / "file_reference_migration"


def _load_module():
    spec = importlib.util.spec_from_file_location("test_wi5640_migration", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write(path: Path, content: str = "content\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="")


def _registry_record(record_id: str, storage_path: str, coverage_mode: str) -> SoTArtifact:
    return SoTArtifact(
        id=record_id,
        domain="control_surface",
        lifecycle="active",
        storage_path=storage_path,
        authority_spec_id="GOV-PLATFORM-SOT-REGISTRY-001",
        mutation_api="fixture",
        versioning_policy="git_tracked",
        backup_policy="git_tracked",
        health_check_function="",
        owner_role="shared",
        restore_action="regenerate_from_source",
        coverage_mode=coverage_mode,
    )


def _seed_registry_authority(root: Path) -> None:
    records = [
        _registry_record("fixture-claude-tree", ".claude/", "recursive"),
        _registry_record("fixture-codex-tree", ".codex/", "recursive"),
        _registry_record("fixture-config-tree", "config/", "recursive"),
        _registry_record("fixture-cursor-tree", ".cursor/", "recursive"),
        _registry_record("fixture-runtime-state", ".gtkb-state/", "opaque_container"),
        _registry_record("fixture-packaged-tree", "groundtruth-kb/", "recursive"),
        _registry_record("fixture-database", "groundtruth.db", "exact"),
        _registry_record("fixture-manifest", "moves.csv", "exact"),
        _registry_record("fixture-policy", "policy.toml", "exact"),
        _registry_record("fixture-consumer", "consumer.py", "exact"),
    ]
    registry = root / "config" / "registry" / "sot-artifacts.toml"
    packaged = (
        root
        / "groundtruth-kb"
        / "src"
        / "groundtruth_kb"
        / "context"
        / "registries"
        / "v1"
        / "config"
        / "registry"
        / "sot-artifacts.toml"
    )
    registry.parent.mkdir(parents=True, exist_ok=True)
    packaged.parent.mkdir(parents=True, exist_ok=True)
    payload = serialize_registry(records)
    registry.write_bytes(payload)
    packaged.write_bytes(payload)
    db_path = root / "groundtruth.db"
    knowledge = KnowledgeDB(db_path=db_path)
    knowledge.close()
    sync_projection(records, db_path, changed_by="test", change_reason="fixture")
    apply_registry_transaction(
        records,
        operation="legacy_bootstrap",
        actor_session="test-session",
        changed_by="test/prime-builder",
        change_reason="WI-5441 migration fixture authority",
        start_packet_hash="sha256:test-start",
        pauth_id="PAUTH-WI5441-TEST",
        bridge_id="gtkb-wi5441-registry-control-plane-reverse-coverage",
        project_root=root,
    )


def _fixture(root: Path, *, sqlite_scans: bool = False) -> Path:
    manifest = root / "moves.csv"
    rows: list[tuple[str, str, str, str]] = []
    for index in range(33):
        rows.append(
            (str(root / ".claude/hooks"), f"hook-{index}.py", str(root / "config/hooks"), f"gtkb-hook-{index}.py")
        )
    for index in range(38):
        rows.append(
            (
                str(root / ".claude/rules"),
                f"rule-{index}.md",
                str(root / "config/agent-control"),
                f"gtkb-rule-{index}.md",
            )
        )
    for index in range(19):
        rows.append(
            (
                str(root / "config/agent-control"),
                f"agent-{index}.md",
                str(root / "config/agent-control"),
                f"gtkb-agent-{index}.md",
            )
        )
    with manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Current home directory:", "Current file name:", "New home directory:", "New file name:"])
        writer.writerows(rows)
    for home, name, new_home, new_name in rows:
        _write(Path(home) / name)
        _write(Path(new_home) / new_name)
    registry = root / "config/agent-control/gtkb-harness-capability-registry.toml"
    registry.write_text("capabilities = []\n", encoding="utf-8")
    (root / "config/agent-control/skill-rename-map.toml").write_text("skills = []\n", encoding="utf-8")
    policy = root / "policy.toml"
    lines = [
        "schema_version = 2",
        "test_fixture = true",
        'migration_id = "WI-5640"',
        'main_bridge_id = "gtkb-file-move-rename-canonicalization-v4"',
        'child_bridge_id = "gtkb-file-move-rename-canonicalization-v4-plan-approval"',
        'manifest_path = "moves.csv"',
        'runtime_directory = ".gtkb-state/file-reference-migration/wi5640"',
        'canonical_root = "."',
        "[alias_catalog]",
        'required_dispositions = ["rewrite", "generator-regenerate", "immutable-audit", "retained-compatibility", "external", "application-boundary", "unresolved"]',
        'candidate_only_origins = ["skill-inventory", "rename-metadata", "inferred-prefix"]',
        "[retention]",
        "retain_all_old_paths = true",
        "inert_source_count = 52",
        "native_rule_projection_count = 38",
        "allow_delete = false",
        "allow_move = false",
        "allow_rename = false",
        "allow_unlink = false",
        "[mutation]",
        'mutable_roots = [".claude", ".cursor", "config"]',
        'root_file_allowlist = ["consumer.py"]',
        'forbidden_roots = ["bridge"]',
        "[generator_execution]",
        "enabled_during_analysis = false",
        "[scan]",
        'inventory_mode = "filesystem"',
        'legacy_encodings = ["cp1252"]',
        "max_inline_text_bytes = 1048576",
        "inventory_excluded_children = true",
        "retain_observed_records = true",
        'catalog_probe_classifications = ["application_boundary", "binary", "canonical_destination", "generated_text", "immutable_audit", "input_authority", "mutable_text", "native_compatibility_projection", "retained_obsolete_source"]',
        "[[classification_rules]]",
        'id = "runtime"',
        'pattern = ".gtkb-state/file-reference-migration/wi5640/**"',
        'class = "runtime_non_authoritative"',
        "priority = 200",
        'comparison = "fixed_root"',
        "mutable = true",
        "[[classification_rules]]",
        'id = "git"',
        'pattern = ".git/**"',
        'class = "runtime_non_authoritative"',
        "priority = 190",
        'comparison = "fixed_root"',
        "mutable = false",
        "[[classification_rules]]",
        'id = "audit"',
        'pattern = "bridge/**"',
        'class = "immutable_audit"',
        "priority = 180",
        'comparison = "fixed_root"',
        "mutable = false",
    ]
    for generator_id in (
        "codex-skills",
        "antigravity-skills",
        "api-skills",
        "goose-api-skills",
        "goose-manifest",
        "cursor-skills",
        "rule-compatibility",
        "harness-parity",
    ):
        lines.extend(
            [
                "[[generator_checks]]",
                f'id = "{generator_id}"',
                'command = ["python", "noop.py", "--check"]',
                'owner = "noop.py"',
            ]
        )
    for index, (home, name, new_home, new_name) in enumerate(rows[:25], start=1):
        source = (Path(home) / name).relative_to(root).as_posix()
        destination = (Path(new_home) / new_name).relative_to(root).as_posix()
        lines.extend(
            [
                "[[content_reconciliation]]",
                f'mapping_id = "M{index:03d}"',
                f'source = "{source}"',
                f'destination = "{destination}"',
                'authority = "transformed_source"',
                'divergence = "newline_only"',
            ]
        )
    if sqlite_scans:
        lines.extend(
            [
                "[[sqlite_scans]]",
                'id = "current"',
                'path = "groundtruth.db"',
                'query = "SELECT id, value FROM refs ORDER BY id"',
                'identity_columns = ["id"]',
                'text_columns = ["value"]',
                "history = false",
                "[[sqlite_scans]]",
                'id = "history"',
                'path = "groundtruth.db"',
                'query = "SELECT id, value FROM history ORDER BY id"',
                'identity_columns = ["id"]',
                'text_columns = ["value"]',
                "history = true",
            ]
        )
    for index in range(38):
        lines.extend(
            [
                "[[rule_projections]]",
                f'source = ".claude/rules/rule-{index}.md"',
                f'canonical = "config/agent-control/gtkb-rule-{index}.md"',
                'class = "projection"',
                'load_policy = "explicit_query"',
            ]
        )
    policy.write_text("\n".join(lines) + "\n", encoding="utf-8")
    _seed_registry_authority(root)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    return policy


def test_manifest_validation_and_category_counts(tmp_path: Path) -> None:
    module = _load_module()
    policy_path = _fixture(tmp_path)
    _, policy = module.load_policy(tmp_path, policy_path)
    rows = module.load_manifest(tmp_path, policy)
    assert len(rows) == 90
    assert {kind: sum(row.category == kind for row in rows) for kind in ("hooks", "rules", "agent-control")} == {
        "hooks": 33,
        "rules": 38,
        "agent-control": 19,
    }


def test_direct_mixed_and_escaped_separators_rewrite_exactly() -> None:
    module = _load_module()
    mapping = module.MappingRow("M001", "hooks", ".claude/hooks/old.py", "config/hooks/gtkb-old.py")
    text = r"one=.claude/hooks/old.py two=.claude\\hooks\\old.py"
    rendered, matches = module.apply_direct_mappings(text, [mapping])
    assert rendered == r"one=config/hooks/gtkb-old.py two=config\\hooks\\gtkb-old.py"
    assert len(matches) == 2


def test_direct_match_has_component_boundary() -> None:
    module = _load_module()
    mapping = module.MappingRow("M001", "hooks", ".claude/hooks/old.py", "config/hooks/gtkb-old.py")
    rendered, matches = module.apply_direct_mappings(".claude/hooks/old.py.bak", [mapping])
    assert rendered == ".claude/hooks/old.py.bak"
    assert matches == []


def test_referrer_relative_bare_filename_is_resolved() -> None:
    module = _load_module()
    mapping = module.MappingRow("M001", "hooks", ".claude/hooks/old.py", "config/hooks/gtkb-old.py")
    rendered, matches = module.apply_referrer_relative_mappings(
        ".claude/hooks/caller.py", 'TARGET = "old.py"\n', [mapping]
    )
    assert rendered == 'TARGET = "../../config/hooks/gtkb-old.py"\n'
    assert matches[0][0] == mapping


def test_encoding_bom_and_newline_round_trip() -> None:
    module = _load_module()
    for raw, path in (
        (b"\xef\xbb\xbfhello\r\n", "a.md"),
        (b"\xff\xfeh\x00i\x00\r\x00\n\x00", "a.txt"),
        ("caf\u00e9\r\n".encode("cp1252"), "a.md"),
    ):
        decoded = module.decode_text(raw, path, ["cp1252"])
        assert decoded is not None
        assert module.encode_text(decoded, decoded.text) == raw


def test_unknown_extension_with_reference_bytes_blocks_instead_of_silent_skip(tmp_path: Path) -> None:
    module = _load_module()
    policy_path = _fixture(tmp_path)
    (tmp_path / "opaque.data").write_bytes(b"header\x00.claude/hooks/hook-0.py\x00tail")
    _, policy = module.load_policy(tmp_path, policy_path)
    mappings = module.load_manifest(tmp_path, policy)
    worktrees, _ = module.git_worktrees(tmp_path)
    _, _, _, blockers, _, _ = module.walk_inventory(tmp_path, policy, mappings, worktrees)
    assert any(
        item["code"] == "UNDECODED_REFERENCE_BYTES" and item["path"] == "opaque.data" and item["mapping_id"] == "M001"
        for item in blockers
    )


def test_static_python_and_powershell_path_construction() -> None:
    module = _load_module()
    python_values = module.python_static_paths('root = ".claude"\npath = Path(root) / "hooks" / "old.py"\n')
    assert any(value.endswith(".claude/hooks/old.py") for _, _, value in python_values)
    powershell_values = module.powershell_static_paths("$p = Join-Path '.claude' 'hooks/old.py'\n")
    assert powershell_values[0][2] == ".claude/hooks/old.py"


def test_reference_fixture_covers_direct_regex_glob_and_segmented_forms() -> None:
    module = _load_module()
    mapping = module.MappingRow("M001", "hooks", ".claude/hooks/old.py", "config/hooks/gtkb-old.py")
    text = (FIXTURES / "direct-forms.txt").read_text(encoding="utf-8")
    decoded = module.decode_text(text.encode(), "direct-forms.txt", ["cp1252"])
    assert decoded is not None
    record = module.InventoryRecord(
        "direct-forms.txt",
        "file",
        "mutable_text",
        "fixture",
        "full",
        len(text),
        0o644,
    )
    scanned = module.ScannedFile("direct-forms.txt", str(FIXTURES / "direct-forms.txt"), record, text.encode(), decoded)
    variants = {hit.variant for hit in module.scan_references({"direct-forms.txt": scanned}, [mapping])}
    assert {"direct", "regex_expression"}.issubset(variants)
    python_values = module.python_static_paths((FIXTURES / "segmented.py").read_text(encoding="utf-8"))
    assert any(value.endswith(".claude/hooks/old.py") for _, _, value in python_values)
    powershell_values = module.powershell_static_paths((FIXTURES / "segmented.ps1").read_text(encoding="utf-8"))
    assert powershell_values[0][2] == ".claude/hooks/old.py"


def test_plan_is_stable_when_runtime_observation_changes(tmp_path: Path) -> None:
    module = _load_module()
    policy = _fixture(tmp_path)
    first, first_residuals = module.analyze(tmp_path, policy)
    runtime_child = tmp_path / ".gtkb-state/file-reference-migration/wi5640/volatile.txt"
    _write(runtime_child, "first\n")
    second, second_residuals = module.analyze(tmp_path, policy)
    assert first.hashes["closure_inventory_sha256"] == second.hashes["closure_inventory_sha256"]
    assert first.hashes["closure_fingerprint"] == second.hashes["closure_fingerprint"]
    assert first.plan_sha256 == second.plan_sha256
    assert first.hashes["full_observation_sha256"] != second.hashes["full_observation_sha256"]
    assert first_residuals == second_residuals


def test_wildcard_fixed_roots_match_root_and_nested_directories() -> None:
    module = _load_module()
    assert module._pattern_matches("pytest-run", "**/pytest-*/**")
    assert module._pattern_matches("pytest-run/a.txt", "**/pytest-*/**")
    assert module._pattern_matches("foo/pytest-run", "**/pytest-*/**")
    assert module._pattern_matches("foo/pytest-run/a.txt", "**/pytest-*/**")
    assert not module._pattern_matches("foo/pytestish/a.txt", "**/pytest-*/**")
    assert module._fixed_root("pytest-run/a.txt", "**/pytest-*/**") == "pytest-run"
    assert module._fixed_root("foo/pytest-run/a.txt", "**/pytest-*/**") == "foo/pytest-run"
    assert (
        module._fixed_root(
            "harness-state/codex/session-envelopes/current.json",
            "harness-state/*/session-envelopes/**",
        )
        == "harness-state/codex/session-envelopes"
    )


def test_equivalent_same_priority_classifications_are_not_a_conflict() -> None:
    module = _load_module()
    rules = [
        module.ClassificationRule("venv", "**/.venv/**", "runtime_non_authoritative", 140, "fixed_root", False),
        module.ClassificationRule(
            "bytecode", "**/__pycache__/**", "runtime_non_authoritative", 140, "fixed_root", False
        ),
    ]
    selected, error = module._policy_classification("project/.venv/pkg/__pycache__/x.pyc", rules)
    assert error is None
    assert selected is not None
    assert selected.classification == "runtime_non_authoritative"


def test_excluded_fixed_root_descendants_are_observed_without_becoming_mutable(tmp_path: Path) -> None:
    module = _load_module()
    policy_path = _fixture(tmp_path)
    _write(tmp_path / "bridge/history/old.md", ".claude/hooks/hook-0.py\n")
    _, policy = module.load_policy(tmp_path, policy_path)
    mappings = module.load_manifest(tmp_path, policy)
    catalog, _ = module.load_obsolete_catalog(tmp_path, policy, mappings)
    worktrees, _ = module.git_worktrees(tmp_path)
    inventory, closure, files, blockers, _, _ = module.walk_inventory(tmp_path, policy, mappings, worktrees)
    assert not blockers
    assert "bridge/history/old.md" not in files
    observed = next(item for item in inventory if item.path == "bridge/history/old.md")
    assert observed.classification == "immutable_audit"
    assert any(item["path"] == "bridge" and item["classification"] == "immutable_audit" for item in closure)
    occurrences, probe_blockers = module.scan_catalog_occurrences(tmp_path, policy, catalog, inventory)
    assert not probe_blockers
    occurrence = next(item for item in occurrences if item.path == "bridge/history/old.md")
    assert occurrence.disposition == "immutable-audit"
    assert occurrence.load_bearing is False


def test_policy_rejects_disabled_full_root_inventory(tmp_path: Path) -> None:
    module = _load_module()
    policy_path = _fixture(tmp_path)
    policy_text = policy_path.read_text(encoding="utf-8").replace(
        "inventory_excluded_children = true",
        "inventory_excluded_children = false",
    )
    policy_path.write_text(policy_text, encoding="utf-8")
    _, policy = module.load_policy(tmp_path, policy_path)
    mappings = module.load_manifest(tmp_path, policy)
    with pytest.raises(module.MigrationError, match="excluded-root descendants remain observable") as exc_info:
        module.validate_policy_contract(policy, mappings)
    assert exc_info.value.code == "FULL_ROOT_INVENTORY_DISABLED"


def test_artifact_registry_is_the_exclusive_inventory_authority(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _load_module()
    policy_path = _fixture(tmp_path)
    _write(tmp_path / "registered.txt", ".claude/hooks/hook-0.py\n")
    _write(tmp_path / "disposable.txt", ".claude/hooks/hook-0.py\n")
    _, policy = module.load_policy(tmp_path, policy_path)
    policy["scan"]["inventory_mode"] = "artifact-registry"
    mappings = module.load_manifest(tmp_path, policy)
    monkeypatch.setattr(module, "registered_artifact_paths", lambda _root: ({"registered.txt"}, []))
    worktrees, _ = module.git_worktrees(tmp_path)
    inventory, _closure, files, blockers, _observation, _count = module.walk_inventory(
        tmp_path, policy, mappings, worktrees
    )
    assert {item.path for item in inventory} == {"registered.txt"}
    assert set(files) == {"registered.txt"}
    assert any(item["code"] == "MANIFEST_DESTINATION_UNREGISTERED" for item in blockers)
    assert not any(item.get("path") == "disposable.txt" for item in blockers)


def test_unreadable_directory_is_a_blocker(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    policy_path = _fixture(tmp_path)
    blocked = tmp_path / "blocked"
    blocked.mkdir()
    real_scandir = module.os.scandir

    def refusing_scandir(path):
        if os.fspath(path).replace("\\", "/").endswith("/blocked"):
            raise PermissionError("fixture denied")
        return real_scandir(path)

    monkeypatch.setattr(module.os, "scandir", refusing_scandir)
    _, policy = module.load_policy(tmp_path, policy_path)
    mappings = module.load_manifest(tmp_path, policy)
    worktrees, _ = module.git_worktrees(tmp_path)
    _, _, _, blockers, _, _ = module.walk_inventory(tmp_path, policy, mappings, worktrees)
    assert any(item["code"] == "UNREADABLE_DIRECTORY" and item["path"] == "blocked" for item in blockers)


def test_sqlite_current_is_blocking_and_history_is_exception(tmp_path: Path) -> None:
    module = _load_module()
    policy_path = _fixture(tmp_path, sqlite_scans=True)
    database = sqlite3.connect(tmp_path / "groundtruth.db")
    database.execute("CREATE TABLE refs(id INTEGER PRIMARY KEY, value TEXT)")
    database.execute("CREATE TABLE history(id INTEGER PRIMARY KEY, value TEXT)")
    database.execute("INSERT INTO refs VALUES(1, '.claude/hooks/hook-0.py')")
    database.execute("INSERT INTO history VALUES(1, '.claude/hooks/hook-0.py')")
    database.commit()
    database.close()
    _, policy = module.load_policy(tmp_path, policy_path)
    mappings = module.load_manifest(tmp_path, policy)
    hits, blockers = module.scan_sqlite(tmp_path, policy, mappings)
    assert not blockers and len(hits) == 2
    assert {item["history"] for item in hits} == {False, True}


def test_literal_windows_like_names_are_inventoried(tmp_path: Path) -> None:
    module = _load_module()
    policy_path = _fixture(tmp_path)
    for name in ("CON", "$null", "list[str]", "-p"):
        with open(module._native_path(tmp_path / name), "wb") as handle:
            handle.write(b"literal\n")
    _, policy = module.load_policy(tmp_path, policy_path)
    mappings = module.load_manifest(tmp_path, policy)
    worktrees, _ = module.git_worktrees(tmp_path)
    inventory, _, _, blockers, _, _ = module.walk_inventory(tmp_path, policy, mappings, worktrees)
    assert not blockers
    assert {"CON", "$null", "list[str]", "-p"}.issubset({item.path for item in inventory})


def test_apply_fails_on_missing_child_before_any_write(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    policy = _fixture(tmp_path)
    analysis, residuals = module.analyze(tmp_path, policy)
    _, report = module.publish_evidence(analysis, residuals, "plan")
    monkeypatch.setenv("CODEX_THREAD_ID", "test-session")
    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID", raising=False)
    monkeypatch.delenv("GTKB_SESSION_CONTEXT_ID", raising=False)
    plan_path = tmp_path / ".gtkb-state/file-reference-migration/wi5640/plan.json"
    before = {
        write.path: (tmp_path / write.path).read_bytes() if (tmp_path / write.path).is_file() else None
        for write in analysis.writes
    }
    with pytest.raises(module.MigrationError, match="Strict child lifecycle") as exc:
        module.apply_plan(tmp_path, plan_path, policy, session_id="test-session")
    assert exc.value.code == "CHILD_LIFECYCLE_INVALID"
    after = {
        write.path: (tmp_path / write.path).read_bytes() if (tmp_path / write.path).is_file() else None
        for write in analysis.writes
    }
    assert before == after


def test_retained_sources_never_enter_write_set(tmp_path: Path) -> None:
    module = _load_module()
    policy = _fixture(tmp_path)
    consumer = tmp_path / "consumer.py"
    _write(consumer, 'PATH = ".claude/hooks/hook-0.py"\n')
    analysis, _ = module.analyze(tmp_path, policy)
    write_set = {item.path for item in analysis.writes}
    assert "consumer.py" in write_set
    assert not any(path.startswith(".claude/hooks/") for path in write_set)
    assert not any(
        path.startswith(".claude/rules/")
        for path in write_set
        if "generator:rule-compatibility" not in next(item for item in analysis.writes if item.path == path).reasons
    )


def test_mutation_policy_blocks_unlisted_root_file(tmp_path: Path) -> None:
    module = _load_module()
    policy = _fixture(tmp_path)
    policy.write_text(
        policy.read_text(encoding="utf-8").replace('root_file_allowlist = ["consumer.py"]', "root_file_allowlist = []"),
        encoding="utf-8",
    )
    _write(tmp_path / "consumer.py", 'PATH = ".claude/hooks/hook-0.py"\n')
    analysis, _ = module.analyze(tmp_path, policy)
    assert "consumer.py" not in {item.path for item in analysis.writes}
    assert any(
        item["code"] == "WRITE_OUTSIDE_MUTATION_POLICY" and item["path"] == "consumer.py" for item in analysis.blockers
    )


def test_native_rule_projection_is_an_allowed_generated_write(tmp_path: Path) -> None:
    module = _load_module()
    policy = _fixture(tmp_path)
    projection = tmp_path / ".claude/rules/rule-0.md"
    projection.write_text("manual drift\n", encoding="utf-8")
    analysis, _ = module.analyze(tmp_path, policy)
    write = next(item for item in analysis.writes if item.path == ".claude/rules/rule-0.md")
    assert "generator:rule-compatibility" in write.reasons


def test_rollback_prevalidates_all_paths_before_mutation(tmp_path: Path) -> None:
    module = _load_module()
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_bytes(b"post-one")
    second.write_bytes(b"concurrent")
    pre_one = tmp_path / "pre-one.bin"
    pre_two = tmp_path / "pre-two.bin"
    post_one = tmp_path / "post-one.bin"
    post_two = tmp_path / "post-two.bin"
    pre_one.write_bytes(b"pre-one")
    pre_two.write_bytes(b"pre-two")
    post_one.write_bytes(b"post-one")
    post_two.write_bytes(b"post-two")
    writes = [
        {
            "path": "first.txt",
            "preimage_sha256": module.sha256_bytes(b"pre-one"),
            "postimage_sha256": module.sha256_bytes(b"post-one"),
            "preimage_payload": "pre-one.bin",
            "payload": "post-one.bin",
            "mode": 0o644,
        },
        {
            "path": "second.txt",
            "preimage_sha256": module.sha256_bytes(b"pre-two"),
            "postimage_sha256": module.sha256_bytes(b"post-two"),
            "preimage_payload": "pre-two.bin",
            "payload": "post-two.bin",
            "mode": 0o644,
        },
    ]
    outcomes = module._rollback_applied(tmp_path, writes, ["first.txt", "second.txt"])
    assert any(item["status"] == "concurrent_postimage_drift" for item in outcomes)
    assert first.read_bytes() == b"post-one"


def _alias_entry(module, *, entry_id: str = "A900", authority: str = "rewrite"):
    return module.CatalogEntry(
        entry_id,
        ".claude/skills/" + "bridge-propose",
        ".claude/skills/" + "gtkb-bridge-propose",
        "test-explicit" if authority == "rewrite" else "test-inferred",
        authority,
        "longest-path-components",
        ("direct", "structured", "sqlite"),
        True,
        authority == "candidate-only",
    )


def test_catalog_rejects_multiple_targets_and_nfc_casefold_collisions() -> None:
    module = _load_module()
    first = _alias_entry(module)
    second = module.CatalogEntry(
        "A901",
        first.source.upper(),
        ".claude/skills/different",
        "test",
        "rewrite",
        "longest-path-components",
        ("direct",),
        True,
    )
    with pytest.raises(module.MigrationError, match="maps to both"):
        module._catalog_collision_check([first, second])


def test_component_alias_matching_ignores_capability_ids_runtime_names_and_prose(tmp_path: Path) -> None:
    module = _load_module()
    entry = _alias_entry(module)
    policy = {
        "scan": {
            "max_catalog_probe_bytes": 1024 * 1024,
            "catalog_probe_classifications": ["mutable_text"],
        }
    }
    path = tmp_path / "consumer.txt"
    _write(
        path,
        "skill.bridge-propose\n.gtkb-state/bridge-propose-drafts\nbridge-propose prose\n"
        "load=.claude/skills/bridge-propose/SKILL.md\n",
    )
    record = module.InventoryRecord("consumer.txt", "file", "mutable_text", "test", "full", path.stat().st_size, 0o644)
    occurrences, blockers = module.scan_catalog_occurrences(tmp_path, policy, [entry], [record])
    assert not blockers
    assert len(occurrences) == 1
    assert occurrences[0].token.replace("\\", "/") == entry.source


def test_structured_json_toml_yaml_locations_are_typed(tmp_path: Path) -> None:
    module = _load_module()
    entry = _alias_entry(module)
    files: dict[str, object] = {}
    samples = {
        "sample.json": '{"path":".claude/skills/bridge-propose/SKILL.md"}\n',
        "sample.toml": 'path = ".claude/skills/bridge-propose/SKILL.md"\n',
        "sample.yaml": 'path: ".claude/skills/bridge-propose/SKILL.md"\n',
    }
    for name, text in samples.items():
        path = tmp_path / name
        _write(path, text)
        raw = path.read_bytes()
        decoded = module.decode_text(raw, name, [])
        record = module.InventoryRecord(name, "file", "mutable_text", "test", "full", len(raw), 0o644)
        files[name] = module.ScannedFile(name, str(path), record, raw, decoded)
    locations, blockers = module.scan_structured_occurrences(files, [entry])
    assert not blockers
    assert {(item.format, item.node_path) for item in locations} == {
        ("json", "/path"),
        ("toml", "/path"),
        ("yaml", "/0/path"),
    }


@pytest.mark.parametrize("suffix", [".zip", ".whl"])
def test_zip_member_name_and_bytes_are_scanned_without_extraction(tmp_path: Path, suffix: str) -> None:
    module = _load_module()
    entry = _alias_entry(module)
    archive = tmp_path / f"fixture{suffix}"
    import zipfile

    with zipfile.ZipFile(archive, "w") as handle:
        handle.writestr(".claude/skills/bridge-propose/SKILL.md", b"x")
        handle.writestr("payload.txt", b".claude/skills/bridge-propose/helpers/run.py")
    record = module.InventoryRecord(
        archive.name, "file", "mutable_candidate", "test", "full", archive.stat().st_size, 0o644
    )
    occurrences, blockers = module.scan_zip_occurrences(tmp_path, [entry], [record])
    assert not blockers
    assert {item.location.split(":")[-2] for item in occurrences} == {"member-name", "member-bytes"}


def test_catalog_probe_skips_vanishing_sqlite_wal_and_shm_sidecars(tmp_path: Path) -> None:
    module = _load_module()
    assert module._builtin_classification("groundtruth.db-wal", "file", {}, {}, set()) == (
        "runtime_non_authoritative",
        "builtin-sqlite-sidecar",
        "full",
    )
    records = [
        module.InventoryRecord(name, "file", "runtime_non_authoritative", "test", "full", 1, 0o644)
        for name in ("groundtruth.db-wal", "groundtruth.db-shm")
    ]
    occurrences, blockers = module.scan_catalog_occurrences(
        tmp_path,
        {"scan": {"max_catalog_probe_bytes": 1024, "catalog_probe_classifications": ["mutable_text"]}},
        [_alias_entry(module)],
        records,
    )
    assert not occurrences
    assert not blockers


def test_physical_alias_inventory_declares_retained_copy_and_generator_operations(tmp_path: Path) -> None:
    module = _load_module()
    source = tmp_path / "templates/skills/bridge-propose/SKILL.md"
    fixture = tmp_path / "fixtures/skills/bridge-propose/SKILL.md"
    _write(source, "template\n")
    _write(fixture, "fixture\n")
    inventory = [
        module.InventoryRecord(
            path.relative_to(tmp_path).as_posix(),
            "file",
            "mutable_text",
            "test",
            "full",
            path.stat().st_size,
            0o644,
            sha256=module.sha256_bytes(path.read_bytes()),
        )
        for path in (source, fixture)
    ]
    policy = {
        "physical_alias_roots": [
            {
                "id": "PA001",
                "alias_id": "A900",
                "source": "templates/skills/bridge-propose",
                "canonical": "templates/skills/gtkb-bridge-propose",
                "disposition": "rewrite",
                "operation": "materialize-copy",
                "owner": "engine",
                "retain_source": True,
            },
            {
                "id": "PA002",
                "alias_id": "A900",
                "source": "fixtures/skills/bridge-propose",
                "canonical": "fixtures/skills/gtkb-bridge-propose",
                "disposition": "generator-regenerate",
                "operation": "generator-regenerate",
                "owner": "capture",
                "retain_source": True,
            },
        ]
    }
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    physical, operations, blockers = module.build_physical_inventory(
        tmp_path, policy, [_alias_entry(module)], inventory
    )
    assert not blockers
    assert {item.operation_type for item in operations} == {"materialize-copy", "generator-regenerate"}
    assert all(item.destination_state == "absent" for item in physical)
    assert all(item.source_path.endswith("SKILL.md") for item in physical)


def test_journal_is_hash_chained_durable_and_tamper_evident(tmp_path: Path) -> None:
    module = _load_module()
    journal = module.TransactionJournal.create(tmp_path, "tx-test", {"plan_sha256": "sha256:" + "1" * 64})
    journal.append("write_intent", {"path": "target.txt"})
    loaded = module.TransactionJournal.load(tmp_path, "tx-test")
    assert [item["sequence"] for item in loaded.records] == [0, 1]
    raw = journal.path.read_bytes()
    journal.path.write_bytes(raw.replace(b"target.txt", b"tamper.txt"))
    with pytest.raises(module.MigrationError, match="hash"):
        module.TransactionJournal.load(tmp_path, "tx-test")


def test_journal_truncation_and_reordering_fail_closed(tmp_path: Path) -> None:
    module = _load_module()
    journal = module.TransactionJournal.create(tmp_path, "tx-test", {"x": 1})
    journal.append("write_intent", {"x": 2})
    lines = journal.path.read_bytes().splitlines(keepends=True)
    journal.path.write_bytes(lines[1] + lines[0])
    with pytest.raises(module.MigrationError, match="sequence/hash link"):
        module.TransactionJournal.load(tmp_path, "tx-test")
    journal.path.write_bytes(lines[0].rstrip(b"\n"))
    with pytest.raises(module.MigrationError, match="terminal LF"):
        module.TransactionJournal.load(tmp_path, "tx-test")


def test_nonterminal_operation_retains_lock_until_explicit_terminal_recovery(tmp_path: Path) -> None:
    module = _load_module()
    journal = module.TransactionJournal.create(tmp_path, "tx-test", {"mode": "apply"})
    with pytest.raises(RuntimeError, match="crash"), module._operation_lock(tmp_path, journal):
        raise RuntimeError("crash")
    lock = tmp_path / module._LOCK_RELATIVE
    assert lock.is_file()
    with pytest.raises(module.MigrationError, match="run the explicit recover command"):
        module._assert_no_incomplete_transaction(tmp_path)
    journal.append("rolled_back", {"status": "rolled_back"})
    result = module.recover_transaction(
        tmp_path,
        Path("unused-policy.toml"),
        transaction_id="tx-test",
        session_id="test-session",
    )
    assert result == {"status": "already_terminal", "transaction_id": "tx-test", "event": "rolled_back"}
    assert not lock.exists()


def test_final_closure_comparison_rejects_matching_fingerprint_with_spoofed_detail() -> None:
    module = _load_module()
    expected = {"fingerprint": "sha256:" + "1" * 64, "target_states": [{"path": "a", "sha256": "x"}]}
    observed = {"fingerprint": expected["fingerprint"], "target_states": [{"path": "b", "sha256": "x"}]}
    with pytest.raises(module.MigrationError) as exc_info:
        module._require_exact_final_closure(observed, expected)
    assert exc_info.value.code == "FINAL_CLOSURE_MISMATCH"


@pytest.mark.skipif(os.name != "nt", reason="Win32 handle semantics")
def test_windows_guard_child_lock_blocks_ancestor_rename_swap(tmp_path: Path) -> None:
    module = _load_module()
    ancestor = tmp_path / "inside"
    target = ancestor / "target.txt"
    _write(target, "inside\n")
    with module.WindowsPathGuard(tmp_path) as guard:
        guard.hold_namespace(target)
        with pytest.raises(PermissionError):
            os.replace(module._native_path(ancestor), module._native_path(tmp_path / "swapped"))
        assert target.read_text(encoding="utf-8") == "inside\n"
    assert not list(ancestor.glob(".gtkb-wi5640-guard-*.tmp"))


@pytest.mark.skipif(os.name != "nt", reason="Win32 handle-relative semantics")
@pytest.mark.parametrize("name", ["ordinary.txt", "CON", "$null", "list[str]", "-p"])
def test_windows_handle_relative_open_read_and_no_replace_rename(tmp_path: Path, name: str) -> None:
    module = _load_module()
    target = tmp_path / name
    module._durable_write(target, b"preimage\n")
    backup_name = f".{name}.backup"
    with module.WindowsPathGuard(tmp_path) as guard:
        guard.hold_namespace(target)
        handle, identity = guard.open_target_for_swap(target)
        try:
            assert identity.reparse_tag == 0
            assert guard.read_handle_bytes(handle) == b"preimage\n"
            parent_handle = guard._parent_handle(target)
            guard.rename_handle(handle, parent_handle, backup_name)
            assert module._literal_read_bytes(target) is None
            renamed = guard._identity(handle)
            assert Path(guard._normalize_final(renamed.final_path)).name.casefold() == backup_name.casefold()
            assert guard.read_handle_bytes(handle) == b"preimage\n"
            guard.rename_handle(handle, parent_handle, name)
        finally:
            guard._kernel32.CloseHandle(handle)
    assert module._literal_read_bytes(target) == b"preimage\n"


@pytest.mark.skipif(os.name != "nt", reason="Win32 literal-path semantics")
@pytest.mark.parametrize("name", ["CON", "$null", "list[str]", "-p"])
def test_atomic_compare_replace_handles_literal_windows_names(tmp_path: Path, name: str) -> None:
    module = _load_module()
    target = tmp_path / name
    with module.WindowsPathGuard(tmp_path) as guard:
        identity = module._atomic_compare_replace(
            tmp_path,
            target,
            b"literal\n",
            expected_preimage_sha256=None,
            mode=0o644,
            guard=guard,
        )
        assert identity.reparse_tag == 0
        assert module._literal_read_bytes(target) == b"literal\n"


@pytest.mark.skipif(os.name != "nt", reason="Win32 handle-relative replacement semantics")
def test_atomic_compare_replace_exclusively_swaps_verified_preimage(tmp_path: Path) -> None:
    module = _load_module()
    target = tmp_path / "target.txt"
    module._durable_write(target, b"preimage\n")
    with module.WindowsPathGuard(tmp_path) as guard:
        module._atomic_compare_replace(
            tmp_path,
            target,
            b"postimage\n",
            expected_preimage_sha256=module.sha256_bytes(b"preimage\n"),
            mode=0o644,
            guard=guard,
            operation_token="verified-swap",
        )
    assert target.read_bytes() == b"postimage\n"
    assert not list(tmp_path.glob(".target.txt.wi5640-verified-swap.*"))


@pytest.mark.skipif(os.name != "nt", reason="Win32 handle-relative replacement semantics")
def test_atomic_compare_replace_preserves_intruder_and_recovery_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _load_module()
    target = tmp_path / "target.txt"
    module._durable_write(target, b"preimage\n")

    def inject_intruder(point: str) -> None:
        if point == "after_atomic_backup":
            module._durable_write(target, b"intruder\n")

    monkeypatch.setattr(module, "_fault", inject_intruder)
    with module.WindowsPathGuard(tmp_path) as guard, pytest.raises(module.MigrationError) as exc_info:
        module._atomic_compare_replace(
            tmp_path,
            target,
            b"postimage\n",
            expected_preimage_sha256=module.sha256_bytes(b"preimage\n"),
            mode=0o644,
            guard=guard,
            operation_token="intruder-race",
        )
    assert exc_info.value.code == "ATOMIC_COMPENSATION_FAILED"
    assert target.read_bytes() == b"intruder\n"
    assert (tmp_path / ".target.txt.wi5640-intruder-race.bak").read_bytes() == b"preimage\n"
    assert (tmp_path / ".target.txt.wi5640-intruder-race.tmp").read_bytes() == b"postimage\n"


@pytest.mark.skipif(os.name != "nt", reason="Win32 crash-recovery semantics")
def test_recovery_classifies_backup_install_crash_and_restores_preimage(tmp_path: Path) -> None:
    module = _load_module()
    temporary = tmp_path / ".target.txt.wi5640-crash.tmp"
    backup = tmp_path / ".target.txt.wi5640-crash.bak"
    temporary.write_bytes(b"postimage\n")
    backup.write_bytes(b"preimage\n")
    operation = {
        "path": "target.txt",
        "preimage_sha256": module.sha256_bytes(b"preimage\n"),
        "postimage_sha256": module.sha256_bytes(b"postimage\n"),
        "mode": 0o644,
    }
    journal = module.TransactionJournal.create(tmp_path, "tx-crash", {"writes": [operation]})
    journal.append(
        "write_intent",
        {
            "path": "target.txt",
            "temporary_path": temporary.name,
            "backup_path": backup.name,
        },
    )
    with module.WindowsPathGuard(tmp_path) as guard:
        prepared = module._prepare_interrupted_atomic_writes(tmp_path, [operation], journal, guard)
        cleaned = module._cleanup_atomic_artifacts(tmp_path, [operation], journal, guard)
    assert prepared == [{"path": "target.txt", "status": "preimage_restored_from_backup"}]
    assert (tmp_path / "target.txt").read_bytes() == b"preimage\n"
    assert cleaned == [{"path": "target.txt", "artifact": temporary.name, "status": "removed"}]
    assert not temporary.exists() and not backup.exists()


@pytest.mark.skipif(os.name != "nt", reason="Win32 crash-recovery semantics")
def test_recovery_refuses_unknown_target_occupant_without_mutation(tmp_path: Path) -> None:
    module = _load_module()
    target = tmp_path / "target.txt"
    temporary = tmp_path / ".target.txt.wi5640-crash.tmp"
    backup = tmp_path / ".target.txt.wi5640-crash.bak"
    target.write_bytes(b"intruder\n")
    temporary.write_bytes(b"postimage\n")
    backup.write_bytes(b"preimage\n")
    operation = {
        "path": "target.txt",
        "preimage_sha256": module.sha256_bytes(b"preimage\n"),
        "postimage_sha256": module.sha256_bytes(b"postimage\n"),
        "mode": 0o644,
    }
    journal = module.TransactionJournal.create(tmp_path, "tx-crash", {"writes": [operation]})
    journal.append(
        "write_intent",
        {
            "path": "target.txt",
            "temporary_path": temporary.name,
            "backup_path": backup.name,
        },
    )
    with module.WindowsPathGuard(tmp_path) as guard:
        outcomes = module._prepare_interrupted_atomic_writes(tmp_path, [operation], journal, guard)
    assert outcomes == [{"path": "target.txt", "status": "unknown_target_artifact"}]
    assert target.read_bytes() == b"intruder\n"
    assert temporary.read_bytes() == b"postimage\n"
    assert backup.read_bytes() == b"preimage\n"


@pytest.mark.skipif(os.name != "nt", reason="Win32 handle-relative directory semantics")
def test_parent_directories_are_created_and_removed_through_held_handles(tmp_path: Path) -> None:
    module = _load_module()
    target = tmp_path / "first/second/target.txt"
    journal = module.TransactionJournal.create(tmp_path, "tx-directories", {"mode": "test"})
    with module.WindowsPathGuard(tmp_path) as guard:
        created = module._ensure_parent_directories(tmp_path, target, guard, journal)
        assert [item["path"] for item in created] == ["first", "first/second"]
        assert target.parent.is_dir()
        outcomes = module._remove_created_directories(tmp_path, created, guard, journal)
    assert outcomes == [
        {"path": "first/second", "status": "removed"},
        {"path": "first", "status": "removed"},
    ]
    assert not (tmp_path / "first").exists()


@pytest.mark.skipif(os.name != "nt", reason="Win32 reparse semantics")
def test_component_relative_guard_rejects_intermediate_directory_symlink(tmp_path: Path) -> None:
    module = _load_module()
    root = tmp_path / "repo"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    canary = outside / "canary.txt"
    canary.write_bytes(b"outside\n")
    link = root / "redirect"
    try:
        os.symlink(outside, link, target_is_directory=True)
    except OSError:
        completed = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "New-Item -ItemType Junction -Path $env:GTKB_TEST_LINK -Target $env:GTKB_TEST_TARGET | Out-Null",
            ],
            check=False,
            capture_output=True,
            text=True,
            env={**os.environ, "GTKB_TEST_LINK": str(link), "GTKB_TEST_TARGET": str(outside)},
        )
        if completed.returncode != 0:
            pytest.skip(f"Directory junction unavailable: {completed.stderr.strip()}")
    with module.WindowsPathGuard(root) as guard, pytest.raises(module.MigrationError) as exc_info:
        guard.guard_target(link / "target.txt")
    assert exc_info.value.code in {"WIN32_HANDLE_OPERATION_FAILED", "REPARSE_OBJECT_FORBIDDEN"}
    assert canary.read_bytes() == b"outside\n"
    assert not (outside / "target.txt").exists()


@pytest.mark.skipif(os.name != "nt", reason="Win32 namespace-lock semantics")
def test_atomic_boundary_blocks_root_and_nested_ancestor_renames(tmp_path: Path, monkeypatch) -> None:
    module = _load_module()
    root = tmp_path / "repo"
    ancestor = root / "nested"
    target = ancestor / "target.txt"
    outside = tmp_path / "outside"
    outside.mkdir()
    canary = outside / "canary.txt"
    canary.write_bytes(b"outside\n")
    module._durable_write(target, b"preimage\n")
    attempts: list[str] = []

    def attack(point: str) -> None:
        if point != "after_namespace_lock":
            return
        for source, destination in (
            (root, tmp_path / "repo-moved"),
            (ancestor, root / "nested-moved"),
        ):
            with pytest.raises(PermissionError):
                os.replace(module._native_path(source), module._native_path(destination))
            attempts.append(source.name)

    monkeypatch.setattr(module, "_fault", attack)
    with module.WindowsPathGuard(root) as guard:
        module._atomic_compare_replace(
            root,
            target,
            b"postimage\n",
            expected_preimage_sha256=module.sha256_bytes(b"preimage\n"),
            mode=0o644,
            guard=guard,
            operation_token="rename-boundary",
        )
    assert attempts == ["repo", "nested"]
    assert target.read_bytes() == b"postimage\n"
    assert canary.read_bytes() == b"outside\n"


@pytest.mark.skipif(os.name != "nt", reason="Win32 compare-and-swap semantics")
def test_rollback_rechecks_after_intent_and_preserves_concurrent_bytes(tmp_path: Path, monkeypatch) -> None:
    module = _load_module()
    target = tmp_path / "target.txt"
    preimage = tmp_path / "preimage.bin"
    payload = tmp_path / "postimage.bin"
    target.write_bytes(b"post")
    preimage.write_bytes(b"pre")
    payload.write_bytes(b"post")
    write = {
        "path": "target.txt",
        "preimage_sha256": module.sha256_bytes(b"pre"),
        "postimage_sha256": module.sha256_bytes(b"post"),
        "preimage_payload": "preimage.bin",
        "payload": "postimage.bin",
        "mode": 0o644,
    }
    journal = module.TransactionJournal.create(tmp_path, "tx-test", {"writes": [write]})

    def drift(point: str) -> None:
        if point == "after_rollback_intent":
            target.write_bytes(b"concurrent")

    monkeypatch.setattr(module, "_fault", drift)
    with module.WindowsPathGuard(tmp_path) as guard:
        outcomes = module._rollback_applied(tmp_path, [write], ["target.txt"], guard=guard, journal=journal)
    assert target.read_bytes() == b"concurrent"
    assert any(item["status"] == "rollback_mutation_failed" for item in outcomes)


def test_governance_residual_evidence_is_non_waiving_and_bound() -> None:
    module = _load_module()
    _path, policy = module.load_policy(ROOT, module.DEFAULT_POLICY)
    assert "governance" not in policy["allowed_baseline_failures"]
    governance = policy["observed_residual_failures"]["governance"]
    nodes = sorted(governance["node_ids"])
    digest = "sha256:" + hashlib.sha256(("\n".join(nodes) + "\n").encode()).hexdigest()
    assert len(nodes) == 4
    assert governance["owner_work_item"] == "WI-5178"
    assert governance["failing_node_count"] == 4
    assert governance["allowed_for_stage_b"] is False
    assert governance["stage_b_requires_all_pass"] is True
    assert digest == governance["node_list_lf_sha256"]
    assert "WI-5648" not in str(governance)


def test_migration_source_consumes_only_public_registered_inventory_api() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    assert "import _artifact_inventory" not in source
    assert "registered_artifact_inventory(root, snapshot=snapshot)" in source
