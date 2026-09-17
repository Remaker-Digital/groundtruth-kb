"""Optional search-cache regeneration derived from the authority's current records.

Retained duties: a read-only preview, an actual rebuild from current canonical
data, and a truthful missing-dependency result that preserves existing cache
bytes. No local database is read or created at any point.

Confinement duty (N-31): the only directory a rebuild may replace is the cache the
application declares in ``.gtkb-app-isolation.json`` (``.groundtruth-chroma``,
``generated_output``). The application root, its Git metadata, authoritative
inputs, undeclared entries, other generated outputs and outside paths are refused
before the authority is contacted, leaving every byte in place.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from groundtruth_kb.db import HAS_CHROMADB
from groundtruth_kb.project import chroma as chroma_module
from groundtruth_kb.project.application_upgrade import UpgradeOptions, apply_upgrade, plan_upgrade
from groundtruth_kb.project.chroma import canonical_documents, regenerate
from groundtruth_kb.project.doctor_isolation import run_isolation_checks

requires_chromadb = pytest.mark.skipif(not HAS_CHROMADB, reason="ChromaDB not installed")


def _seed(native_application) -> None:
    client = native_application.client
    client.request(
        "PUT",
        "/v1/specifications/SPEC-ALPHA-1",
        body={
            "expected_version": 0,
            "actor": "qualification",
            "reason": "cache fixture",
            "fields": {
                "title": "Alpha behavior",
                "description": "Alpha must greet.",
                "application_scope": "application:Alpha",
            },
        },
    )
    client.request(
        "PUT",
        "/v1/specifications/SPEC-BETA-1",
        body={
            "expected_version": 0,
            "actor": "qualification",
            "reason": "cache fixture",
            "fields": {"title": "Beta behavior", "application_scope": "application:Beta"},
        },
    )
    client.request(
        "PUT",
        "/v1/tests/TEST-ALPHA-1",
        body={
            "expected_version": 0,
            "actor": "qualification",
            "reason": "cache fixture",
            "fields": {
                "title": "Alpha greets",
                "test_type": "integration",
                "expected_outcome": "greeting appears",
                "spec_id": "SPEC-ALPHA-1",
                "test_file": "tests/test_greeting.py",
                "test_function": "test_greets",
                "application_scope": "application:Alpha",
            },
        },
    )
    client.request(
        "PUT",
        "/v1/test-plans/PLAN-ALPHA",
        body={
            "expected_version": 0,
            "actor": "qualification",
            "reason": "cache fixture",
            "fields": {"title": "Alpha plan"},
        },
    )
    client.request(
        "PUT",
        "/v1/test-phases/PHASE-ALPHA",
        body={
            "expected_version": 0,
            "actor": "qualification",
            "reason": "cache fixture",
            "fields": {
                "title": "Alpha effects",
                "plan_id": "PLAN-ALPHA",
                "phase_order": 10,
                "gate_criteria": "Greeting observed",
                "test_ids": ["TEST-ALPHA-1"],
            },
        },
    )
    client.request(
        "PUT",
        "/v1/work-items/WI-ALPHA-1",
        body={
            "expected_version": 0,
            "actor": "qualification",
            "reason": "cache fixture",
            "project_id": "PROJECT-Alpha",
            "fields": {
                "title": "Implement the greeting",
                "description": "Alpha work",
                "origin": "new",
                "priority": "P2",
                "component": "adoption",
                "source_spec_id": "SPEC-ALPHA-1",
                "source_test_id": "TEST-ALPHA-1",
            },
        },
    )


def test_canonical_documents_are_the_applications_current_records(native_application) -> None:
    _seed(native_application)
    documents = canonical_documents(native_application.client, "application:Alpha")
    assert {row["id"] for row in documents} == {
        "specifications/SPEC-ALPHA-1",
        "tests/TEST-ALPHA-1",
        "work-items/WI-ALPHA-1",
    }
    assert all(row["version"] == 1 for row in documents)
    assert "Alpha must greet." in next(row["text"] for row in documents if row["domain"] == "specifications")
    assert {row["id"] for row in canonical_documents(native_application.client, "application:Beta")} == {
        "specifications/SPEC-BETA-1"
    }


def test_chroma_regenerate_replaces_stale_overlay_from_current_records(
    clean_adopter, fake_chromadb, native_application
):
    """Regeneration deletes stale cache files, rebuilds from the authority and leaves the doctor check green."""
    adopter, host = clean_adopter
    _seed(native_application)
    chroma = adopter / ".groundtruth-chroma"
    chroma.mkdir(parents=True, exist_ok=True)
    stale = chroma / "stale.txt"
    stale.write_text("not canonical", encoding="utf-8")

    result = regenerate(adopter)

    assert result.status == "regenerated"
    assert "stale.txt" in result.removed_paths and not stale.exists()
    assert result.indexed == 3 and result.record_counts == {"specifications": 1, "tests": 1, "work-items": 1}
    store = fake_chromadb.instances[-1]
    assert store.path == chroma.resolve() and store.closed
    assert set(store.collection.rows) == {"specifications/SPEC-ALPHA-1", "tests/TEST-ALPHA-1", "work-items/WI-ALPHA-1"}
    assert store.collection.rows["specifications/SPEC-ALPHA-1"]["metadata"]["application_scope"] == "application:Alpha"
    assert not list(adopter.rglob("groundtruth.db")), "no local authority store is created"
    checks = {check.name: check for check in run_isolation_checks(adopter, "dual-agent", product_root=host.parent)}
    assert checks["isolation:chroma-regeneratable"].status == "pass"


@requires_chromadb
def test_chroma_regenerate_with_the_real_dependency(clean_adopter, native_application) -> None:
    adopter, _host = clean_adopter
    _seed(native_application)
    result = regenerate(adopter)
    assert result.status == "regenerated" and result.indexed == 3
    assert (adopter / ".groundtruth-chroma").is_dir()


def test_chroma_regenerate_dry_run_json_does_not_write(clean_adopter, native_application) -> None:
    """The public CLI exposes a non-mutating preview of the rebuild."""
    adopter, _host = clean_adopter
    _seed(native_application)
    chroma = adopter / ".groundtruth-chroma"
    assert not chroma.exists()
    facts = native_application.facts()

    result = native_application.invoke("project", "chroma", "regenerate", "--dir", str(adopter), "--dry-run", "--json")

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "would-regenerate" and payload["dry_run"] is True
    assert payload["chroma_path"] == str(chroma.resolve())
    assert payload["application_scope"] == "application:Alpha"
    assert payload["record_counts"] == {"specifications": 1, "tests": 1, "work-items": 1}
    assert payload["canonical_writes"] == 0
    assert not chroma.exists()
    assert native_application.facts() == facts


def test_chroma_regenerate_reports_optional_dependency_skip(clean_adopter, monkeypatch) -> None:
    """Missing optional ChromaDB support is an explicit skip that preserves existing bytes."""
    adopter, _host = clean_adopter
    chroma = adopter / ".groundtruth-chroma"
    chroma.mkdir(parents=True, exist_ok=True)
    marker = chroma / "existing.txt"
    marker.write_text("leave intact when regeneration cannot run", encoding="utf-8")
    monkeypatch.setattr(chroma_module._db_module, "HAS_CHROMADB", False)

    result = chroma_module.regenerate(adopter)

    assert result.status == "skipped"
    assert result.errors == ("ChromaDB not installed",)
    assert marker.read_text(encoding="utf-8") == "leave intact when regeneration cannot run"
    assert "existing.txt" in result.removed_paths, "the preview still names what a rebuild would replace"


def test_chroma_regenerate_refuses_targets_without_a_configured_authority(tmp_path, clean_adopter) -> None:
    adopter, _host = clean_adopter
    with pytest.raises(ValueError, match="groundtruth.toml"):
        regenerate(tmp_path)
    local = tmp_path / "legacy"
    local.mkdir()
    (local / "groundtruth.toml").write_text('[groundtruth]\ndb_path = "groundtruth.db"\n', encoding="utf-8")
    with pytest.raises(ValueError, match="authority_url"):
        regenerate(local)
    assert not (local / "groundtruth.db").exists()
    with pytest.raises(ValueError, match="application_scope"):
        regenerate(adopter, application_scope="platform")


# --- cache-target confinement ---------------------------------------------------------------------------------------


class _NeverConstructed:
    """Authority client stand-in: constructing it means records were about to be read before the refusal."""

    def __init__(self, url: str) -> None:
        raise AssertionError("the authority must not be contacted for a refused cache target: " + url)


def _configure_cache_path(adopter: Path, value: str) -> None:
    """Select ``[search] chroma_path``; GTConfig anchors a relative value to the application's groundtruth.toml."""
    config = adopter / "groundtruth.toml"
    config.write_text(config.read_text(encoding="utf-8") + f'\n[search]\nchroma_path = "{value}"\n', encoding="utf-8")


