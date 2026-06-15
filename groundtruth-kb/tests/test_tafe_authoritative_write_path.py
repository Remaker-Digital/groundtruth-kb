# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Failure-injection tests for the WI-4510 Phase-3 ``tafe_canonical`` write path.

These tests exercise the cross-store fail-closed publish contract from
``bridge/gtkb-wi4510-phase-3-authority-flip-003.md`` (Loyal Opposition GO at
``-004``), governed by ``ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001`` and
``DCL-INDEX-GENERATED-VIEW-001``. Each test derives from a DCL assertion or one
of the three failure scenarios the prior NO-GO (``-002``) required:

* #6  cross-store write order (verify before commit before publish) — AST.
* #7  single DB commit per authoritative write — AST.
* #8  fail-closed pre-commit divergence (Codex scenario 1) — nothing written.
* #9  recoverable TAFE-ahead is the only post-commit failure (Codex scenario 2).
* #10 publish-reconcile is lossless + idempotent.
* #11 INDEX-ahead quarantine.
* Codex scenario 3 — next-writer-guard repair + revert after a mid-publish split.
* atomicity regression — the independent-commit hazard is removed (rollback).
* ``index_canonical`` byte-identity + no shadow write on the default path
  (``GOV-FILE-BRIDGE-AUTHORITY-001`` v2 read-surface preservation).

