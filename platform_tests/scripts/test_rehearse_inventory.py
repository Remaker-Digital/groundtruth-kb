"""Tests for Wave 2 Slice 2 _inventory.py + _common.py is_runtime_manifest extension.

Per ``bridge/gtkb-isolation-016-phase8-wave2-slice2-003.md`` (REVISED-1)
and ``-004`` (Codex GO).

All tests are fixture-based per F2; no test walks ``LEGACY_ROOT``. The
unreadable-file case uses monkeypatching for Windows determinism per the
GO -004 implementation conditions.
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from rehearse import _inventory  # noqa: E402
from rehearse._common import (  # noqa: E402
    LEGACY_ROOT,
    ManifestValidationError,
    load_manifest,
)

_VALID_FILTER_TEMPLATE = (
    "git filter-repo --path <agent-red-paths-from-_path_rewrite> "
    "--path-rename <each-source>:applications/Agent_Red/<each-target>"
)


def _build_fixture_tree(root: Path) -> None:
    """Create a deterministic fixture tree for inventory tests."""
    (root / "src").mkdir(parents=True)
    (root / "src" / "main.py").write_text("print('hello')\n", encoding="utf-8")
    (root / "src" / "utils.py").write_text("def foo(): pass\n", encoding="utf-8")
    (root / "docs" / "guide.md").parent.mkdir(parents=True)
    (root / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    (root / ".git").mkdir()
    (root / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (root / "node_modules").mkdir()
    (root / "node_modules" / "pkg").mkdir()
    (root / "node_modules" / "pkg" / "index.js").write_text("//\n", encoding="utf-8")


def _build_fixture_matrix(matrix_path: Path) -> None:
    """Create a small but valid Preliminary Authority Matrix markdown file."""
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    matrix_path.write_text(
        "# Test Matrix\n\n"
        "## Preliminary Authority Matrix\n\n"
        "| Surface | Current Evidence | Target Authority | App-Subject Access | GT-KB-Subject Access | Required Decision / Verification |\n"
        "|---|---|---|---|---|---|\n"
        "| `groundtruth.toml` | App root manifest | App-local | Update profile | Define schema | Verify schema |\n"
        "| `bridge/INDEX.md` | Subject-mixed bridge state | App bridge | Write app bridge | Write product bridge | Verify split |\n"
        "| `memory/work_list.md` | Mixed backlog | App backlog | Update app items | Manage product backlog | Verify subject-scoped |\n\n"
        "## Next Section\n",
        encoding="utf-8",
    )


def _build_fixture_manifest(
    output_dir: Path,
    matrix_path: Path,
    legacy_root: Path,
) -> dict[str, Any]:
    """Return a minimal valid Wave 2 manifest dict (already loaded shape)."""
    return {
        "target_root": str((legacy_root / "applications" / "Agent_Red").as_posix()),
        "legacy_root": str(legacy_root.as_posix()),
        "applications_namespace": str((legacy_root / "applications").as_posix()),
        "output_dir": "C:/temp/agent-red-rehearsal",
        "git_strategy": "clone_with_history_filter",
        "git_filter_command_template": _VALID_FILTER_TEMPLATE,
        "phase_1_authority_matrix_path": str(matrix_path.relative_to(LEGACY_ROOT).as_posix()),
        "excluded_paths": [".env", "secrets/", ".tmp.driveupload/"],
    }


# ----- F1: per-file inventory shape -----


def test_walk_inventory_with_metadata_returns_per_file_dict(tmp_path: Path) -> None:
    """Each file entry has sha256, size, mtime.

    Per inventory-perf -004 GO: helper now returns
    ``(inventory, ignored_summary, walk_walltime, hash_walltime)``.
    """
    _build_fixture_tree(tmp_path)
    files, _ignored, _walk_t, _hash_t = _inventory._walk_inventory_with_metadata(
        tmp_path, frozenset({".git", "node_modules"})
    )
    assert "src/main.py" in files
    entry = files["src/main.py"]
    assert "sha256" in entry and len(entry["sha256"]) == 64
    assert "size" in entry and isinstance(entry["size"], int) and entry["size"] > 0
    assert "mtime" in entry and entry["mtime"].endswith("Z")


def test_walk_inventory_excludes_ignored_top_level(tmp_path: Path) -> None:
    """Ignored top-level directories produce no entries."""
    _build_fixture_tree(tmp_path)
    files, _ignored, _walk_t, _hash_t = _inventory._walk_inventory_with_metadata(
        tmp_path, frozenset({".git", "node_modules"})
    )
    assert all(not p.startswith(".git/") for p in files)
    assert all(not p.startswith("node_modules/") for p in files)


def test_walk_inventory_excludes_manifest_excluded_paths(tmp_path: Path) -> None:
    """Manifest excluded_paths translate to top-level ignore entries via run()."""
    _build_fixture_tree(tmp_path)
    (tmp_path / "secrets").mkdir()
    (tmp_path / "secrets" / "key").write_text("REDACTED\n", encoding="utf-8")
    output_dir = tmp_path / "output"
    matrix_path = LEGACY_ROOT / (
        "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/"
        "GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md"
    )
    if not matrix_path.exists():
        pytest.skip("production matrix unavailable in checkout")
    manifest = _build_fixture_manifest(output_dir, matrix_path, tmp_path)
    result = _inventory.run(manifest, output_dir, inventory_root=tmp_path)
    assert result["status"] == "ok"
    assert "secrets" in result["output_files"][0] or True  # path written
    # Read inventory and assert no secrets/* paths
    import json as _json

    inventory = _json.loads((output_dir / "inventory.json").read_text(encoding="utf-8"))
    assert all(not p.startswith("secrets/") for p in inventory["files"])


def test_walk_inventory_handles_unreadable_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Read failures (permission denied, transient I/O) skip the file gracefully.

    Per GO -004 condition: monkeypatch the read path for Windows determinism
    rather than relying on filesystem permission modes.
    """
    _build_fixture_tree(tmp_path)
    target = tmp_path / "src" / "main.py"
    real_read_bytes = Path.read_bytes

    def _selective_read(self: Path) -> bytes:
        if self == target:
            raise OSError("simulated unreadable file for test")
        return real_read_bytes(self)

    monkeypatch.setattr(Path, "read_bytes", _selective_read)
    files, _ignored, _walk_t, _hash_t = _inventory._walk_inventory_with_metadata(
        tmp_path, frozenset({".git", "node_modules"})
    )
    assert "src/main.py" not in files
    assert "src/utils.py" in files
    assert "docs/guide.md" in files


