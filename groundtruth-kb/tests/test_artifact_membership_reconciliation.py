"""Specification-derived tests for typed artifact membership reconciliation."""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.artifact_membership_reconciliation import (
    ArtifactObservation,
    ObserverResult,
    observe_registered_dependency_closure,
    reconcile_artifact_membership,
)
from groundtruth_kb.project.registry_control_plane import load_registry_snapshot, serialize_registry
from groundtruth_kb.project.sot_registry import SoTArtifact, sync_projection


def _record(record_id: str, storage_path: str, coverage_mode: str = "exact") -> SoTArtifact:
    return SoTArtifact(
        id=record_id,
        domain="control_surface",
        lifecycle="active",
        storage_path=storage_path,
        authority_spec_id="GOV-PLATFORM-SOT-REGISTRY-001",
        mutation_api="test mutation API",
        versioning_policy="git_tracked",
        backup_policy="git_tracked",
        health_check_function="",
        owner_role="shared",
        restore_action="git_restore",
        coverage_mode=coverage_mode,
    )


def _snapshot(tmp_path: Path, records: list[SoTArtifact]):
    registry = tmp_path / "config" / "registry" / "sot-artifacts.toml"
    packaged = (
        tmp_path
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
    db_path = tmp_path / "groundtruth.db"
    KnowledgeDB(db_path=db_path)
    sync_projection(records, db_path, changed_by="test", change_reason="reconciliation fixture")
    return load_registry_snapshot(
        project_root=tmp_path,
        registry_path=registry,
        packaged_registry_path=packaged,
        db_path=db_path,
    )


def _observer_results(*observations: ArtifactObservation) -> tuple[ObserverResult, ...]:
    grouped: dict[str, list[ArtifactObservation]] = {
        "capability_inventory": [],
        "governed_knowledge": [],
        "package_and_entrypoint": [],
        "registered_dependency_closure": [],
    }
    for observation in observations:
        grouped[observation.observer_class].append(observation)
    ancestors = {
        parent.as_posix()
        for observation in observations
        for parent in Path(observation.relative_path).parents
        if parent.as_posix() not in {"", "."}
    }
    results = [
        ObserverResult(
            observer_class=name,
            succeeded=True,
            input_digest=f"sha256:{index:064x}",
            observations=tuple(values),
            ancestor_paths=tuple(sorted(ancestors if values else ())),
        )
        for index, (name, values) in enumerate(grouped.items(), start=1)
    ]
    results.append(
        ObserverResult(
            observer_class="physical_census",
            succeeded=True,
            input_digest=f"sha256:{5:064x}",
            ancestor_paths=tuple(sorted(ancestors)),
        )
    )
    return tuple(results)


def test_observed_gap_is_candidate_and_disposable_subtree_is_pruned(tmp_path: Path) -> None:
    (tmp_path / "member.txt").write_text("registered", encoding="utf-8")
    (tmp_path / "load").mkdir()
    (tmp_path / "load" / "operative.py").write_text("print('operative')\n", encoding="utf-8")
    (tmp_path / "cache" / "deep").mkdir(parents=True)
    (tmp_path / "cache" / "deep" / "disposable.bin").write_bytes(b"x")
    snapshot = _snapshot(tmp_path, [_record("member", "member.txt")])
    observation = ArtifactObservation(
        "load/operative.py",
        "capability_inventory",
        "fixture:capability",
        "fixture operative surface",
    )

    report = reconcile_artifact_membership(
        tmp_path,
        snapshot=snapshot,
        db_path=tmp_path / "groundtruth.db",
        observer_results=_observer_results(observation),
    )

    assert report["membership_complete"] is False
    assert report["counts"]["unregistered_load_bearing"] == 1
    assert report["counts"]["invalid_unknown"] == 0
    assert [row["record"]["storage_path"] for row in report["admission_candidates"]] == ["load/operative.py"]
    cache = next(entry for entry in report["entries"] if entry["relative_path"] == "cache")
    assert cache["traversal_state"] == "pruned_uninspected_subtree"
    assert cache["descendants_inspected"] is False
    assert not any(entry["relative_path"] == "cache/deep/disposable.bin" for entry in report["entries"])


def test_all_required_observers_must_succeed_before_pruning_or_admission(tmp_path: Path) -> None:
    (tmp_path / "member.txt").write_text("registered", encoding="utf-8")
    (tmp_path / "candidate.py").write_text("pass\n", encoding="utf-8")
    snapshot = _snapshot(tmp_path, [_record("member", "member.txt")])
    results = list(
        _observer_results(
            ArtifactObservation(
                "candidate.py",
                "capability_inventory",
                "fixture:capability",
                "fixture operative surface",
            )
        )
    )
    failed = results[1]
    results[1] = ObserverResult(
        observer_class=failed.observer_class,
        succeeded=False,
        input_digest=failed.input_digest,
        diagnostics=("fixture observer unavailable",),
    )

    report = reconcile_artifact_membership(
        tmp_path,
        snapshot=snapshot,
        db_path=tmp_path / "groundtruth.db",
        observer_results=results,
    )

    assert report["membership_complete"] is False
    assert report["counts"]["invalid_unknown"] == 1
    assert report["admission_candidates"] == []
    assert report["entries"][0]["relative_path"] == "."


def test_service_boundaries_virtual_declarations_and_links_are_not_followed(tmp_path: Path) -> None:
    (tmp_path / "member.txt").write_text("registered", encoding="utf-8")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "hidden").write_text("not inspected", encoding="utf-8")
    hosted = tmp_path / "applications" / "Demo"
    hosted.mkdir(parents=True)
    (hosted / "hidden.py").write_text("not inspected", encoding="utf-8")
    target = tmp_path / "link-target"
    target.mkdir()
    (target / "hidden.txt").write_text("not followed", encoding="utf-8")
    link = tmp_path / "linked"
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError:
        link = None
    snapshot = _snapshot(
        tmp_path,
        [
            _record("member", "member.txt"),
            _record("virtual", "membase:fixture", "virtual"),
        ],
    )

    report = reconcile_artifact_membership(
        tmp_path,
        snapshot=snapshot,
        db_path=tmp_path / "groundtruth.db",
        observer_results=_observer_results(),
        deep=True,
    )

    entries = {entry["relative_path"]: entry for entry in report["entries"]}
    assert entries[".git"]["traversal_state"] == "owned_service_boundary"
    assert ".git/hidden" not in entries
    assert entries["applications/Demo"]["traversal_state"] == "hosted_application_boundary"
    assert "applications/Demo/hidden.py" not in entries
    assert not any(
        entry["registry_id"] == "virtual" and entry["membership_class"] == "invalid_unknown"
        for entry in report["entries"]
    )
    if link is not None:
        assert entries["linked"]["traversal_state"] == "no_follow_boundary"
        assert "linked/hidden.txt" not in entries