def _declare(adopter: Path, name: str, classification: str, purpose: str) -> None:
    """Add one top-level DIR entry to the application's artifact registry."""
    registry = adopter / ".gtkb-app-isolation.json"
    payload = json.loads(registry.read_text(encoding="utf-8"))
    payload["top_level_artifacts"].append(
        {"name": name, "type": "DIR", "classification": classification, "purpose": purpose}
    )
    registry.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _snapshot(root: Path) -> dict[str, bytes]:
    """Every file under ``root`` (Git metadata included) with its bytes."""
    return {path.relative_to(root).as_posix(): path.read_bytes() for path in root.rglob("*") if path.is_file()}


def _plant_sentinel(directory: Path, name: str = "sentinel.txt") -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    marker = directory / name
    marker.write_text("must survive a refused regeneration", encoding="utf-8")
    return marker


def _hostile_target(adopter: Path, scenario: str) -> tuple[str | None, str]:
    """Prepare one refusal scenario; return the ``chroma_path`` setting (None keeps the default) and the message."""
    if scenario == "root":
        return ".", "is the application root itself"
    if scenario == "authoritative-child":
        _plant_sentinel(adopter / "src", "sentinel.py")
        _declare(adopter, "src", "authoritative_input", "Application source tree")
        return "src", "top-level entry 'src' is declared authoritative_input"
    if scenario == "git-directory":
        assert (adopter / ".git" / "HEAD").is_file(), "the scaffold initializes the application repository"
        return ".git", "Git metadata is never a cache target"
    if scenario == "undeclared-sibling":
        _plant_sentinel(adopter / "scratch")
        return "scratch", "top-level entry 'scratch' is not declared in .gtkb-app-isolation.json"
    if scenario == "outside-target":
        _plant_sentinel(adopter.parent / "outside-Alpha")
        return "../outside-Alpha", "is outside application target"
    if scenario == "other-generated-output":
        _plant_sentinel(adopter / ".claude", "settings.json")
        _declare(adopter, ".claude", "generated_output", "Harness configuration projected from the host baseline")
        return ".claude", "declared generated_output but is not the declared search cache .groundtruth-chroma"
    if scenario == "hook-directory":
        assert (adopter / ".githooks" / "reference-transaction").is_file()
        return ".githooks", "top-level entry '.githooks' is declared authoritative_input"
    if scenario == "cache-reclassified":
        registry = adopter / ".gtkb-app-isolation.json"
        payload = json.loads(registry.read_text(encoding="utf-8"))
        for entry in payload["top_level_artifacts"]:
            if entry["name"] == ".groundtruth-chroma":
                entry["classification"] = "authoritative_input"
        registry.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return None, ".groundtruth-chroma is declared DIR authoritative_input"
    if scenario == "registry-unreadable":
        (adopter / ".gtkb-app-isolation.json").write_text("{not json", encoding="utf-8")
        return None, "cannot be classified: .gtkb-app-isolation.json"
    raise AssertionError(scenario)