The default-direction safe default and reversibility backstop (DCL #3 / #4) are
covered by ``test_bridge_authority_direction.py``.
"""

from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.tafe_bridge_ingestion import (
    ARTIFACT_TYPE,
    assess_publish_state,
    ingest_bridge_index,
    make_archived_extra_oracle,
)
from groundtruth_kb.typed_artifact_flow import TypedArtifactFlowService

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


# ── module loading (scripts/ modules are not importable as a package) ──


def _load_scripts_module(name: str) -> ModuleType:
    if name in sys.modules:
        return sys.modules[name]
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    path = SCRIPTS_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


biw = _load_scripts_module("bridge_index_writer")
cutover = _load_scripts_module("bridge_authority_cutover")
tafe_ingestion = sys.modules["groundtruth_kb.tafe_bridge_ingestion"]


# ── fixtures / builders ──


def _index(*blocks: tuple[str, list[tuple[str, int]]]) -> str:
    """Build canonical ``bridge/INDEX.md`` text from (slug, [(status, version)])."""
    parts = ["# Bridge INDEX\n", "\n"]
    for slug, lines in blocks:
        parts.append(f"Document: {slug}\n")
        for status, version in lines:
            parts.append(f"{status}: bridge/{slug}-{version:03d}.md\n")
        parts.append("\n")
    return "".join(parts)


def _open(root: Path) -> tuple[KnowledgeDB, TypedArtifactFlowService]:
    db = KnowledgeDB(root / "groundtruth.db")
    return db, TypedArtifactFlowService(db)


def _state_dir(root: Path) -> Path:
    return root / ".gtkb-state" / "bridge-index-writer"


def _setup_tafe_project(
    tmp_path: Path,
    *blocks: tuple[str, list[tuple[str, int]]],
    direction: str = "tafe_canonical",
    ingest: bool = True,
) -> tuple[Path, Path]:
    """Build a project whose shadow mirrors the INDEX, then set the direction.

    Mirrors the real cutover precondition (a GREEN final re-ingest before the
    flip), so the write-start reconcile guard sees an in-sync surface.
    """
    root = tmp_path
    bridge_dir = root / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)
    index_text = _index(*blocks)
    index_path = bridge_dir / "INDEX.md"
    index_path.write_text(index_text, encoding="utf-8")
    for slug, lines in blocks:
        for status, version in lines:
            (bridge_dir / f"{slug}-{version:03d}.md").write_text(f"{status}\n", encoding="utf-8")
    db, service = _open(root)
    service.seed_reviewed_task_flow_definitions(changed_by="test", change_reason="seed")
    if ingest:
        ingest_bridge_index(index_text, service, apply=True, changed_by="test")
    db.close()
    if direction is not None:
        cutover.write_authority_direction(root, direction)
    return root, index_path


def _mutate_prepend_status(slug: str, status: str, version: int):
    """A mutate that inserts a status line at the top of an existing block."""
    line = f"{status}: bridge/{slug}-{version:03d}.md\n"

    def mutate(current: str) -> str:
        out: list[str] = []
        inserted = False
        for raw in current.splitlines(keepends=True):
            out.append(raw)
            if not inserted and raw.strip() == f"Document: {slug}":
                out.append(line)
                inserted = True
        if not inserted:
            raise AssertionError(f"Document: {slug} not found in INDEX")
        return "".join(out)

    return mutate


def _run_write(root: Path, index_path: Path, mutate) -> str:
    return biw.atomic_index_update(index_path, mutate, state_dir=_state_dir(root), project_root=root)


# ── AST helpers (DCL #6 / #7) ──


def _function_calls(func_name: str) -> list[tuple[str, int]]:
    """Return (call_name, lineno) for calls inside the named top-level function."""
    source = Path(biw.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    target = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == func_name)
    calls: list[tuple[str, int]] = []
    for node in ast.walk(target):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                calls.append((func.id, node.lineno))
            elif isinstance(func, ast.Attribute):
                calls.append((func.attr, node.lineno))
    return calls


def _first_lineno(calls: list[tuple[str, int]], name: str) -> int:
    linenos = [lineno for call_name, lineno in calls if call_name == name]
    assert linenos, f"expected a call to {name!r} in the function"
    return min(linenos)


# ── DCL #6: cross-store write order (verify -> commit -> publish) ──


def test_write_order_verify_before_commit_before_publish() -> None:
    """The tafe_canonical branch verifies before committing and commits before publishing."""
    calls = _function_calls("_tafe_canonical_publish")
    verify_at = _first_lineno(calls, "assess_publish_state")
    commit_at = _first_lineno(calls, "insert_bridge_thread_atomic")
    publish_at = _first_lineno(calls, "_atomic_write")
    assert verify_at < commit_at < publish_at, (
        f"expected verify({verify_at}) < commit({commit_at}) < publish({publish_at})"
    )


# ── DCL #7: single DB commit per authoritative write ──


def test_write_path_uses_atomic_helper_not_per_row_inserters() -> None:
    """The tafe_canonical path commits via insert_bridge_thread_atomic, never the per-row inserters."""
    call_names = {name for name, _ in _function_calls("_tafe_canonical_publish")}
    assert "insert_bridge_thread_atomic" in call_names
    assert "insert_flow_instance" not in call_names
    assert "insert_flow_artifact" not in call_names


# ── ADR authority flip + DCL #2: happy path records the artifact + regenerates byte-faithful ──


def test_tafe_canonical_write_records_artifact_and_regenerates(tmp_path: Path) -> None:
    root, index_path = _setup_tafe_project(tmp_path, ("alpha", [("NEW", 1)]))
    (root / "bridge" / "alpha-002.md").write_text("GO\n", encoding="utf-8")

    published = _run_write(root, index_path, _mutate_prepend_status("alpha", "GO", 2))

    # the new authoritative version line is in the published INDEX
    assert "GO: bridge/alpha-002.md" in published
    assert index_path.read_text(encoding="utf-8") == published

    db, service = _open(root)
    try:
        artifact = service.get_flow_artifact("fa-bridge-alpha-002")
        assert artifact is not None
        assert artifact["metadata_parsed"]["status_token"] == "GO"
        # and the regenerated INDEX is a faithful view of the shadow
        instances = service.list_flow_instances()
        artifacts = service.list_flow_artifacts(artifact_type=ARTIFACT_TYPE)
        verdict = assess_publish_state(
            published, instances, artifacts, is_archived_extra=make_archived_extra_oracle(root)
        )
        assert verdict.in_sync, verdict.regen_verify.as_dict()
    finally:
        db.close()


# ── DCL #8 / Codex scenario 1: pre-commit divergence writes nothing ──


def test_divergence_before_publish_writes_nothing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, index_path = _setup_tafe_project(tmp_path, ("alpha", [("NEW", 1)]))
    before_index = index_path.read_text(encoding="utf-8")

    # Force the planner to capture NOTHING while the intended write adds a line:
    # the regenerated INDEX then omits the intended GO line -> verify diverges.
    monkeypatch.setattr(tafe_ingestion, "plan_bridge_thread_writes", lambda *a, **k: [])

    with pytest.raises(biw.CrossStorePublishError):
        _run_write(root, index_path, _mutate_prepend_status("alpha", "GO", 2))

    # Nothing written: INDEX byte-identical, direction unchanged, no shadow row.
    assert index_path.read_text(encoding="utf-8") == before_index
    assert cutover.read_authority_direction(root) == "tafe_canonical"
    db, service = _open(root)
    try:
        assert service.get_flow_artifact("fa-bridge-alpha-002") is None
    finally:
        db.close()


# ── DCL #9 / Codex scenario 2: publish failure after commit leaves recoverable TAFE-ahead ──


def test_publish_failure_after_commit_is_recoverable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, index_path = _setup_tafe_project(tmp_path, ("alpha", [("NEW", 1)]))
    (root / "bridge" / "alpha-002.md").write_text("GO\n", encoding="utf-8")
    before_index = index_path.read_text(encoding="utf-8")

    def _raise(*_args, **_kwargs):
        raise OSError("simulated publish failure after commit")

    monkeypatch.setattr(biw, "_atomic_write", _raise)

    with pytest.raises(OSError, match="simulated publish failure"):
        _run_write(root, index_path, _mutate_prepend_status("alpha", "GO", 2))

    # INDEX is untouched (fully-old, never torn) ...
    assert index_path.read_text(encoding="utf-8") == before_index
    # ... but the full thread committed atomically (TAFE is one write ahead).
    db, service = _open(root)
    try:
        artifact = service.get_flow_artifact("fa-bridge-alpha-002")
        assert artifact is not None  # committed despite the publish failure
        instances = service.list_flow_instances()
        artifacts = service.list_flow_artifacts(artifact_type=ARTIFACT_TYPE)
        verdict = assess_publish_state(
            index_path.read_text(encoding="utf-8"),
            instances,
            artifacts,
            is_archived_extra=make_archived_extra_oracle(root),
        )
        # The split is TAFE-ahead (repairable), never INDEX-ahead, never missing.
        assert verdict.state == "tafe_ahead"
        assert not verdict.regen_verify.missing_in_generated
    finally:
        db.close()


# ── DCL #10: publish-reconcile is lossless + idempotent ──


def test_publish_reconcile_heals_losslessly_and_is_idempotent(tmp_path: Path) -> None:
    root, index_path = _setup_tafe_project(tmp_path, ("alpha", [("NEW", 1)]))

    # Manufacture a TAFE-ahead split: commit a new artifact to the shadow without publishing.
    db, service = _open(root)
    try:
        rows_before = len(service.list_flow_artifacts(artifact_type=ARTIFACT_TYPE))
        db.insert_bridge_thread_atomic(
            [],
            [
                {
                    "id": "fa-bridge-alpha-002",
                    "flow_instance_id": "flow-bridge-alpha",
                    "artifact_type": ARTIFACT_TYPE,
                    "artifact_ref": "bridge/alpha-002.md",
                    "relationship": "version",
                    "metadata": {"status_token": "GO"},
                }
            ],
            changed_by="test",
            change_reason="manufacture TAFE-ahead split",
        )
        rows_after_commit = len(service.list_flow_artifacts(artifact_type=ARTIFACT_TYPE))
    finally:
        db.close()
    assert rows_after_commit == rows_before + 1

    # First reconcile heals the split (republishes INDEX from the shadow).
    first = biw.reconcile_publish(root)
    assert first["state"] == "tafe_ahead"
    assert first["repaired"] is True
    assert "GO: bridge/alpha-002.md" in index_path.read_text(encoding="utf-8")

    # No shadow row was deleted by recovery.
    db, service = _open(root)
    try:
        assert len(service.list_flow_artifacts(artifact_type=ARTIFACT_TYPE)) == rows_after_commit
    finally:
        db.close()

    # Second reconcile is a no-op (idempotent).
    second = biw.reconcile_publish(root)
    assert second["state"] == "in_sync"
    assert second["repaired"] is False


# ── DCL #11: INDEX-ahead is quarantined, never auto-applied ──


def test_index_ahead_is_quarantined(tmp_path: Path) -> None:
    root, index_path = _setup_tafe_project(tmp_path, ("alpha", [("NEW", 1)]))

    # Plant a whole thread in the INDEX that the authoritative shadow never recorded.
    contaminated = index_path.read_text(encoding="utf-8") + "Document: phantom\nNEW: bridge/phantom-001.md\n\n"
    index_path.write_text(contaminated, encoding="utf-8")

    result = biw.reconcile_publish(root)
    assert result["state"] == "index_ahead"
    assert result["repaired"] is False
    assert result["index_ahead"] is True
    # The contamination is NOT auto-applied / silently dropped: the INDEX is left as-is
    # for owner/LO disposition.
    assert index_path.read_text(encoding="utf-8") == contaminated


def test_assess_classifies_per_version_index_ahead(tmp_path: Path) -> None:
    """A shared thread whose INDEX carries a version the shadow lacks is INDEX-ahead."""
    root, _ = _setup_tafe_project(tmp_path, ("alpha", [("NEW", 1)]))
    index_with_extra_version = _index(("alpha", [("GO", 2), ("NEW", 1)]))
    db, service = _open(root)
    try:
        instances = service.list_flow_instances()
        artifacts = service.list_flow_artifacts(artifact_type=ARTIFACT_TYPE)
    finally:
        db.close()
    verdict = assess_publish_state(
        index_with_extra_version, instances, artifacts, is_archived_extra=make_archived_extra_oracle(root)
    )
    assert verdict.index_ahead
    assert verdict.state == "index_ahead"


# ── Codex scenario 3: the next writer's guard repairs a leftover split before its own write ──


def test_next_writer_guard_repairs_leftover_split(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, index_path = _setup_tafe_project(tmp_path, ("alpha", [("NEW", 1)]))
    (root / "bridge" / "alpha-002.md").write_text("GO\n", encoding="utf-8")
    (root / "bridge" / "beta-001.md").write_text("NEW\n", encoding="utf-8")
    before_index = index_path.read_text(encoding="utf-8")

    # Crash the first write at publish (commit lands, INDEX stays old): a TAFE-ahead split.
    monkeypatch.setattr(biw, "_atomic_write", lambda *a, **k: (_ for _ in ()).throw(OSError("boom")))
    with pytest.raises(OSError):
        _run_write(root, index_path, _mutate_prepend_status("alpha", "GO", 2))
    assert index_path.read_text(encoding="utf-8") == before_index  # unpublished

    # Restore the real writer; a *new* write's write-start guard heals the leftover split
    # before applying its own change.
    monkeypatch.undo()

    def _add_beta(current: str) -> str:
        lines = current.splitlines(keepends=True)
        idx = next((i for i, line in enumerate(lines) if line.startswith("Document: ")), len(lines))
        block = "Document: beta\nNEW: bridge/beta-001.md\n\n"
        return "".join(lines[:idx]) + block + "".join(lines[idx:])

    published = _run_write(root, index_path, _add_beta)

    # The leftover alpha GO line is healed AND the new beta thread is applied.
    assert "GO: bridge/alpha-002.md" in published
    assert "Document: beta" in published
    db, service = _open(root)
    try:
        instances = service.list_flow_instances()
        artifacts = service.list_flow_artifacts(artifact_type=ARTIFACT_TYPE)
        verdict = assess_publish_state(
            published, instances, artifacts, is_archived_extra=make_archived_extra_oracle(root)
        )
        assert verdict.in_sync, verdict.regen_verify.as_dict()
    finally:
        db.close()


def test_revert_after_split_restores_index_canonical(tmp_path: Path) -> None:
    """revert flips back to index_canonical and can restore the frozen INDEX copy."""
    root, index_path = _setup_tafe_project(tmp_path, ("alpha", [("NEW", 1)]), direction=None)
    pre_flip = index_path.read_text(encoding="utf-8")
    frozen = cutover.flip_to_tafe_canonical(root)
    try:
        assert cutover.read_authority_direction(root) == "tafe_canonical"
        index_path.write_text("SUSPECT POST-FLIP STATE\n", encoding="utf-8")
        cutover.revert_to_index_canonical(root, restore_frozen=frozen)
        assert cutover.read_authority_direction(root) == "index_canonical"
        assert index_path.read_text(encoding="utf-8") == pre_flip
    finally:
        import os

        os.chmod(frozen, 0o644)


# ── atomicity regression: the independent-commit hazard is removed ──


def test_partial_thread_rolls_back(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A failure between the instance insert and an artifact insert rolls the whole thread back."""
    root, _ = _setup_tafe_project(tmp_path, ("alpha", [("NEW", 1)]), direction=None, ingest=False)
    db, service = _open(root)
    try:
        original_core = db._insert_flow_artifact_row

        def _raise_on_artifact(*_args, **_kwargs):
            raise RuntimeError("simulated mid-thread failure")

        monkeypatch.setattr(db, "_insert_flow_artifact_row", _raise_on_artifact)

        with pytest.raises(RuntimeError, match="simulated mid-thread failure"):
            db.insert_bridge_thread_atomic(
                [
                    {
                        "id": "flow-bridge-gamma",
                        "flow_definition_id": "implementation",
                        "subject_type": "bridge_thread",
                        "subject_id": "gamma",
                        "status": "in_review",
                        "metadata": {"shadow": True},
                    }
                ],
                [
                    {
                        "id": "fa-bridge-gamma-001",
                        "flow_instance_id": "flow-bridge-gamma",
                        "artifact_type": ARTIFACT_TYPE,
                        "artifact_ref": "bridge/gamma-001.md",
                        "relationship": "version",
                        "metadata": {"status_token": "NEW"},
                    }
                ],
                changed_by="test",
                change_reason="atomicity regression",
            )

        # The whole transaction rolled back: neither the instance nor the artifact exists.
        monkeypatch.setattr(db, "_insert_flow_artifact_row", original_core)
        assert service.get_flow_instance("flow-bridge-gamma") is None
        assert service.get_flow_artifact("fa-bridge-gamma-001") is None
    finally:
        db.close()


# ── index_canonical byte-identity + no shadow write (default path unchanged) ──


def test_index_canonical_is_byte_identical_and_writes_no_shadow(tmp_path: Path) -> None:
    root, index_path = _setup_tafe_project(tmp_path, ("alpha", [("NEW", 1)]), direction="index_canonical")
    original = index_path.read_text(encoding="utf-8")
    mutate = _mutate_prepend_status("alpha", "GO", 2)
    expected = mutate(original)

    written = _run_write(root, index_path, mutate)

    # byte-identical to a plain mutate+write — no regeneration / reformat.
    assert written == expected
    assert index_path.read_text(encoding="utf-8") == expected

    # the default path never touches the TAFE shadow.
    db, service = _open(root)
    try:
        assert service.get_flow_artifact("fa-bridge-alpha-002") is None
    finally:
        db.close()


def test_absent_direction_uses_index_canonical_path(tmp_path: Path) -> None:
    """No direction state file -> the safe-default index_canonical write path."""
    root, index_path = _setup_tafe_project(tmp_path, ("alpha", [("NEW", 1)]), direction=None)
    assert not cutover.direction_state_path(root).exists()
    original = index_path.read_text(encoding="utf-8")
    mutate = _mutate_prepend_status("alpha", "GO", 2)
    written = _run_write(root, index_path, mutate)
    assert written == mutate(original)
    db, service = _open(root)
    try:
        assert service.get_flow_artifact("fa-bridge-alpha-002") is None
    finally:
        db.close()