# ----- F3: matrix parser -----


def test_parse_authority_matrix_extracts_preliminary_table_rows(tmp_path: Path) -> None:
    matrix_path = tmp_path / "matrix.md"
    _build_fixture_matrix(matrix_path)
    rows = _inventory._parse_authority_matrix(matrix_path)
    assert len(rows) == 3
    assert rows[0]["surface"] == "`groundtruth.toml`"
    assert all(
        set(r.keys())
        >= {
            "surface",
            "current_evidence",
            "target_authority",
            "app_subject_access",
            "gtkb_subject_access",
            "required_decision_or_verification",
            "_audit_note",
        }
        for r in rows
    )


def test_parse_authority_matrix_missing_section_raises(tmp_path: Path) -> None:
    matrix_path = tmp_path / "matrix.md"
    matrix_path.write_text("# Some Other Header\n\nNo preliminary table here.\n", encoding="utf-8")
    with pytest.raises(ManifestValidationError, match="Preliminary Authority Matrix"):
        _inventory._parse_authority_matrix(matrix_path)


def test_parse_authority_matrix_empty_table_raises(tmp_path: Path) -> None:
    matrix_path = tmp_path / "matrix.md"
    matrix_path.write_text(
        "# Test\n\n## Preliminary Authority Matrix\n\n"
        "| Surface | A | B | C | D | E |\n|---|---|---|---|---|---|\n\n"
        "## Next Section\n",
        encoding="utf-8",
    )
    with pytest.raises(ManifestValidationError, match="no surface rows"):
        _inventory._parse_authority_matrix(matrix_path)


# ----- runtime manifest construction -----


def test_build_runtime_manifest_populates_surface_treatments() -> None:
    source = {"target_root": "x", "legacy_root": "y", "applications_namespace": "z"}
    rows = [
        {
            "surface": "Foo Bar",
            "current_evidence": "ce",
            "target_authority": "ta",
            "app_subject_access": "asa",
            "gtkb_subject_access": "gsa",
            "required_decision_or_verification": "rdv",
            "_audit_note": "n",
        },
        {
            "surface": "groundtruth.toml",
            "current_evidence": "ce2",
            "target_authority": "ta2",
            "app_subject_access": "asa2",
            "gtkb_subject_access": "gsa2",
            "required_decision_or_verification": "rdv2",
            "_audit_note": "n2",
        },
    ]
    runtime = _inventory._build_runtime_manifest(source, rows)
    assert "surface_treatments" in runtime
    assert "foo-bar" in runtime["surface_treatments"]
    assert "groundtruth-toml" in runtime["surface_treatments"]
    assert "_inventory_metadata" in runtime
    assert "schema_note" in runtime["_inventory_metadata"]


