# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for :mod:`groundtruth_kb.project.sot_registry`.

Covers DCL-SOT-REGISTRY-RECORD-SCHEMA-001 (per-record schema validation)
and DCL-SOT-REGISTRY-PROJECTION-PARITY-001 (parity check semantics).

Bootstrap inventory at ``config/registry/sot-artifacts.toml`` is asserted
to load cleanly and meet GOV-PLATFORM-SOT-REGISTRY-001 acceptance criteria.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from groundtruth_kb.project.sot_registry import (
    InvalidSoTRecord,
    SoTArtifact,
    UnknownDomain,
    default_registry_path,
    load_toml,
    validate_projection_parity,
)

# ---------------------------------------------------------------------------
# Bootstrap inventory acceptance (GOV-PLATFORM-SOT-REGISTRY-001)
# ---------------------------------------------------------------------------


def test_bootstrap_inventory_loads() -> None:
    """The shipped TOML loads without errors and contains >= 22 records."""
    records = load_toml(default_registry_path())
    assert len(records) >= 22, f"expected >=22 bootstrap records, got {len(records)}"


def test_bootstrap_row1_is_self_reference() -> None:
    """Row 1 of the registry MUST be the registry itself.

    Bootstrap guarantee per DCL-SOT-REGISTRY-PROJECTION-PARITY-001.
    """
    records = load_toml(default_registry_path())
    row1 = records[0]
    assert row1.id == "sot-registry-toml"
    assert row1.storage_path == "config/registry/sot-artifacts.toml"
    assert row1.authority_spec_id == "GOV-PLATFORM-SOT-REGISTRY-001"


def test_bootstrap_all_records_have_valid_enums() -> None:
    """All bootstrap records have enum values that load_toml accepted."""
    records = load_toml(default_registry_path())
    valid_domains = {
        "specifications",
        "narrative_authority",
        "bridge_protocol",
        "harness_state",
        "control_surface",
        "governance_policy",
        "runtime_state",
        "scaffold_lifecycle",
        "operational_notepad",
        "retired",
    }
    for r in records:
        assert r.domain in valid_domains, f"{r.id}: invalid domain {r.domain}"
        assert r.lifecycle in {"active", "deprecated", "archive", "generated"}
        assert r.owner_role in {
            "prime_builder",
            "loyal_opposition",
            "owner_only",
            "shared",
            "automated_only",
        }


def test_bootstrap_no_duplicate_ids() -> None:
    """All bootstrap record ids are unique (loader rejects duplicates)."""
    records = load_toml(default_registry_path())
    ids = [r.id for r in records]
    assert len(ids) == len(set(ids)), "duplicate ids in bootstrap inventory"


# ---------------------------------------------------------------------------
# Schema validation (DCL-SOT-REGISTRY-RECORD-SCHEMA-001)
# ---------------------------------------------------------------------------


def _write_toml(tmp_path: Path, body: str) -> Path:
    target = tmp_path / "sot-artifacts.toml"
    target.write_text(textwrap.dedent(body), encoding="utf-8")
    return target


def test_loader_rejects_missing_required_field(tmp_path: Path) -> None:
    body = """
        [[artifacts]]
        id = "missing-storage-path"
        domain = "control_surface"
        lifecycle = "active"
        # storage_path missing
        authority_spec_id = "GOV-PLATFORM-SOT-REGISTRY-001"
        mutation_api = "n/a"
        versioning_policy = "git_tracked"
        backup_policy = "git_tracked"
        health_check_function = ""
        owner_role = "shared"
    """
    path = _write_toml(tmp_path, body)
    with pytest.raises(InvalidSoTRecord, match="missing required field"):
        load_toml(path)


def test_loader_rejects_invalid_domain(tmp_path: Path) -> None:
    body = """
        [[artifacts]]
        id = "bad-domain"
        domain = "not-a-real-domain"
        lifecycle = "active"
        storage_path = "x"
        authority_spec_id = "GOV-X"
        mutation_api = "n/a"
        versioning_policy = "git_tracked"
        backup_policy = "git_tracked"
        health_check_function = ""
        owner_role = "shared"
    """
    path = _write_toml(tmp_path, body)
    with pytest.raises(UnknownDomain):
        load_toml(path)


def test_loader_rejects_invalid_lifecycle(tmp_path: Path) -> None:
    body = """
        [[artifacts]]
        id = "bad-lifecycle"
        domain = "control_surface"
        lifecycle = "invented"
        storage_path = "x"
        authority_spec_id = "GOV-X"
        mutation_api = "n/a"
        versioning_policy = "git_tracked"
        backup_policy = "git_tracked"
        health_check_function = ""
        owner_role = "shared"
    """
    path = _write_toml(tmp_path, body)
    with pytest.raises(InvalidSoTRecord, match="lifecycle"):
        load_toml(path)


def test_loader_rejects_generated_without_mutation_api(tmp_path: Path) -> None:
    body = """
        [[artifacts]]
        id = "generated-without-generator"
        domain = "control_surface"
        lifecycle = "generated"
        storage_path = "x"
        authority_spec_id = "GOV-X"
        mutation_api = ""
        versioning_policy = "regenerated_from_source"
        backup_policy = "regenerable_from_source"
        health_check_function = ""
        owner_role = "shared"
    """
    path = _write_toml(tmp_path, body)
    with pytest.raises(InvalidSoTRecord, match="generated"):
        load_toml(path)


