"""Current baseline coverage, derived outputs and canonical registry reads.

GOV-PLATFORM-SOT-REGISTRY-001 and GOV-HARNESS-NEUTRAL-BASELINE-001 require
unambiguous source coverage; record counts and packaged mirrors prove neither.
"""

from pathlib import Path

import pytest
from groundtruth_kb.project.registry_control_plane import load_registry_snapshot
from groundtruth_kb.project.sot_registry import load_toml

from scripts.harness_projection import project_harness

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REGISTRY = PROJECT_ROOT / "config/registry/sot-artifacts.toml"
BASELINE = PROJECT_ROOT / ".harness-baseline-configuration"


@pytest.fixture(scope="module")
def snapshot():
    return load_registry_snapshot(project_root=PROJECT_ROOT)


def test_every_neutral_source_has_unambiguous_active_coverage(snapshot):
    paths = [p for p in BASELINE.rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    assert paths
    shared = PROJECT_ROOT / ".agents/skills"
    skill_paths = [p for p in shared.rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    assert skill_paths
    paths += skill_paths + [PROJECT_ROOT / name for name in ("AGENTS.md", "CLAUDE.md", ".goosehints")]
    for path in paths:
        assert path.is_file(), path
        record = snapshot.resolver.resolve(path.relative_to(PROJECT_ROOT))
        assert record is not None, path
        assert record.lifecycle == "active", path
        assert record.authority_spec_id == "GOV-HARNESS-NEUTRAL-BASELINE-001", path
        assert record.storage_path.startswith(
            (".harness-baseline-configuration/", ".agents/skills/")
        ) or record.storage_path in {"AGENTS.md", "CLAUDE.md", ".goosehints"}, path


def test_schema_and_registry_self_coverage(snapshot):
    records = load_toml(REGISTRY)
    assert tuple(records) == snapshot.records
    assert len({r.id for r in records}) == len(records)
    record = snapshot.resolver.resolve("config/registry/sot-artifacts.toml")
    assert record is not None and record.lifecycle == "active"
    assert record.coverage_mode == "exact"
    assert all(not r.storage_path.startswith("applications/") for r in records)


def test_redundant_packaged_registry_is_absent():
    assert not list((PROJECT_ROOT / "groundtruth-kb/src/groundtruth_kb").rglob("sot-artifacts.toml"))


@pytest.mark.parametrize(
    "harness",
    [
        name
        for name, profile in project_harness.load_profiles()["harnesses"].items()
        if profile.get("status") != "profile_pending"
    ],
)
def test_all_engine_outputs_have_unambiguous_non_authoritative_coverage(snapshot, harness):
    plan = project_harness.build_plan(harness)
    assert plan.writes and not plan.gaps, plan.gaps
    for path in plan.writes:
        record = snapshot.resolver.resolve(path)
        assert record is not None, path
        assert record.lifecycle == "generated", path
        profile = project_harness.load_profiles()["harnesses"][harness]
        stub_dir = profile.get("skills_stub_dir", "") + "/"
        if profile["skills_discovery"] == "pointer_stubs" and path.startswith(stub_dir):
            assert record.coverage_mode == "recursive" and record.storage_path == stub_dir, path
        else:
            assert record.coverage_mode == "exact" and record.storage_path == path, path
        assert record.authority_spec_id == "GOV-HARNESS-NEUTRAL-BASELINE-001", path
        assert record.mutation_api.startswith(f"gt harness project {harness};"), path
        assert ".harness-baseline-configuration" in record.mutation_api, path
        assert record.versioning_policy == "regenerated_from_source", path
        assert record.backup_policy == "regenerable_from_source", path
        assert record.restore_action == "regenerate_from_source", path
    root = project_harness.load_profiles()["harnesses"][harness]["config_dir"]
    assert snapshot.resolver.resolve(root + "/foreign-unmanaged-do-not-delete.txt") is None


def test_target_configuration_is_never_registered_as_active_authority(snapshot):
    historical_roots = {
        ".agent/",
        ".agents/",
        ".antigravity/",
        ".api-harness/",
        ".claude/",
        ".codex/",
        ".cursor/",
        ".goose/",
    }
    roots = tuple(
        historical_roots
        | {profile["config_dir"] + "/" for profile in project_harness.load_profiles()["harnesses"].values()}
    )
    for record in snapshot.records:
        if record.storage_path.startswith(roots) and not record.storage_path.startswith(".agents/skills/"):
            assert record.lifecycle != "active", record.storage_path


def test_runtime_denials_have_one_non_authoritative_runtime_declaration(snapshot):
    record = snapshot.resolver.resolve(".groundtruth/runtime/gate-denials.jsonl")
    assert record is not None
    assert record.domain == "runtime_state" and record.lifecycle == "active"
    assert record.coverage_mode == "exact"
    assert record.storage_path == ".groundtruth/runtime/gate-denials.jsonl"
    assert record.backup_policy == "gitignored_runtime"
    assert record.restore_action == "visibility_only"
    assert snapshot.resolver.resolve(".groundtruth/runtime/foreign-unmanaged.txt") is None