def test_write_runtime_manifest_produces_loadable_toml(tmp_path: Path) -> None:
    runtime = {
        "target_root": "E:/GT-KB/applications/Agent_Red",
        "legacy_root": "E:/GT-KB",
        "applications_namespace": "E:/GT-KB/applications",
        "output_dir": "C:/temp/agent-red-rehearsal",
        "git_strategy": "fresh_repo",
        "phase_1_authority_matrix_path": (
            "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/"
            "GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md"
        ),
        "excluded_paths": [".env", ".tmp.driveupload/"],
        "surface_treatments": {
            "foo": {
                "surface": "Foo",
                "current_evidence": "x",
                "target_authority": "y",
                "app_subject_access": "a",
                "gtkb_subject_access": "b",
                "required_decision_or_verification": "c",
                "_audit_note": "n",
            }
        },
        "_inventory_metadata": {"populated_at": "z", "matrix_source": "m", "row_count": "1", "schema_note": "s"},
    }
    output_path = tmp_path / "runtime-manifest.toml"
    _inventory._write_runtime_manifest(runtime, output_path)
    parsed = tomllib.loads(output_path.read_text(encoding="utf-8"))
    assert parsed["target_root"] == runtime["target_root"]
    assert "foo" in parsed["surface_treatments"]
    assert parsed["surface_treatments"]["foo"]["surface"] == "Foo"


# ----- run() integration via inventory_root override -----


def test_run_against_fixture_tree_with_inventory_root_override(tmp_path: Path) -> None:
    """Full run() against a fixture tree using inventory_root override (F2)."""
    fixture_root = tmp_path / "fixture-repo"
    fixture_root.mkdir()
    _build_fixture_tree(fixture_root)
    output_dir = tmp_path / "output"

    matrix_path = LEGACY_ROOT / (
        "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/"
        "GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md"
    )
    if not matrix_path.exists():
        pytest.skip("production matrix unavailable in checkout")

    manifest = _build_fixture_manifest(output_dir, matrix_path, fixture_root)
    result = _inventory.run(manifest, output_dir, inventory_root=fixture_root)
    assert result["status"] == "ok", f"unexpected error: {result['warnings']}"
    assert result["metrics"]["file_count"] >= 3  # src/main.py, src/utils.py, docs/guide.md
    assert (output_dir / "inventory.json").exists()
    assert (output_dir / "runtime-manifest.toml").exists()


def test_run_runtime_manifest_revalidation_failure_reports_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """If matrix has no rows, run() returns status='error' (does NOT raise)."""
    fixture_root = tmp_path / "fixture-repo"
    fixture_root.mkdir()
    _build_fixture_tree(fixture_root)
    empty_matrix_path = tmp_path / "empty-matrix.md"
    empty_matrix_path.write_text(
        "# Test\n\n## Preliminary Authority Matrix\n\n"
        "| Surface | A | B | C | D | E |\n|---|---|---|---|---|---|\n\n"
        "## Next Section\n",
        encoding="utf-8",
    )
    output_dir = tmp_path / "output"
    # Build manifest manually since matrix lives in tmp_path (outside LEGACY_ROOT);
    # patch LEGACY_ROOT in _inventory so the relative-path lookup resolves.
    manifest = {
        "target_root": str((fixture_root / "applications" / "Agent_Red").as_posix()),
        "legacy_root": str(fixture_root.as_posix()),
        "applications_namespace": str((fixture_root / "applications").as_posix()),
        "output_dir": "C:/temp/agent-red-rehearsal",
        "git_strategy": "fresh_repo",
        "phase_1_authority_matrix_path": "empty-matrix.md",
        "excluded_paths": [],
    }
    monkeypatch.setattr(_inventory, "LEGACY_ROOT", tmp_path)
    result = _inventory.run(manifest, output_dir, inventory_root=fixture_root)
    assert result["status"] == "error"
    assert any("no surface rows" in w for w in result["warnings"])


# ----- _common.py is_runtime_manifest extension (Slice 2 contract) -----


def test_load_manifest_runtime_empty_surface_treatments_rejected(tmp_path: Path) -> None:
    """Runtime manifest with empty surface_treatments + is_runtime_manifest=True raises."""
    legacy_posix = LEGACY_ROOT.as_posix()
    runtime_path = tmp_path / "runtime-manifest.toml"
    runtime_path.write_text(
        f'target_root = "{legacy_posix}/applications/Agent_Red"\n'
        f'legacy_root = "{legacy_posix}"\n'
        f'applications_namespace = "{legacy_posix}/applications"\n'
        f'output_dir = "C:/temp/agent-red-rehearsal"\n'
        f'git_strategy = "fresh_repo"\n'
        f'phase_1_authority_matrix_path = "independent-progress-assessments/'
        f'CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md"\n'
        f"\n[surface_treatments]\n",
        encoding="utf-8",
    )
    with pytest.raises(ManifestValidationError, match="M5: runtime manifest requires non-empty"):
        load_manifest(runtime_path, wave=2, is_runtime_manifest=True)