def test_loader_rejects_duplicate_id(tmp_path: Path) -> None:
    body = """
        [[artifacts]]
        id = "dup"
        domain = "control_surface"
        lifecycle = "active"
        storage_path = "a"
        authority_spec_id = "GOV-X"
        mutation_api = "n/a"
        versioning_policy = "git_tracked"
        backup_policy = "git_tracked"
        health_check_function = ""
        owner_role = "shared"

        [[artifacts]]
        id = "dup"
        domain = "control_surface"
        lifecycle = "active"
        storage_path = "b"
        authority_spec_id = "GOV-X"
        mutation_api = "n/a"
        versioning_policy = "git_tracked"
        backup_policy = "git_tracked"
        health_check_function = ""
        owner_role = "shared"
    """
    path = _write_toml(tmp_path, body)
    with pytest.raises(InvalidSoTRecord, match="duplicate id"):
        load_toml(path)


def test_loader_rejects_unknown_field(tmp_path: Path) -> None:
    body = """
        [[artifacts]]
        id = "with-unknown"
        domain = "control_surface"
        lifecycle = "active"
        storage_path = "x"
        authority_spec_id = "GOV-X"
        mutation_api = "n/a"
        versioning_policy = "git_tracked"
        backup_policy = "git_tracked"
        health_check_function = ""
        owner_role = "shared"
        extra_unknown_field = "boom"
    """
    path = _write_toml(tmp_path, body)
    with pytest.raises(InvalidSoTRecord, match="unknown field"):
        load_toml(path)


def test_loader_accepts_optional_fields(tmp_path: Path) -> None:
    body = """
        [[artifacts]]
        id = "with-optionals"
        domain = "control_surface"
        lifecycle = "active"
        storage_path = "x"
        authority_spec_id = "GOV-X"
        mutation_api = "n/a"
        versioning_policy = "git_tracked"
        backup_policy = "git_tracked"
        health_check_function = "_some_check"
        owner_role = "shared"
        depends_on = ["other-id-1", "other-id-2"]
        forbidden_substitutes = ["MEMORY.md"]
        notes = "Optional fields exercise."
    """
    path = _write_toml(tmp_path, body)
    records = load_toml(path)
    assert len(records) == 1
    r = records[0]
    assert r.depends_on == ("other-id-1", "other-id-2")
    assert r.forbidden_substitutes == ("MEMORY.md",)
    assert r.notes == "Optional fields exercise."


def test_loader_health_check_can_be_null(tmp_path: Path) -> None:
    body = """
        [[artifacts]]
        id = "null-health"
        domain = "control_surface"
        lifecycle = "active"
        storage_path = "x"
        authority_spec_id = "GOV-X"
        mutation_api = "n/a"
        versioning_policy = "git_tracked"
        backup_policy = "git_tracked"
        health_check_function = ""
        owner_role = "shared"
    """
    path = _write_toml(tmp_path, body)
    records = load_toml(path)
    assert records[0].health_check_function == ""


# ---------------------------------------------------------------------------
# Parity validation (DCL-SOT-REGISTRY-PROJECTION-PARITY-001)
# ---------------------------------------------------------------------------


def _mk_record(record_id: str = "x") -> SoTArtifact:
    return SoTArtifact(
        id=record_id,
        domain="control_surface",
        lifecycle="active",
        storage_path="path",
        authority_spec_id="GOV-X",
        mutation_api="n/a",
        versioning_policy="git_tracked",
        backup_policy="git_tracked",
        health_check_function=None,
        owner_role="shared",
    )


def test_parity_in_sync_for_identical_lists() -> None:
    r = _mk_record()
    report = validate_projection_parity([r], [r])
    assert report.in_sync is True
    assert report.toml_count == 1
    assert report.projection_count == 1
    assert report.missing_in_projection == ()
    assert report.missing_in_toml == ()
    assert report.field_divergences == ()


def test_parity_detects_missing_in_projection() -> None:
    r1 = _mk_record("a")
    r2 = _mk_record("b")
    report = validate_projection_parity([r1, r2], [r1])
    assert report.in_sync is False
    assert report.missing_in_projection == ("b",)
    assert report.missing_in_toml == ()


def test_parity_detects_missing_in_toml() -> None:
    r1 = _mk_record("a")
    r2 = _mk_record("b")
    report = validate_projection_parity([r1], [r1, r2])
    assert report.in_sync is False
    assert report.missing_in_projection == ()
    assert report.missing_in_toml == ("b",)


def test_parity_detects_field_divergence() -> None:
    toml_rec = _mk_record("x")
    proj_rec = SoTArtifact(
        id="x",
        domain="control_surface",
        lifecycle="deprecated",  # divergence
        storage_path="path",
        authority_spec_id="GOV-X",
        mutation_api="n/a",
        versioning_policy="git_tracked",
        backup_policy="git_tracked",
        health_check_function=None,
        owner_role="shared",
    )
    report = validate_projection_parity([toml_rec], [proj_rec])
    assert report.in_sync is False
    assert report.field_divergences == (("x", "lifecycle"),)


# ---------------------------------------------------------------------------
# Self-reference invariant (parity bootstrap guarantee)
# ---------------------------------------------------------------------------


def test_removing_self_reference_breaks_bootstrap_guarantee() -> None:
    """If row 1 (self-reference) is removed from the registry, downstream
    consumers should observe the missing record (DCL-SOT-REGISTRY-PROJECTION-PARITY-001
    bootstrap guarantee).
    """
    records = load_toml(default_registry_path())
    full = records
    truncated = records[1:]  # drop row 1
    report = validate_projection_parity(truncated, full)
    assert report.in_sync is False
    assert "sot-registry-toml" in report.missing_in_toml
