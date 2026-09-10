"""Specification-derived tests for typed artifact membership reconciliation."""

from __future__ import annotations

import os
import subprocess
from dataclasses import replace
from pathlib import Path

import groundtruth_kb.project.artifact_membership_reconciliation as membership
from groundtruth_kb.project.artifact_membership_reconciliation import (
    ArtifactObservation,
    ObserverResult,
    observe_package_and_entrypoint,
    observe_registered_dependency_closure,
    reconcile_artifact_membership,
)
from groundtruth_kb.project.registry_control_plane import load_registry_snapshot, serialize_registry
from groundtruth_kb.project.sot_registry import SoTArtifact


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
    registry.parent.mkdir(parents=True, exist_ok=True)
    payload = serialize_registry(records)
    registry.write_bytes(payload)
    return load_registry_snapshot(
        project_root=tmp_path,
        registry_path=registry,
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
    assert report["sweep_eligible"] is False
    assert report["release_eligible"] is False


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
    assert report["sweep_eligible"] is False
    assert report["release_eligible"] is False


def test_package_observer_includes_untracked_nonignored_members(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[tool.pytest.ini_options]\ntestpaths = ["tests"]\n',
        encoding="utf-8",
    )
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "tracked.py").write_text("pass\n", encoding="utf-8")
    (tests / "new.py").write_text("pass\n", encoding="utf-8")
    (tests / "ignored.py").write_text("pass\n", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("tests/ignored.py\n", encoding="utf-8")
    subprocess.run(["git", "init", "--quiet"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "add", "pyproject.toml", ".gitignore", "tests/tracked.py"],
        cwd=tmp_path,
        check=True,
    )

    result = observe_package_and_entrypoint(tmp_path, None, tmp_path / "groundtruth.db")  # type: ignore[arg-type]

    observed = {item.relative_path: item for item in result.observations}
    assert result.succeeded is True
    assert "tests/tracked.py" in observed
    assert "tests/new.py" in observed
    assert "tests/ignored.py" not in observed
    assert observed["tests/new.py"].evidence_source == "git_index_and_untracked_nonignored_enumeration"


def test_untracked_nonignored_candidate_uses_git_managed_policy_fields(tmp_path: Path) -> None:
    (tmp_path / "member.txt").write_text("registered", encoding="utf-8")
    candidate = tmp_path / "tests" / "new.py"
    candidate.parent.mkdir()
    candidate.write_text("pass\n", encoding="utf-8")
    subprocess.run(["git", "init", "--quiet"], cwd=tmp_path, check=True)
    snapshot = _snapshot(tmp_path, [_record("member", "member.txt")])
    observation = ArtifactObservation(
        "tests/new.py",
        "package_and_entrypoint",
        "git_index_and_untracked_nonignored_enumeration",
        "untracked nonignored package member",
    )

    report = reconcile_artifact_membership(
        tmp_path,
        snapshot=snapshot,
        db_path=tmp_path / "groundtruth.db",
        observer_results=_observer_results(observation),
    )
    record = report["admission_candidates"][0]["record"]

    assert record["storage_path"] == "tests/new.py"
    assert record["versioning_policy"] == "git_tracked"
    assert record["backup_policy"] == "git_tracked"
    assert record["restore_action"] == "git_restore"


def test_package_observer_fails_nonadmitting_when_git_inventory_is_unavailable(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[tool.pytest.ini_options]\ntestpaths = ["tests"]\n',
        encoding="utf-8",
    )
    candidate = tmp_path / "tests" / "candidate.py"
    candidate.parent.mkdir()
    candidate.write_text("pass\n", encoding="utf-8")
    monkeypatch.setattr(membership, "_git_managed_inventory", lambda _root: None)

    observer = observe_package_and_entrypoint(tmp_path, None, tmp_path / "groundtruth.db")  # type: ignore[arg-type]

    assert observer.succeeded is False
    assert observer.observations == ()
    assert observer.diagnostics == ("Git-managed inventory unavailable; package admission is disabled",)

    snapshot = _snapshot(tmp_path, [_record("member", "pyproject.toml")])
    report = reconcile_artifact_membership(
        tmp_path,
        snapshot=snapshot,
        db_path=tmp_path / "groundtruth.db",
        observer_results=(observer,),
    )
    assert report["membership_complete"] is False
    assert report["counts"]["invalid_unknown"] == 1
    assert report["admission_candidates"] == []


def test_unreadable_paths_preserve_registry_and_observer_authority(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "member.txt").write_text("registered", encoding="utf-8")
    for name in ("disposable", "observed", "registered"):
        (tmp_path / name).mkdir()
    snapshot = _snapshot(
        tmp_path,
        [
            _record("member", "member.txt"),
            _record("registered", "registered"),
        ],
    )
    original_scandir = os.scandir

    def blocked_scandir(path):
        if Path(path).name in {"disposable", "observed", "registered"}:
            raise PermissionError("fixture unreadable directory")
        return original_scandir(path)

    monkeypatch.setattr(os, "scandir", blocked_scandir)
    report = reconcile_artifact_membership(
        tmp_path,
        snapshot=snapshot,
        db_path=tmp_path / "groundtruth.db",
        observer_results=_observer_results(
            ArtifactObservation(
                "observed",
                "capability_inventory",
                "fixture:capability",
                "fixture operative surface",
            )
        ),
        deep=True,
    )

    entries = {entry["relative_path"]: entry for entry in report["entries"]}
    assert entries["disposable"]["membership_class"] == "unregistered_disposable"
    assert entries["observed"]["membership_class"] == "unregistered_load_bearing"
    assert entries["registered"]["membership_class"] == "invalid_unknown"
    assert report["counts"]["unregistered_load_bearing"] == 1
    assert report["counts"]["invalid_unknown"] == 1
    assert report["admission_candidates"] == []


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


def test_database_filename_does_not_establish_service_identity(tmp_path: Path) -> None:
    (tmp_path / "member.txt").write_text("registered", encoding="utf-8")
    database = tmp_path / "groundtruth.db"
    payload = b"unselected database fixture; inventory must not read it"
    database.write_bytes(payload)
    snapshot = _snapshot(tmp_path, [_record("member", "member.txt")])

    result = observe_registered_dependency_closure(tmp_path, snapshot, tmp_path / "selected.db")

    assert result.succeeded, result.diagnostics
    assert not any(item.relative_path == "groundtruth.db" for item in result.observations)
    assert database.read_bytes() == payload


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


def test_declared_opaque_service_keeps_payloads_out_of_admission(tmp_path: Path) -> None:
    payload = tmp_path / "runtime-store" / "internal.json"
    payload.parent.mkdir()
    payload.write_text("{}\n", encoding="utf-8")
    snapshot = _snapshot(tmp_path, [_record("store", "runtime-store/", "opaque_container")])
    observations = (
        ArtifactObservation("runtime-store", "governed_knowledge", "service:store", "declared service"),
        ArtifactObservation(
            "runtime-store/internal.json",
            "registered_dependency_closure",
            "registered_text:policy.md",
            "payload reference",
        ),
    )

    report = reconcile_artifact_membership(
        tmp_path,
        snapshot=snapshot,
        db_path=tmp_path / "absent.db",
        observer_results=_observer_results(*observations),
    )

    assert report["admission_candidates"] == []
    assert not any(entry["relative_path"] == "runtime-store/internal.json" for entry in report["entries"])
    assert payload.exists()


def test_formal_permission_payload_cannot_seed_dependency_scanning(tmp_path: Path) -> None:
    (tmp_path / "member.txt").write_text("registered", encoding="utf-8")
    target = tmp_path / "scripts" / "live.py"
    target.parent.mkdir()
    target.write_text("pass\n", encoding="utf-8")
    approval = tmp_path / ".groundtruth" / "formal-artifact-approvals" / "packet.json"
    approval.parent.mkdir(parents=True)
    approval.write_text('{"source_path":"scripts/live.py"}\n', encoding="utf-8")
    snapshot = _snapshot(tmp_path, [_record("member", "member.txt")])

    result = observe_registered_dependency_closure(tmp_path, snapshot, tmp_path / "absent.db")

    assert result.succeeded, result.diagnostics
    assert result.observations == ()
    assert approval.exists()


def test_archived_declaration_does_not_supply_current_dependencies(tmp_path: Path) -> None:
    target = tmp_path / "scripts" / "live.py"
    target.parent.mkdir()
    target.write_text("pass\n", encoding="utf-8")
    archived = replace(_record("old", "removed.md"), lifecycle="archive", depends_on=("scripts/live.py",))
    snapshot = _snapshot(tmp_path, [archived])

    result = observe_registered_dependency_closure(tmp_path, snapshot, tmp_path / "absent.db")

    assert result.succeeded, result.diagnostics
    assert result.observations == ()


def test_current_baseline_source_supplies_transitive_dependencies(tmp_path: Path) -> None:
    baseline = tmp_path / ".harness-baseline-configuration" / "rules" / "current.md"
    baseline.parent.mkdir(parents=True)
    baseline.write_text("Load `scripts/current.py`.\n", encoding="utf-8")
    script = tmp_path / "scripts" / "current.py"
    script.parent.mkdir()
    script.write_text("# Read `config/current.toml`\n", encoding="utf-8")
    config = tmp_path / "config" / "current.toml"
    config.parent.mkdir()
    config.write_text("answer = 42\n", encoding="utf-8")
    snapshot = _snapshot(tmp_path, [_record("baseline", ".harness-baseline-configuration/", "recursive")])

    result = observe_registered_dependency_closure(tmp_path, snapshot, tmp_path / "absent.db")

    assert result.succeeded, result.diagnostics
    assert {"scripts/current.py", "config/current.toml"} <= {item.relative_path for item in result.observations}


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
    assert after["identity_state"]["current"] is True
    assert not {"audit_complete", "audit_performed", "audit_gaps"} & after.keys()
    assert after["operational_liveness"] is True
    assert after["admission_candidates"] == []
    assert not (tmp_path / "groundtruth.db").exists()


def test_sweep_requires_present_registered_objects_and_complete_traversal(tmp_path: Path) -> None:
    (tmp_path / "member.txt").write_text("registered", encoding="utf-8")
    snapshot = _snapshot(
        tmp_path, [_record("member", "member.txt"), _record("registry", "config/registry/sot-artifacts.toml")]
    )
    complete = reconcile_artifact_membership(
        tmp_path, snapshot=snapshot, observer_results=_observer_results(), deep=True
    )
    assert complete["membership_complete"] is True
    assert complete["pruned_envelope_count"] == 0
    assert complete["sweep_eligible"] is True

    (tmp_path / "member.txt").unlink()
    missing = reconcile_artifact_membership(
        tmp_path, snapshot=snapshot, observer_results=_observer_results(), deep=True
    )
    assert missing["identity_state"]["missing"] == [{"id": "member", "path": "member.txt"}]
    assert missing["sweep_eligible"] is False
    assert missing["release_eligible"] is False

    (tmp_path / "member.txt").write_text("registered", encoding="utf-8")
    (tmp_path / "uninspected/deep").mkdir(parents=True)
    (tmp_path / "uninspected/deep/keep.txt").write_text("uninspected work", encoding="utf-8")
    pruned = reconcile_artifact_membership(tmp_path, snapshot=snapshot, observer_results=_observer_results())
    assert pruned["membership_complete"] is True
    assert pruned["pruned_envelope_count"] > 0
    assert pruned["sweep_eligible"] is False
    assert pruned["release_eligible"] is False
    assert (tmp_path / "uninspected/deep/keep.txt").read_text(encoding="utf-8") == "uninspected work"


def test_dependency_observer_does_not_promote_harness_output_or_formal_permission_records(tmp_path: Path) -> None:
    baseline = tmp_path / ".harness-baseline-configuration/rules/current.md"
    baseline.parent.mkdir(parents=True)
    baseline.write_text("A stale reference to `.claude/rules/old.md` is not a canonical source.\n", encoding="utf-8")
    projection = tmp_path / ".claude/rules/old.md"
    projection.parent.mkdir(parents=True)
    projection.write_text("obsolete generated guidance", encoding="utf-8")
    receipt = tmp_path / ".groundtruth/formal-artifact-approvals/old.json"
    receipt.parent.mkdir(parents=True)
    receipt.write_text('{"source_path":".claude/rules/old.md"}', encoding="utf-8")
    snapshot = _snapshot(tmp_path, [_record("baseline", ".harness-baseline-configuration/rules/current.md")])
    result = observe_registered_dependency_closure(tmp_path, snapshot, tmp_path / "absent.db")
    assert result.succeeded, result.diagnostics
    assert not any(
        item.relative_path.startswith((".claude/", ".groundtruth/formal-artifact-approvals"))
        for item in result.observations
    )
    assert projection.read_text(encoding="utf-8") == "obsolete generated guidance"
    assert receipt.exists()


def test_dependency_references_do_not_follow_an_in_root_junction(tmp_path: Path) -> None:
    source = tmp_path / "docs/current.md"
    source.parent.mkdir()
    source.write_text("See `docs/linked/payload.md`.\n", encoding="utf-8")
    payload = tmp_path / "private/payload.md"
    payload.parent.mkdir()
    payload.write_text("not a current source", encoding="utf-8")
    linked = tmp_path / "docs/linked"
    if os.name == "nt":
        subprocess.run(["cmd", "/c", "mklink", "/J", str(linked), str(payload.parent)], check=True, capture_output=True)
    else:
        linked.symlink_to(payload.parent, target_is_directory=True)
    snapshot = _snapshot(tmp_path, [_record("current", "docs/current.md")])

    result = observe_registered_dependency_closure(tmp_path, snapshot, tmp_path / "absent.db")

    assert result.succeeded, result.diagnostics
    assert not result.observations
    assert payload.read_text(encoding="utf-8") == "not a current source"


def test_dependency_observer_reports_unreadable_current_source(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "docs/current.md"
    source.parent.mkdir()
    source.write_text("Current instructions", encoding="utf-8")
    snapshot = _snapshot(tmp_path, [_record("current", "docs/current.md")])
    original = Path.read_bytes

    def unreadable(path):
        if path == source:
            raise PermissionError("Current source is unreadable")
        return original(path)

    monkeypatch.setattr(Path, "read_bytes", unreadable)
    result = observe_registered_dependency_closure(tmp_path, snapshot, tmp_path / "absent.db")

    assert not result.succeeded
    assert not result.observations
    assert any("Current source is unreadable" in diagnostic for diagnostic in result.diagnostics)


def test_dependency_observer_does_not_drop_references_in_large_current_sources(tmp_path: Path) -> None:
    source = tmp_path / "docs/current.md"
    source.parent.mkdir()
    source.write_text("current instructions\n" * 100_000 + "See `scripts/current.py`.\n", encoding="utf-8")
    target = tmp_path / "scripts/current.py"
    target.parent.mkdir()
    target.write_text("pass\n", encoding="utf-8")
    snapshot = _snapshot(tmp_path, [_record("current", "docs/current.md")])

    result = observe_registered_dependency_closure(tmp_path, snapshot, tmp_path / "absent.db")

    assert result.succeeded, result.diagnostics
    assert "scripts/current.py" in {item.relative_path for item in result.observations}
