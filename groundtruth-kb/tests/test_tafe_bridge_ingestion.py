"""Spec-derived tests for TAFE Slice C bridge-thread second-write ingestion.

Each test derives from a constraint of ``ADR-TAFE-SLICE-C-INGESTION-001``:

* D1 — every thread maps to the ``implementation`` flow; advisory-as-status.
* D2 — deterministic ``flow-bridge-<slug>`` / ``fa-bridge-<slug>-<NNN>`` identity.
* D3 — latest-token -> flow status, with the dual-``NEW`` disambiguation.
* D4 — fingerprint-gated, replay-safe idempotence.
* Scope — only ``flow_instances`` + ``flow_artifacts``; never ``stage_instances``
  / ``flow_events``.
* ``GOV-FILE-BRIDGE-AUTHORITY-001`` — the canonical INDEX is never written and the
  ingestion module holds no canonical-index path literal.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.tafe_bridge_ingestion import (
    _file_slug_from_path,
    _plan_thread,
    derive_flow_status,
    ingest_bridge_index,
)
from groundtruth_kb.tafe_index_sync import DocumentBlock, IndexVersionLine
from groundtruth_kb.typed_artifact_flow import TypedArtifactFlowService


def _index(*blocks: tuple[str, list[tuple[str, int]]]) -> str:
    """Build canonical ``bridge/INDEX.md`` text from (slug, [(status, version)])."""
    parts = ["# Bridge INDEX\n", "\n"]
    for slug, lines in blocks:
        parts.append(f"Document: {slug}\n")
        for status, version in lines:
            parts.append(f"{status}: bridge/{slug}-{version:03d}.md\n")
        parts.append("\n")
    return "".join(parts)


def _service(tmp_path: Path) -> tuple[KnowledgeDB, TypedArtifactFlowService]:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    service = TypedArtifactFlowService(db)
    service.seed_reviewed_task_flow_definitions(changed_by="test", change_reason="seed for ingestion test")
    return db, service


# --- D1: flow_definition selection + advisory-as-status -------------------------


def test_thread_maps_to_implementation_flow(tmp_path: Path) -> None:
    db, service = _service(tmp_path)
    try:
        ingest_bridge_index(_index(("alpha-thread", [("GO", 2), ("NEW", 1)])), service, apply=True)
        inst = service.get_flow_instance("flow-bridge-alpha-thread")
        assert inst is not None
        assert inst["flow_definition_id"] == "implementation"
        assert inst["subject_type"] == "bridge_thread"
        assert inst["subject_id"] == "alpha-thread"
        assert inst["status"] == "in_implementation"
        assert inst["metadata_parsed"]["shadow"] is True
    finally:
        db.close()


def test_advisory_thread_status_and_metadata(tmp_path: Path) -> None:
    db, service = _service(tmp_path)
    try:
        ingest_bridge_index(_index(("advice-thread", [("ADVISORY", 1)])), service, apply=True)
        inst = service.get_flow_instance("flow-bridge-advice-thread")
        assert inst is not None
        assert inst["flow_definition_id"] == "implementation"
        assert inst["status"] == "advisory"
        assert inst["metadata_parsed"]["bridge_kind"] == "advisory"
    finally:
        db.close()


# --- D2: deterministic instance + per-version artifact identity -----------------


def test_deterministic_instance_and_artifact_ids(tmp_path: Path) -> None:
    db, service = _service(tmp_path)
    try:
        ingest_bridge_index(_index(("beta-thread", [("GO", 2), ("NEW", 1)])), service, apply=True)
        assert service.get_flow_instance("flow-bridge-beta-thread") is not None
        artifacts = {a["id"]: a for a in service.list_flow_artifacts(flow_instance_id="flow-bridge-beta-thread")}
        assert set(artifacts) == {"fa-bridge-beta-thread-001", "fa-bridge-beta-thread-002"}
        latest = artifacts["fa-bridge-beta-thread-002"]
        assert latest["artifact_type"] == "bridge_version"
        assert latest["artifact_ref"] == "bridge/beta-thread-002.md"
        assert latest["relationship"] == "version"
        assert latest["metadata_parsed"]["status_token"] == "GO"
        assert artifacts["fa-bridge-beta-thread-001"]["metadata_parsed"]["status_token"] == "NEW"
    finally:
        db.close()


# --- D3: latest-token -> flow status (table) ------------------------------------


@pytest.mark.parametrize(
    "token,expected",
    [
        ("REVISED", "in_review"),
        ("GO", "in_implementation"),
        ("NO-GO", "in_revision"),
        ("VERIFIED", "complete"),
        ("WITHDRAWN", "withdrawn"),
        ("ADVISORY", "advisory"),
        ("DEFERRED", "deferred"),
        ("ACCEPTED", "unknown"),
    ],
)
def test_status_token_to_flow_status(tmp_path: Path, token: str, expected: str) -> None:
    db, service = _service(tmp_path)
    try:
        ingest_bridge_index(_index(("tok-thread", [(token, 1)])), service, apply=True)
        inst = service.get_flow_instance("flow-bridge-tok-thread")
        assert inst is not None
        assert inst["status"] == expected
        # The pure mapping (no prior GO) agrees with the written row.
        assert derive_flow_status(token, has_prior_go=False) == expected
    finally:
        db.close()


# --- D3: dual-NEW disambiguation ------------------------------------------------


def test_new_after_go_is_in_verification(tmp_path: Path) -> None:
    db, service = _service(tmp_path)
    try:
        # A post-implementation report: latest NEW (v3) filed after a prior GO (v2).
        ingest_bridge_index(_index(("report-thread", [("NEW", 3), ("GO", 2), ("NEW", 1)])), service, apply=True)
        inst = service.get_flow_instance("flow-bridge-report-thread")
        assert inst is not None
        assert inst["status"] == "in_verification"
        assert inst["metadata_parsed"]["bridge_kind"] == "implementation_report"
    finally:
        db.close()


def test_new_without_go_is_in_review(tmp_path: Path) -> None:
    db, service = _service(tmp_path)
    try:
        ingest_bridge_index(_index(("proposal-thread", [("NEW", 1)])), service, apply=True)
        inst = service.get_flow_instance("flow-bridge-proposal-thread")
        assert inst is not None
        assert inst["status"] == "in_review"
        assert inst["metadata_parsed"]["bridge_kind"] == "implementation_proposal"
    finally:
        db.close()


# --- D4: replay-safe idempotence ------------------------------------------------


def test_reingest_unchanged_index_is_noop(tmp_path: Path) -> None:
    db, service = _service(tmp_path)
    try:
        text = _index(("idem-thread", [("GO", 2), ("NEW", 1)]))
        first = ingest_bridge_index(text, service, apply=True)
        assert first.instances_written == 1
        assert first.artifacts_written == 2

        second = ingest_bridge_index(text, service, apply=True)
        assert second.instances_written == 0
        assert second.artifacts_written == 0

        assert len(service.get_flow_instance_history("flow-bridge-idem-thread")) == 1
        assert len(service.list_flow_artifacts(flow_instance_id="flow-bridge-idem-thread")) == 2
    finally:
        db.close()


def test_state_change_appends_one_version(tmp_path: Path) -> None:
    db, service = _service(tmp_path)
    try:
        ingest_bridge_index(_index(("evolve-thread", [("NEW", 1)])), service, apply=True)
        assert len(service.get_flow_instance_history("flow-bridge-evolve-thread")) == 1
        assert service.get_flow_instance("flow-bridge-evolve-thread")["status"] == "in_review"

        result = ingest_bridge_index(_index(("evolve-thread", [("GO", 2), ("NEW", 1)])), service, apply=True)
        assert result.instances_written == 1
        assert result.artifacts_written == 1  # only the new GO v2 line

        history = service.get_flow_instance_history("flow-bridge-evolve-thread")
        assert len(history) == 2  # exactly one new version appended
        assert service.get_flow_instance("flow-bridge-evolve-thread")["status"] == "in_implementation"
        assert len(service.list_flow_artifacts(flow_instance_id="flow-bridge-evolve-thread")) == 2
    finally:
        db.close()


# --- Scope exclusion: no stage_instances / flow_events --------------------------


def test_no_stage_instances_or_events_written(tmp_path: Path) -> None:
    db, service = _service(tmp_path)
    try:
        text = _index(
            ("scope-thread-a", [("VERIFIED", 2), ("NEW", 1)]),
            ("scope-thread-b", [("ADVISORY", 1)]),
        )
        ingest_bridge_index(text, service, apply=True)
        assert service.list_stage_instances() == []
        assert service.list_flow_events() == []
    finally:
        db.close()


# --- GOV-FILE-BRIDGE-AUTHORITY-001: no canonical-index write/literal ------------


def test_ingestion_does_not_write_canonical_index(tmp_path: Path) -> None:
    db, service = _service(tmp_path)
    try:
        result = ingest_bridge_index(_index(("noindex-thread", [("GO", 2), ("NEW", 1)])), service, apply=True)
    finally:
        db.close()
    # The shadow ingest wrote flow rows but the canonical index is never touched
    # (the module reads no file; the CLI owns the guarded read). End-to-end
    # byte-fidelity of bridge/INDEX.md is asserted in the CLI tests below.
    assert result.applied is True
    assert result.instances_written == 1


def test_ingestion_module_holds_no_canonical_index_path_literal() -> None:
    """The module embeds no canonical-index path literal in executable code.

    Docstring prose that *describes* ``bridge/INDEX.md`` is allowed; the
    prohibition (ADR scope, per the GO note) is on a code path literal that would
    read or write the canonical index. We parse the AST and exclude docstrings.
    """
    import ast

    import groundtruth_kb.tafe_bridge_ingestion as ingestion_module

    source = Path(ingestion_module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)

    docstrings = {
        ast.get_docstring(node, clean=False)
        for node in ast.walk(tree)
        if isinstance(node, ast.Module | ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef)
        and ast.get_docstring(node, clean=False) is not None
    }

    offending = [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and node.value not in docstrings
        and "index.md" in node.value.lower()
    ]
    assert offending == [], f"canonical-index path literal found in code: {offending}"


# --- CLI: dry-run default writes nothing; canonical index untouched -------------


def test_cli_ingest_dry_run_default_writes_nothing(runner: CliRunner, project_dir: Path) -> None:
    bridge_dir = project_dir / "bridge"
    bridge_dir.mkdir()
    index_file = bridge_dir / "INDEX.md"
    index_file.write_text(_index(("cli-thread", [("GO", 2), ("NEW", 1)])), encoding="utf-8")
    before = index_file.read_bytes()

    result = runner.invoke(
        main,
        ["--config", str(project_dir / "groundtruth.toml"), "flow", "ingest-bridge-index", "--json"],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "dry_run"
    assert payload["applied"] is False
    assert payload["mutated"] is False

    db = KnowledgeDB(project_dir / "groundtruth.db")
    try:
        assert db.get_flow_instance("flow-bridge-cli-thread") is None
        assert db.list_flow_artifacts(flow_instance_id="flow-bridge-cli-thread") == []
    finally:
        db.close()

    assert index_file.read_bytes() == before  # canonical INDEX byte-identical


# --- WI-4574: ingestion phantom-guard (Document-name vs file-slug consistency) --
#
# Derived from the ``ADR-TAFE-SLICE-C-INGESTION-001`` D2 identity contract: a
# thread's ``subject_id`` (``Document:`` name) must be consistent with the slug of
# its version-line ``artifact_ref``. A mismatch (the historical ``sp1`` phantom)
# must never create a mismatched-``subject_id`` orphan flow_instance.


def test_mismatched_document_name_is_skipped(tmp_path: Path) -> None:
    """A ``Document:`` block whose name != its version-line file slug is skipped.

    Regression for the WI-4574 phantom orphan: a malformed block named
    ``sp1-dispatch-reliability-prime-handoff`` pointing at the correctly-slugged
    ``bridge/gtkb-sp1-...`` file must not create a mismatched-``subject_id``
    flow_instance; the block name is recorded in ``threads_skipped``.
    """
    db, service = _service(tmp_path)
    try:
        index_text = (
            "# Bridge INDEX\n\n"
            "Document: sp1-dispatch-reliability-prime-handoff\n"
            "NEW: bridge/gtkb-sp1-dispatch-reliability-prime-handoff-001.md\n\n"
        )
        result = ingest_bridge_index(index_text, service, apply=True)
        assert "sp1-dispatch-reliability-prime-handoff" in result.threads_skipped
        assert service.get_flow_instance("flow-bridge-sp1-dispatch-reliability-prime-handoff") is None
        # No instance is created under the file slug either: the guard skips the
        # whole malformed block rather than silently rewriting its identity.
        assert service.get_flow_instance("flow-bridge-gtkb-sp1-dispatch-reliability-prime-handoff") is None
        assert result.instances_written == 0
    finally:
        db.close()


def test_matching_document_name_ingests_unchanged(tmp_path: Path) -> None:
    """A ``Document:`` block whose name matches its version-line file slug ingests.

    The guard skips ONLY clear mismatches; a consistent block is unaffected.
    """
    db, service = _service(tmp_path)
    try:
        index_text = (
            "# Bridge INDEX\n\n"
            "Document: gtkb-sp1-dispatch-reliability-prime-handoff\n"
            "NEW: bridge/gtkb-sp1-dispatch-reliability-prime-handoff-001.md\n\n"
        )
        result = ingest_bridge_index(index_text, service, apply=True)
        assert "gtkb-sp1-dispatch-reliability-prime-handoff" not in result.threads_skipped
        inst = service.get_flow_instance("flow-bridge-gtkb-sp1-dispatch-reliability-prime-handoff")
        assert inst is not None
        assert inst["subject_id"] == "gtkb-sp1-dispatch-reliability-prime-handoff"
        assert result.instances_written == 1
    finally:
        db.close()


def test_file_slug_derivation_fails_open_on_unparseable_path() -> None:
    """``_file_slug_from_path`` returns the slug for a normal path, None otherwise.

    The Slice A version-line regex guarantees the ``bridge/<slug>-NNN.md`` shape
    for any parsed version line, so an unparseable ``latest.path`` cannot arise
    through the parser; the ``None`` (fail-open) branch is exercised here directly.
    """
    assert _file_slug_from_path("bridge/gtkb-sp1-dispatch-reliability-prime-handoff-001.md") == (
        "gtkb-sp1-dispatch-reliability-prime-handoff"
    )
    assert _file_slug_from_path("bridge/gtkb-spec-pipeline-f8-012.md") == "gtkb-spec-pipeline-f8"
    # No determinable ``-NNN.md`` version suffix -> not determinable -> fail open.
    assert _file_slug_from_path("bridge/oddball-thread.md") is None
    assert _file_slug_from_path("bridge/-001.md") is None
    assert _file_slug_from_path("bridge/no-extension") is None


def test_unparseable_version_path_is_not_skipped(tmp_path: Path) -> None:
    """Fail-open at the ``_plan_thread`` boundary: an unparseable path never skips.

    Drives ``_plan_thread`` directly with a hand-built ``DocumentBlock`` whose
    version-line path has no determinable ``-NNN.md`` suffix (a shape the parser
    itself would never emit). The block must still plan a flow_instance rather
    than be dropped, proving the guard skips ONLY clear, determinable mismatches.
    """
    db, service = _service(tmp_path)
    try:
        line = IndexVersionLine(
            status="NEW",
            path="bridge/oddball-thread.md",  # no -NNN.md suffix -> file slug undeterminable
            version=1,
            line_number=2,
            raw="NEW: bridge/oddball-thread.md\n",
        )
        block = DocumentBlock(
            name="oddball-thread",
            document_line_number=1,
            document_raw="Document: oddball-thread\n",
            body_raw=(line.raw,),
            version_lines=(line,),
            malformed_lines=(),
        )
        plan = _plan_thread(block, service)
        assert plan is not None  # fail-open: not skipped
        assert plan.slug == "oddball-thread"
        assert plan.flow_instance_id == "flow-bridge-oddball-thread"
    finally:
        db.close()


def test_cli_ingest_apply_writes_shadow_and_leaves_index(runner: CliRunner, project_dir: Path) -> None:
    bridge_dir = project_dir / "bridge"
    bridge_dir.mkdir()
    index_file = bridge_dir / "INDEX.md"
    index_file.write_text(_index(("cli-apply-thread", [("GO", 2), ("NEW", 1)])), encoding="utf-8")
    before = index_file.read_bytes()

    # The shadow write requires the seeded implementation flow_definition.
    db = KnowledgeDB(project_dir / "groundtruth.db")
    try:
        TypedArtifactFlowService(db).seed_reviewed_task_flow_definitions(changed_by="test", change_reason="cli seed")
    finally:
        db.close()

    result = runner.invoke(
        main,
        ["--config", str(project_dir / "groundtruth.toml"), "flow", "ingest-bridge-index", "--apply", "--json"],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "applied"
    assert payload["applied"] is True
    assert payload["instances_written"] == 1
    assert payload["artifacts_written"] == 2

    db = KnowledgeDB(project_dir / "groundtruth.db")
    try:
        inst = db.get_flow_instance("flow-bridge-cli-apply-thread")
        assert inst is not None
        assert inst["status"] == "in_implementation"
    finally:
        db.close()

    assert index_file.read_bytes() == before  # canonical INDEX byte-identical