REFUSAL_SCENARIOS = (
    "root",
    "authoritative-child",
    "git-directory",
    "undeclared-sibling",
    "outside-target",
    "other-generated-output",
    "hook-directory",
    "cache-reclassified",
    "registry-unreadable",
)


@pytest.mark.parametrize("scenario", REFUSAL_SCENARIOS)
def test_chroma_regenerate_refuses_targets_that_are_not_the_declared_cache(
    clean_adopter, fake_chromadb, monkeypatch, scenario
) -> None:
    """A target other than the declared disposable cache is refused before any read or deletion."""
    adopter, _host = clean_adopter
    setting, fragment = _hostile_target(adopter, scenario)
    if setting is not None:
        _configure_cache_path(adopter, setting)
    existing = _plant_sentinel(adopter / ".groundtruth-chroma", "existing.txt")
    before = _snapshot(adopter.parent)
    monkeypatch.setattr(chroma_module, "AuthorityClient", _NeverConstructed)

    with pytest.raises(chroma_module.CacheTargetError, match=re.escape(fragment)) as info:
        regenerate(adopter)

    assert info.value.code == "cache_target_refused"
    assert isinstance(info.value, ValueError)
    assert _snapshot(adopter.parent) == before, "a refusal changes no byte under the disposable host"
    assert existing.read_text(encoding="utf-8") == "must survive a refused regeneration"
    assert fake_chromadb.instances == [], "no persistent client is constructed for a refused target"