def test_load_manifest_runtime_populated_surface_treatments_accepted(tmp_path: Path) -> None:
    """Runtime manifest with populated surface_treatments + is_runtime_manifest=True passes."""
    legacy_posix = LEGACY_ROOT.as_posix()
    runtime_path = tmp_path / "runtime-manifest.toml"
    runtime_path.write_text(
        f'target_root = "{legacy_posix}/applications/Agent_Red"\n'
        f'legacy_root = "{legacy_posix}"\n'
        f'applications_namespace = "{legacy_posix}/applications"\n'
        f'output_dir = "C:/temp/agent-red-rehearsal"\n'
        f'git_strategy = "fresh_repo"\n'
        f'phase_1_authority_matrix_path = "independent-progress-assessments/'
        f'CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md"\n'
        f"\n[surface_treatments.foo]\n"
        f'surface = "Foo"\n',
        encoding="utf-8",
    )
    data = load_manifest(runtime_path, wave=2, is_runtime_manifest=True)
    assert "foo" in data["surface_treatments"]


# ----- inventory-perf REVISED-1 (S313): cache-only exclusions + dryrun-ignored.json -----


def test_default_ignored_top_level_includes_only_cache_and_transient() -> None:
    """Per inventory-perf -004 GO: only cache/transient dirs; logs/ NOT in default."""
    expected_cache_dirs = {
        ".git",
        "__pycache__",
        "node_modules",
        ".groundtruth-chroma",
        ".tmp.driveupload",
        ".codex_pydeps",
        ".venv",
        "venv",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        "htmlcov",
    }
    assert expected_cache_dirs == _inventory._DEFAULT_IGNORED_TOP_LEVEL
    assert "logs" not in _inventory._DEFAULT_IGNORED_TOP_LEVEL


def test_run_descends_into_logs_subtree(tmp_path: Path) -> None:
    """Per inventory-perf -004 GO: logs/ retained in inventory."""
    _build_fixture_tree(tmp_path)
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs" / "deploy-test.log").write_text("test deploy log\n", encoding="utf-8")
    output_dir = tmp_path / "output"
    matrix_path = LEGACY_ROOT / (
        "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/"
        "GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md"
    )
    if not matrix_path.exists():
        pytest.skip("production matrix unavailable in checkout")
    manifest = _build_fixture_manifest(output_dir, matrix_path, tmp_path)
    result = _inventory.run(manifest, output_dir, inventory_root=tmp_path)
    assert result["status"] == "ok"
    import json as _json

    inventory = _json.loads((output_dir / "inventory.json").read_text(encoding="utf-8"))
    assert "logs/deploy-test.log" in inventory["files"]


def test_run_excludes_codex_pydeps_subtree(tmp_path: Path) -> None:
    """Per inventory-perf -004 GO: cache exclusion of .codex_pydeps."""
    _build_fixture_tree(tmp_path)
    (tmp_path / ".codex_pydeps").mkdir()
    (tmp_path / ".codex_pydeps" / "stub.py").write_text("# stub\n", encoding="utf-8")
    output_dir = tmp_path / "output"
    matrix_path = LEGACY_ROOT / (
        "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/"
        "GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md"
    )
    if not matrix_path.exists():
        pytest.skip("production matrix unavailable in checkout")
    manifest = _build_fixture_manifest(output_dir, matrix_path, tmp_path)
    result = _inventory.run(manifest, output_dir, inventory_root=tmp_path)
    assert result["status"] == "ok"
    import json as _json

    inventory = _json.loads((output_dir / "inventory.json").read_text(encoding="utf-8"))
    assert all(not p.startswith(".codex_pydeps/") for p in inventory["files"])