def test_manifest_is_deterministic_across_observation_order(tmp_path: Path) -> None:
    (tmp_path / "member.txt").write_text("registered", encoding="utf-8")
    (tmp_path / "one.py").write_text("one\n", encoding="utf-8")
    (tmp_path / "two.py").write_text("two\n", encoding="utf-8")
    snapshot = _snapshot(tmp_path, [_record("member", "member.txt")])
    one = ArtifactObservation("one.py", "capability_inventory", "cap:one", "operative")
    two = ArtifactObservation("two.py", "governed_knowledge", "spec:two", "operative")

    first = reconcile_artifact_membership(
        tmp_path,
        snapshot=snapshot,
        db_path=tmp_path / "groundtruth.db",
        observer_results=_observer_results(one, two),
    )
    second = reconcile_artifact_membership(
        tmp_path,
        snapshot=snapshot,
        db_path=tmp_path / "groundtruth.db",
        observer_results=_observer_results(two, one),
    )

    assert first["candidate_manifest_sha256"] == second["candidate_manifest_sha256"]
    assert first["reconciliation_evidence_digest"] == second["reconciliation_evidence_digest"]
    assert first["admission_candidates"] == second["admission_candidates"]


def test_groundtruth_database_candidate_is_service_owned_opaque_identity(tmp_path: Path) -> None:
    (tmp_path / "member.txt").write_text("registered", encoding="utf-8")
    snapshot = _snapshot(tmp_path, [_record("member", "member.txt")])
    observation = ArtifactObservation(
        "groundtruth.db",
        "governed_knowledge",
        "context-manifest:groundtruth.db",
        "canonical MemBase service identity",
    )

    report = reconcile_artifact_membership(
        tmp_path,
        snapshot=snapshot,
        db_path=tmp_path / "groundtruth.db",
        observer_results=_observer_results(observation),
    )
    record = next(
        row["record"] for row in report["admission_candidates"] if row["record"]["storage_path"] == "groundtruth.db"
    )

    assert record["coverage_mode"] == "opaque_container"
    assert record["owner_role"] == "automated_only"
    assert record["versioning_policy"] == "append_only_versioned"


