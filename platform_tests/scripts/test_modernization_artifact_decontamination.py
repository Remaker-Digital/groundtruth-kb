"""Frozen acceptance for modernization artifact lifecycle decontamination.

The twelve tests map one-to-one to MOD-AD-01 through MOD-AD-12.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_SRC = ROOT / "groundtruth-kb" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from check_artifact_decontamination import (  # noqa: E402
    audit_repository,
    discover_effective_loading_graph,
)
from groundtruth_kb.artifact_lifecycle.decontamination import (  # noqa: E402
    ArtifactAuthorityIndex,
    ArtifactLifecycleError,
    ArtifactRecord,
    WorkerReference,
    canonical_report_bytes,
    load_repository_snapshot,
    normalize_repository_path,
    parse_startup_inventory,
)
from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from groundtruth_kb.project.registry_control_plane import serialize_registry  # noqa: E402
from groundtruth_kb.project.sot_registry import SoTArtifact, sync_projection  # noqa: E402

CHECKER = ROOT / "scripts" / "check_artifact_decontamination.py"
EXPECTED = {f"MOD-AD-{index:02d}" for index in range(1, 13)}


def _sot_record(
    record_id: str,
    storage_path: str,
    lifecycle: str,
    *,
    coverage_mode: str = "exact",
) -> SoTArtifact:
    return SoTArtifact(
        id=record_id,
        domain="control_surface",
        lifecycle=lifecycle,
        storage_path=storage_path,
        authority_spec_id="TEST-SPEC",
        mutation_api="fixture",
        versioning_policy="git_tracked",
        backup_policy="git_tracked",
        health_check_function="",
        owner_role="shared",
        restore_action="git_restore",
        coverage_mode=coverage_mode,
    )


def _write_registry_generation(root: Path, records: list[SoTArtifact]) -> None:
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
    KnowledgeDB(db_path=db_path)
    sync_projection(records, db_path, changed_by="test", change_reason="fixture")


def _write_import_graph_fixture(
    root: Path,
    *,
    entrypoint: str,
    modules: dict[str, str] | None = None,
    declare_current: bool = True,
) -> list[SoTArtifact]:
    registry = root / "config" / "registry"
    control = root / "config" / "agent-control"
    scripts = root / "scripts"
    rules = root / "rules"
    registry.mkdir(parents=True)
    control.mkdir(parents=True)
    scripts.mkdir(parents=True)
    rules.mkdir(parents=True)
    records = [
        _sot_record("current", "rules/current.md", "active"),
        _sot_record("history", "rules/stale.md", "archive"),
    ]
    _write_registry_generation(root, records)
    (registry / "context-manifests.toml").write_text("items = []\n", encoding="utf-8")
    current_row = "| Current | `rules/current.md` | active | loaded |\n" if declare_current else ""
    (control / "SESSION-STARTUP-CONTROL-MAP.md").write_text(
        "| Startup service | `scripts/session_self_initialization.py` | active | loaded |\n"
        f"{current_row}"
        "| History | `rules/stale.md` | superseded | history |\n",
        encoding="utf-8",
    )
    (control / "activity-envelope-sharding.toml").write_text(
        "[classes.global_baseline]\nallowed_surfaces = []\n[classes.activity_only]\ndeferred_surfaces = []\n",
        encoding="utf-8",
    )
    (control / "system-interface-map.toml").write_text("systems = []\n", encoding="utf-8")
    (scripts / "session_self_initialization.py").write_text(entrypoint, encoding="utf-8")
    (rules / "current.md").write_text("current\n", encoding="utf-8")
    (rules / "stale.md").write_text("stale\n", encoding="utf-8")
    for relative_path, text in (modules or {}).items():
        target = root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return records


def _index() -> ArtifactAuthorityIndex:
    return ArtifactAuthorityIndex(
        [
            ArtifactRecord("guide", "rules/guide-v1.md", "superseded", "fixture", 1, "guide"),
            ArtifactRecord("guide", "rules/guide-v2.md", "current", "fixture", 2),
            ArtifactRecord("guide-render", "generated/guide.md", "generated", "fixture"),
        ]
    )


def test_mod_ad_01_lifecycle_is_mechanically_classified() -> None:
    index = _index()
    assert index.path_status("rules/guide-v2.md")["status"] == "current"
    assert index.path_status("rules/guide-v1.md")["status"] == "historical"


def test_mod_ad_02_unordered_history_resolves_one_current_authority() -> None:
    index = ArtifactAuthorityIndex(reversed(_index().records))
    resolution = index.resolve("guide")
    assert resolution["status"] == "resolved"
    assert resolution["current"]["path"] == "rules/guide-v2.md"
    assert [item["path"] for item in resolution["history"]] == ["rules/guide-v1.md"]


def test_mod_ad_03_multiple_current_authorities_fail_closed() -> None:
    index = ArtifactAuthorityIndex(
        [
            ArtifactRecord("guide", "rules/a.md", "current", "fixture"),
            ArtifactRecord("guide", "rules/b.md", "active", "fixture", 2),
        ]
    )
    report = index.audit([])
    assert report["status"] == "FAIL"
    assert report["findings"] == [
        {
            "id": "ambiguous:guide",
            "severity": "P0",
            "reason": "logical artifact has multiple current authorities",
        }
    ]


def test_mod_ad_04_current_worker_path_passes() -> None:
    report = _index().audit([WorkerReference("rules/guide-v2.md", "fixture")])
    assert report["status"] == "PASS"
    assert report["worker_references"][0]["resolution"] == "current"


def test_mod_ad_05_superseded_worker_path_is_p0() -> None:
    report = _index().audit([WorkerReference("rules/guide-v1.md", "fixture")])
    assert report["status"] == "FAIL"
    assert report["findings"][0]["severity"] == "P0"
    assert "historical authority" in report["findings"][0]["reason"]


def test_mod_ad_06_unknown_worker_path_fails_closed() -> None:
    report = _index().audit([WorkerReference("rules/unregistered.md", "fixture")])
    assert report["status"] == "FAIL"
    assert report["findings"][0]["severity"] == "P1"
    assert "no lifecycle declaration" in report["findings"][0]["reason"]


def test_mod_ad_07_conflicting_path_lifecycle_is_p0() -> None:
    index = ArtifactAuthorityIndex(
        [
            ArtifactRecord("archive", "archive/old", "archive", "registry-a", scope="tree"),
            ArtifactRecord("revived", "archive/old/worker.md", "current", "registry-b"),
        ]
    )
    report = index.audit([WorkerReference("archive/old/worker.md", "fixture")])
    assert report["status"] == "FAIL"
    assert report["findings"][0]["severity"] == "P0"
    assert "conflicting lifecycle" in report["findings"][0]["reason"]


def test_mod_ad_08_generated_projection_is_not_current_authority() -> None:
    resolution = _index().resolve("guide-render")
    assert resolution["status"] == "no_current"
    assert resolution["current"] is None
    assert resolution["projections"][0]["path"] == "generated/guide.md"


def test_sot_tree_declaration_classifies_descendants_without_file_existence(tmp_path: Path) -> None:
    records = _write_import_graph_fixture(tmp_path, entrypoint="def main():\n    return None\n")
    _write_registry_generation(
        tmp_path,
        [
            *records,
            _sot_record("runtime", ".state/", "generated", coverage_mode="recursive"),
        ],
    )

    index, _ = load_repository_snapshot(tmp_path)
    assert index.path_status(".state/nested/missing.json")["status"] == "generated"


def test_mod_ad_09_paths_are_exact_case_insensitive_and_cannot_escape() -> None:
    assert _index().path_status("RULES\\GUIDE-V2.MD")["status"] == "current"
    with pytest.raises(ArtifactLifecycleError):
        normalize_repository_path("../rules/guide-v2.md")
    with pytest.raises(ArtifactLifecycleError):
        normalize_repository_path("E:/GT-KB/rules/guide-v2.md")


def test_mod_ad_10_narrative_negative_control_cannot_declare_lifecycle() -> None:
    records, references = parse_startup_inventory(
        "This prose says `rules/stale.md` is active.\n"
        "| Current Guide | `rules/current.md` | active | loaded |\n"
        "| Old Guide | `rules/stale.md` | superseded | history |\n",
        source="fixture.md",
    )
    index = ArtifactAuthorityIndex(records)
    assert len(references) == 1
    assert references[0].path == "rules/current.md"
    assert index.path_status("rules/stale.md")["status"] == "historical"


def test_mod_ad_11_report_bytes_are_order_independent() -> None:
    index = _index()
    references = [
        WorkerReference("generated/guide.md", "second"),
        WorkerReference("rules/guide-v2.md", "first"),
    ]
    assert canonical_report_bytes(index.audit(references)) == canonical_report_bytes(index.audit(reversed(references)))


@pytest.mark.timeout(600)
def test_effective_loading_graph_is_repeatable() -> None:
    first = discover_effective_loading_graph(ROOT)
    second = discover_effective_loading_graph(ROOT)

    assert canonical_report_bytes(first) == canonical_report_bytes(second)
    assert first["entrypoints"]
    assert first["load_edges"]


def test_undeclared_dynamic_import_fails_closed(tmp_path: Path) -> None:
    _write_import_graph_fixture(
        tmp_path,
        entrypoint=("import importlib\n\ndef load(module_name):\n    return importlib.import_module(module_name)\n"),
    )

    graph = discover_effective_loading_graph(tmp_path)

    assert graph["declared_dynamic_imports"] == []
    assert graph["unresolved_imports"] == [
        {
            "importer": "scripts/session_self_initialization.py",
            "line": 4,
            "module": "<dynamic>",
            "reason": "dynamic import target is not a string literal",
            "source": "scripts/session_self_initialization.py:4",
        }
    ]


def test_explicit_runtime_validated_dynamic_import_boundary_is_reported(tmp_path: Path) -> None:
    _write_import_graph_fixture(
        tmp_path,
        entrypoint=(
            "import importlib\n\n"
            "__gtkb_dynamic_import_contract__ = {\n"
            "    'load': 'Configured plugin is runtime type-validated.',\n"
            "}\n\n"
            "def load(module_name):\n"
            "    return importlib.import_module(module_name)\n"
        ),
    )

    graph = discover_effective_loading_graph(tmp_path)

    assert graph["unresolved_imports"] == []
    assert graph["declared_dynamic_imports"] == [
        {
            "source": "scripts/session_self_initialization.py",
            "line": 8,
            "function": "load",
            "reason": "Configured plugin is runtime type-validated.",
        }
    ]


def test_mod_ad_12_repository_contract_passes_for_declared_import_closure(tmp_path: Path) -> None:
    _write_import_graph_fixture(
        tmp_path,
        entrypoint="from support import loader\n\ndef main():\n    return loader.load()\n",
        modules={
            "support/__init__.py": "",
            "support/loader.py": (
                "from pathlib import Path\n"
                "PROJECT_ROOT = Path(__file__).resolve().parent.parent\n"
                "def load():\n"
                "    return (PROJECT_ROOT / 'rules' / 'current.md').read_text(encoding='utf-8')\n"
            ),
        },
    )
    result = subprocess.run(
        [sys.executable, str(CHECKER), "--project-root", str(tmp_path), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assertions = {item["id"]: item for item in report["assertions"]}
    assert report["status"] == "PASS"
    assert set(assertions) == EXPECTED
    assert all(item["status"] == "PASS" and item["evidence"] for item in assertions.values())


def test_mod_ad_12_live_repository_contract_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(CHECKER), "--project-root", str(ROOT), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["status"] == "PASS"
    assert report["audit"]["findings"] == []
    assert report["effective_loading_graph"]["unresolved_imports"] == []


def test_retired_system_interface_left_startup_visible_fails_live_repository_audit(tmp_path: Path) -> None:
    registry = tmp_path / "config" / "registry"
    control = tmp_path / "config" / "agent-control"
    registry.mkdir(parents=True)
    control.mkdir(parents=True)
    _write_registry_generation(tmp_path, [_sot_record("current", "rules/current.md", "active")])
    (registry / "context-manifests.toml").write_text("items = []\n", encoding="utf-8")
    (control / "SESSION-STARTUP-CONTROL-MAP.md").write_text(
        "| Current | `rules/current.md` | active | loaded |\n",
        encoding="utf-8",
    )
    (control / "activity-envelope-sharding.toml").write_text(
        "[classes.global_baseline]\nallowed_surfaces = []\n[classes.activity_only]\ndeferred_surfaces = []\n",
        encoding="utf-8",
    )
    (control / "system-interface-map.toml").write_text(
        '[[systems]]\nid = "stale"\nauthoritative_source = "rules/retired.md"\n'
        'lifecycle_state = "retired"\nstartup_visibility = "compact_status"\n',
        encoding="utf-8",
    )

    report = audit_repository(tmp_path)

    assert report["status"] == "FAIL"
    stale_reference = next(item for item in report["audit"]["worker_references"] if item["path"] == "rules/retired.md")
    assert stale_reference["resolution"] == "historical"
    assert any(item["id"] == "rules/retired.md" and item["severity"] == "P0" for item in report["audit"]["findings"])


def test_undeclared_effective_loader_fails_live_repository_audit(tmp_path: Path) -> None:
    registry = tmp_path / "config" / "registry"
    control = tmp_path / "config" / "agent-control"
    scripts = tmp_path / "scripts"
    registry.mkdir(parents=True)
    control.mkdir(parents=True)
    scripts.mkdir(parents=True)
    _write_registry_generation(tmp_path, [_sot_record("current", "rules/current.md", "active")])
    (registry / "context-manifests.toml").write_text("items = []\n", encoding="utf-8")
    (control / "SESSION-STARTUP-CONTROL-MAP.md").write_text(
        "| Startup service | `scripts/session_self_initialization.py` | active | loaded |\n"
        "| Current | `rules/current.md` | active | loaded |\n",
        encoding="utf-8",
    )
    (control / "activity-envelope-sharding.toml").write_text(
        "[classes.global_baseline]\nallowed_surfaces = []\n[classes.activity_only]\ndeferred_surfaces = []\n",
        encoding="utf-8",
    )
    (control / "system-interface-map.toml").write_text("systems = []\n", encoding="utf-8")
    (scripts / "session_self_initialization.py").write_text(
        "from pathlib import Path\n"
        "PROJECT_ROOT = Path(__file__).resolve().parent.parent\n"
        "UNDECLARED = PROJECT_ROOT / 'rules' / 'undeclared.md'\n"
        "def main():\n"
        "    return UNDECLARED.read_text(encoding='utf-8')\n",
        encoding="utf-8",
    )
    rules = tmp_path / "rules"
    rules.mkdir()
    (rules / "undeclared.md").write_text("present but not authoritative\n", encoding="utf-8")

    report = audit_repository(tmp_path)

    assertion = next(item for item in report["assertions"] if item["id"] == "MOD-AD-11")
    assert report["status"] == "FAIL"
    assert assertion["status"] == "FAIL"
    assert report["effective_loading_graph"]["load_edges"] == [
        {
            "entrypoint": "scripts/session_self_initialization.py",
            "line": 5,
            "loader": "read_text",
            "path": "rules/undeclared.md",
            "source": "scripts/session_self_initialization.py:5",
        }
    ]
    assert any(
        item["id"] == "rules/undeclared.md"
        and item["severity"] == "P1"
        and item["reason"] == "worker-loading path has no lifecycle declaration"
        for item in report["audit"]["findings"]
    )


def test_transitive_contaminated_import_is_a_live_worker_finding(tmp_path: Path) -> None:
    _write_import_graph_fixture(
        tmp_path,
        entrypoint="from support import loader\n",
        modules={
            "support/__init__.py": "",
            "support/loader.py": (
                "from pathlib import Path\n"
                "PROJECT_ROOT = Path(__file__).resolve().parent.parent\n"
                "CONTAMINATED = PROJECT_ROOT / 'rules' / 'stale.md'\n"
                "def load():\n"
                "    return CONTAMINATED.read_text(encoding='utf-8')\n"
            ),
        },
    )

    report = audit_repository(tmp_path)

    assert report["status"] == "FAIL"
    assert report["effective_loading_graph"]["load_edges"] == [
        {
            "entrypoint": "support/loader.py",
            "line": 5,
            "loader": "read_text",
            "path": "rules/stale.md",
            "source": "support/loader.py:5",
        }
    ]
    assert any(
        item["id"] == "rules/stale.md" and item["severity"] == "P0" and "historical authority" in item["reason"]
        for item in report["audit"]["findings"]
    )


def test_missing_local_module_fails_closed_without_execution(tmp_path: Path) -> None:
    _write_import_graph_fixture(
        tmp_path,
        entrypoint="import support.missing\n",
        modules={"support/__init__.py": "raise RuntimeError('must not execute')\n"},
    )

    report = audit_repository(tmp_path)

    assert report["status"] == "FAIL"
    assert report["effective_loading_graph"]["unresolved_imports"] == [
        {
            "importer": "scripts/session_self_initialization.py",
            "line": 1,
            "module": "support.missing",
            "reason": "local module does not resolve to a repository file",
            "source": "scripts/session_self_initialization.py:1",
        }
    ]
    assert any(
        item["id"] == "unresolved-import:scripts/session_self_initialization.py:1" and item["severity"] == "P1"
        for item in report["audit"]["findings"]
    )


def test_import_cycles_are_traversed_once_and_remain_deterministic(tmp_path: Path) -> None:
    _write_import_graph_fixture(
        tmp_path,
        entrypoint="from support import a\n",
        modules={
            "support/__init__.py": "",
            "support/a.py": "from support import b\n",
            "support/b.py": (
                "from pathlib import Path\n"
                "from support import a\n"
                "PROJECT_ROOT = Path(__file__).resolve().parent.parent\n"
                "def load():\n"
                "    return (PROJECT_ROOT / 'rules' / 'current.md').read_text(encoding='utf-8')\n"
            ),
        },
    )

    first = discover_effective_loading_graph(tmp_path)
    second = discover_effective_loading_graph(tmp_path)

    assert first == second
    assert first["unresolved_imports"] == []
    assert first["python_modules"] == [
        "scripts/session_self_initialization.py",
        "support/__init__.py",
        "support/a.py",
        "support/b.py",
    ]
    assert sum(edge["imported"] == "support/a.py" for edge in first["import_edges"]) == 2


def test_valid_declared_transitive_dependency_closure_passes(tmp_path: Path) -> None:
    _write_import_graph_fixture(
        tmp_path,
        entrypoint="from support import loader\n",
        modules={
            "support/__init__.py": "",
            "support/loader.py": (
                "from pathlib import Path\n"
                "PROJECT_ROOT = Path(__file__).resolve().parent.parent\n"
                "def load():\n"
                "    return (PROJECT_ROOT / 'rules' / 'current.md').read_text(encoding='utf-8')\n"
            ),
        },
    )

    report = audit_repository(tmp_path)

    assert report["status"] == "PASS"
    assert report["audit"]["findings"] == []
    assert report["effective_loading_graph"]["unresolved_imports"] == []
    assertion = next(item for item in report["assertions"] if item["id"] == "MOD-AD-11")
    assert assertion["status"] == "PASS"
    assert assertion["evidence"]["reachable_python_modules"] == 3
    assert assertion["evidence"]["effective_source_declarations"] == 0


def test_parent_relative_import_resolves_within_local_package(tmp_path: Path) -> None:
    _write_import_graph_fixture(
        tmp_path,
        entrypoint="from support.nested import loader\n",
        modules={
            "support/__init__.py": "",
            "support/common.py": (
                "from pathlib import Path\n"
                "PROJECT_ROOT = Path(__file__).resolve().parent.parent\n"
                "def load():\n"
                "    return (PROJECT_ROOT / 'rules' / 'current.md').read_text(encoding='utf-8')\n"
            ),
            "support/nested/__init__.py": "",
            "support/nested/loader.py": "from .. import common\n",
        },
    )

    graph = discover_effective_loading_graph(tmp_path)

    assert graph["unresolved_imports"] == []
    assert "support/common.py" in graph["python_modules"]
    assert any(
        edge["importer"] == "support/nested/loader.py"
        and edge["imported"] == "support/common.py"
        and edge["module"] == ".."
        for edge in graph["import_edges"]
    )