def test_chroma_regenerate_cli_refuses_the_application_root(
    clean_adopter, fake_chromadb, monkeypatch, native_application
) -> None:
    """The public route surfaces the typed refusal and leaves the application intact."""
    adopter, _host = clean_adopter
    _configure_cache_path(adopter, ".")
    before = _snapshot(adopter.parent)
    monkeypatch.setattr(chroma_module, "AuthorityClient", _NeverConstructed)

    result = native_application.invoke("project", "chroma", "regenerate", "--dir", str(adopter), "--json")

    assert result.exit_code == 1, result.output
    assert "cache_target_refused: ChromaDB path" in result.output and "is the application root itself" in result.output
    assert _snapshot(adopter.parent) == before
    assert (adopter / "application.toml").is_file() and (adopter / ".git" / "HEAD").is_file()
    assert fake_chromadb.instances == []


def test_chroma_regenerate_accepts_the_explicitly_configured_declared_cache(
    clean_adopter, fake_chromadb, native_application
) -> None:
    """An explicit ``[search] chroma_path`` naming the declared cache regenerates it and touches nothing else."""
    adopter, _host = clean_adopter
    _seed(native_application)
    _configure_cache_path(adopter, ".groundtruth-chroma")
    source = _plant_sentinel(adopter / "src", "sentinel.py")
    cache = adopter / ".groundtruth-chroma"
    stale = _plant_sentinel(cache, "stale.txt")
    siblings = {key: value for key, value in _snapshot(adopter).items() if not key.startswith(".groundtruth-chroma/")}

    result = regenerate(adopter)

    assert result.status == "regenerated" and result.chroma_path == cache.resolve()
    assert "stale.txt" in result.removed_paths and not stale.exists()
    assert fake_chromadb.instances[-1].path == cache.resolve()
    assert source.read_text(encoding="utf-8") == "must survive a refused regeneration"
    assert {k: v for k, v in _snapshot(adopter).items() if not k.startswith(".groundtruth-chroma/")} == siblings


def test_chroma_regenerate_accepts_the_cache_once_upgrade_declares_it(
    clean_adopter, fake_chromadb, monkeypatch, native_application
) -> None:
    """A registry that predates the cache declaration refuses regeneration until ``gt project upgrade`` adds it."""
    adopter, host = clean_adopter
    native_application.stage_baseline()
    registry = adopter / ".gtkb-app-isolation.json"
    payload = json.loads(registry.read_text(encoding="utf-8"))
    payload["top_level_artifacts"] = [e for e in payload["top_level_artifacts"] if e["name"] != ".groundtruth-chroma"]
    registry.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    native_application.commit_all(adopter)
    _seed(native_application)
    cache = adopter / ".groundtruth-chroma"
    stale = _plant_sentinel(cache, "stale.txt")
    with monkeypatch.context() as scoped:
        scoped.setattr(chroma_module, "AuthorityClient", _NeverConstructed)
        with pytest.raises(chroma_module.CacheTargetError, match="entry '.groundtruth-chroma' is not declared"):
            regenerate(adopter)
    assert stale.exists() and fake_chromadb.instances == []

    options = UpgradeOptions("Alpha", "PROJECT-Alpha", host, native_application.client.url)
    applied = apply_upgrade(plan_upgrade(options))

    assert applied["written"] == [".gtkb-app-isolation.json"] and applied["commits"] == 0
    declared = json.loads(registry.read_text(encoding="utf-8"))["top_level_artifacts"]
    assert [e for e in declared if e["name"] == ".groundtruth-chroma"] == [
        {
            "name": ".groundtruth-chroma",
            "type": "DIR",
            "classification": "generated_output",
            "purpose": "Derived search cache rebuilt from the configured authority",
        }
    ]
    siblings = {k: v for k, v in _snapshot(adopter).items() if not k.startswith(".groundtruth-chroma/")}

    result = regenerate(adopter)

    assert result.status == "regenerated" and result.chroma_path == cache.resolve()
    assert "stale.txt" in result.removed_paths and not stale.exists()
    assert result.indexed == 3 and fake_chromadb.instances[-1].path == cache.resolve()
    assert {k: v for k, v in _snapshot(adopter).items() if not k.startswith(".groundtruth-chroma/")} == siblings