def test_dependency_observer_closes_transitively_from_typed_seed_paths(tmp_path: Path) -> None:
    (tmp_path / "member.txt").write_text("registered", encoding="utf-8")
    (tmp_path / "seed.py").write_text("# See `docs/one.md`\n", encoding="utf-8")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "one.md").write_text("See `config/final.toml`\n", encoding="utf-8")
    (tmp_path / "config").mkdir(exist_ok=True)
    (tmp_path / "config" / "final.toml").write_text("answer = 42\n", encoding="utf-8")
    snapshot = _snapshot(tmp_path, [_record("member", "member.txt")])

    result = observe_registered_dependency_closure(
        tmp_path,
        snapshot,
        tmp_path / "groundtruth.db",
        seed_paths=("seed.py",),
    )

    observed = {item.relative_path for item in result.observations}
    assert {"docs/one.md", "config/final.toml"} <= observed


def test_dependency_observer_rejects_runtime_scratch_and_opaque_payloads(tmp_path: Path) -> None:
    (tmp_path / "member.txt").write_text("registered", encoding="utf-8")
    (tmp_path / "seed.py").write_text(
        "\n".join(
            (
                "# `.gtkb-state/run.json`",
                "# `test-auth-root/bridge/x.md`",
                "# `groundtruth-kb/.venv/marker.txt`",
                "# `config/live.toml`",
            )
        ),
        encoding="utf-8",
    )
    for relative in (
        ".gtkb-state/run.json",
        "test-auth-root/bridge/x.md",
        "groundtruth-kb/.venv/marker.txt",
        "config/live.toml",
    ):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fixture\n", encoding="utf-8")
    snapshot = _snapshot(
        tmp_path,
        [
            _record("member", "member.txt"),
            _record("runtime", ".gtkb-state/", "opaque_container"),
        ],
    )

    result = observe_registered_dependency_closure(
        tmp_path,
        snapshot,
        tmp_path / "groundtruth.db",
        seed_paths=("seed.py",),
    )

    observed = {item.relative_path for item in result.observations}
    assert "config/live.toml" in observed
    assert ".gtkb-state/run.json" not in observed
    assert "test-auth-root/bridge/x.md" not in observed
    assert "groundtruth-kb/.venv/marker.txt" not in observed