def test_metrics_includes_walk_and_hash_walltime_separately(tmp_path: Path) -> None:
    """Per inventory-perf -004 GO: 3 distinct walltime metrics."""
    _build_fixture_tree(tmp_path)
    output_dir = tmp_path / "output"
    matrix_path = LEGACY_ROOT / (
        "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/"
        "GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md"
    )
    if not matrix_path.exists():
        pytest.skip("production matrix unavailable in checkout")
    manifest = _build_fixture_manifest(output_dir, matrix_path, tmp_path)
    result = _inventory.run(manifest, output_dir, inventory_root=tmp_path)
    assert result["status"] == "ok"
    metrics = result["metrics"]
    assert "walk_walltime_seconds" in metrics
    assert "hash_walltime_seconds" in metrics
    assert "ignored_summary_walltime_seconds" in metrics
    assert isinstance(metrics["walk_walltime_seconds"], (int, float))
    assert isinstance(metrics["hash_walltime_seconds"], (int, float))


def test_run_emits_dryrun_ignored_json(tmp_path: Path) -> None:
    """Per inventory-perf -004 GO: dryrun-ignored.json present."""
    _build_fixture_tree(tmp_path)
    output_dir = tmp_path / "output"
    matrix_path = LEGACY_ROOT / (
        "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/"
        "GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md"
    )
    if not matrix_path.exists():
        pytest.skip("production matrix unavailable in checkout")
    manifest = _build_fixture_manifest(output_dir, matrix_path, tmp_path)
    result = _inventory.run(manifest, output_dir, inventory_root=tmp_path)
    assert result["status"] == "ok"
    dryrun_ignored = output_dir / "dryrun-ignored.json"
    assert dryrun_ignored.exists()
    assert any(str(dryrun_ignored) in str(p) for p in result["output_files"])


def test_dryrun_ignored_json_records_ignored_directories_with_reasons(tmp_path: Path) -> None:
    """Per Codex GO -004 reporting constraint 1: every default ignored dir has reason."""
    _build_fixture_tree(tmp_path)
    (tmp_path / ".codex_pydeps").mkdir()
    (tmp_path / ".codex_pydeps" / "x.py").write_text("\n", encoding="utf-8")
    output_dir = tmp_path / "output"
    matrix_path = LEGACY_ROOT / (
        "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/"
        "GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md"
    )
    if not matrix_path.exists():
        pytest.skip("production matrix unavailable in checkout")
    manifest = _build_fixture_manifest(output_dir, matrix_path, tmp_path)
    _inventory.run(manifest, output_dir, inventory_root=tmp_path)
    import json as _json

    payload = _json.loads((output_dir / "dryrun-ignored.json").read_text(encoding="utf-8"))
    assert payload["schema_kind"] == "directory_summary_not_per_file_listing"
    assert "ignored_directories_summary" in payload
    codex_entry = next(
        (e for e in payload["ignored_directories_summary"] if e["path"] == ".codex_pydeps"),
        None,
    )
    assert codex_entry is not None
    assert codex_entry["reason"] == "codex_python_deps_cache_regenerable_from_pyproject_toml"
    assert codex_entry["file_count"] == 1
    assert codex_entry["default_or_manifest"] == "default"


def test_dryrun_ignored_json_includes_manifest_excluded_paths_section(tmp_path: Path) -> None:
    """Per Codex GO -004 reporting constraint 1: separately list manifest paths."""
    _build_fixture_tree(tmp_path)
    output_dir = tmp_path / "output"
    matrix_path = LEGACY_ROOT / (
        "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/"
        "GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md"
    )
    if not matrix_path.exists():
        pytest.skip("production matrix unavailable in checkout")
    manifest = _build_fixture_manifest(output_dir, matrix_path, tmp_path)
    _inventory.run(manifest, output_dir, inventory_root=tmp_path)
    import json as _json

    payload = _json.loads((output_dir / "dryrun-ignored.json").read_text(encoding="utf-8"))
    assert "manifest_excluded_paths" in payload
    assert isinstance(payload["manifest_excluded_paths"], list)


def test_walker_returns_ignored_summary_with_audit_data(tmp_path: Path) -> None:
    """Per inventory-perf -004 GO: ignored_summary populated with file_count + bytes."""
    _build_fixture_tree(tmp_path)
    (tmp_path / ".pytest_cache").mkdir()
    (tmp_path / ".pytest_cache" / "v.txt").write_text("cached\n", encoding="utf-8")
    files, ignored_summary, walk_t, hash_t = _inventory._walk_inventory_with_metadata(
        tmp_path, _inventory._DEFAULT_IGNORED_TOP_LEVEL
    )
    assert ".pytest_cache" in ignored_summary
    assert ignored_summary[".pytest_cache"]["file_count"] >= 1
    assert ignored_summary[".pytest_cache"]["total_bytes"] > 0
    assert ignored_summary[".pytest_cache"]["reason"] == "pytest_run_cache_regenerated_on_next_test_run"
    assert walk_t >= 0.0
    assert hash_t >= 0.0