def test_formal_approval_packets_use_one_recursive_service_container(tmp_path: Path) -> None:
    (tmp_path / "member.txt").write_text("registered", encoding="utf-8")
    approval = tmp_path / ".groundtruth" / "formal-artifact-approvals" / "packet.json"
    approval.parent.mkdir(parents=True)
    approval.write_text("{}\n", encoding="utf-8")
    snapshot = _snapshot(tmp_path, [_record("member", "member.txt")])
    root = ArtifactObservation(
        ".groundtruth/formal-artifact-approvals",
        "registered_dependency_closure",
        "managed_service_container:formal-artifact-approvals",
        "immutable formal-approval audit service container",
    )
    child = ArtifactObservation(
        ".groundtruth/formal-artifact-approvals/packet.json",
        "registered_dependency_closure",
        "registered_text:policy.md",
        "deterministic in-root reference",
    )

    report = reconcile_artifact_membership(
        tmp_path,
        snapshot=snapshot,
        db_path=tmp_path / "groundtruth.db",
        observer_results=_observer_results(root, child),
    )

    candidates = [row["record"] for row in report["admission_candidates"]]
    assert [row["storage_path"] for row in candidates] == [".groundtruth/formal-artifact-approvals/"]
    assert candidates[0]["coverage_mode"] == "recursive"
    assert not any(
        entry["relative_path"] == ".groundtruth/formal-artifact-approvals/packet.json" for entry in report["entries"]
    )


def test_proposed_service_container_text_participates_in_dependency_fixed_point(tmp_path: Path) -> None:
    (tmp_path / "member.txt").write_text("registered", encoding="utf-8")
    target = tmp_path / "scripts" / "live.py"
    target.parent.mkdir()
    target.write_text("pass\n", encoding="utf-8")
    approval = tmp_path / ".groundtruth" / "formal-artifact-approvals" / "packet.json"
    approval.parent.mkdir(parents=True)
    approval.write_text('{"source_path":"scripts/live.py"}\n', encoding="utf-8")
    snapshot = _snapshot(tmp_path, [_record("member", "member.txt")])

    result = observe_registered_dependency_closure(
        tmp_path,
        snapshot,
        tmp_path / "groundtruth.db",
    )

    observed = {item.relative_path for item in result.observations}
    assert ".groundtruth/formal-artifact-approvals" in observed
    assert "scripts/live.py" in observed
    assert ".groundtruth/formal-artifact-approvals/packet.json" not in observed


def test_exact_admission_reaches_membership_closure_without_audit_dependency(tmp_path: Path) -> None:
    (tmp_path / "member.txt").write_text("registered", encoding="utf-8")
    (tmp_path / "operative.py").write_text("pass\n", encoding="utf-8")
    original = [_record("member", "member.txt")]
    snapshot = _snapshot(tmp_path, original)
    observation = ArtifactObservation(
        "operative.py",
        "package_and_entrypoint",
        "pyproject:testpaths",
        "build-selected test member",
    )
    observers = _observer_results(observation)
    before = reconcile_artifact_membership(
        tmp_path,
        snapshot=snapshot,
        db_path=tmp_path / "groundtruth.db",
        observer_results=observers,
    )
    candidate = SoTArtifact(**before["batch_records"][0])

    after_snapshot = _snapshot(tmp_path, [*original, candidate])
    after = reconcile_artifact_membership(
        tmp_path,
        snapshot=after_snapshot,
        db_path=tmp_path / "groundtruth.db",
        observer_results=observers,
    )

    assert after["membership_complete"] is True
    assert after["audit_complete"] is False
    assert after["audit_performed"] is False
    assert after["audit_gaps"] == [{"kind": "audit_not_performed"}]
    assert after["operational_liveness"] is True
    assert after["admission_candidates"] == []

    audited = reconcile_artifact_membership(
        tmp_path,
        snapshot=after_snapshot,
        db_path=tmp_path / "groundtruth.db",
        observer_results=observers,
        audit=True,
    )
    assert audited["membership_complete"] is True
    assert audited["audit_performed"] is True
    assert audited["audit_complete"] is False
    assert {gap["kind"] for gap in audited["audit_gaps"]} == {"missing_revision"}
