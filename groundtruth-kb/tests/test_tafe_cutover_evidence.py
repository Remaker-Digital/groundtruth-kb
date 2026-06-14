"""Spec-derived tests for TAFE cutover-evidence gathering (WI-4509).

Each test derives from a WI-4509 evidence category (and the read-only contract):

* **parallel-run parity** — the INDEX->shadow derivation reproduces one instance
  per Document block and one artifact per version line (ADR D1/D2/D3); a block
  that derives no instance is a parity gap.
* **completeness** — the Slice B oracle's lost/extra-block diff surfaces.
* **contention-zero (idempotence)** — a re-plan over the current INDEX writes
  nothing once the shadow is populated (ADR D4).
* **flow completion rates** — the derived flow_status distribution is reported.
* **compatibility-view fidelity** — the stored shadow reconstructs the INDEX
  latest-status; an injected shadow/INDEX divergence surfaces.
* **GOV-FILE-BRIDGE-AUTHORITY-001** — the CLI is read-only over the canonical
  INDEX (byte-identical) and the shadow, and the module holds no canonical-index
  path literal in executable code.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.tafe_bridge_ingestion import ingest_bridge_index
from groundtruth_kb.tafe_cutover_evidence import gather_cutover_evidence
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
    service.seed_reviewed_task_flow_definitions(changed_by="test", change_reason="seed for cutover-evidence test")
    return db, service


# --- Parallel-run parity (ADR D1/D2/D3) -----------------------------------------


def test_parity_one_instance_per_thread_one_artifact_per_version(tmp_path: Path) -> None:
    db, service = _service(tmp_path)
    try:
        text = _index(("alpha", [("GO", 2), ("NEW", 1)]), ("beta", [("NEW", 1)]))
        report = gather_cutover_evidence(text, service, project_root=tmp_path)
    finally:
        db.close()

    assert report.parity.index_threads == 2
    assert report.parity.derived_instances == 2
    assert report.parity.index_version_lines == 3
    assert report.parity.derived_artifacts == 3
    assert report.parity.parity_mismatches == ()
    assert report.parity.threads_skipped == ()
    assert report.parity.ok is True


def test_parity_mismatch_detected(tmp_path: Path) -> None:
    db, service = _service(tmp_path)
    try:
        # A Document block with no version lines derives no shadow instance.
        text = "Document: empty-thread\n\nDocument: real-thread\nNEW: bridge/real-thread-001.md\n\n"
        report = gather_cutover_evidence(text, service, project_root=tmp_path)
    finally:
        db.close()

    assert "empty-thread" in report.parity.threads_skipped
    mismatch_slugs = {item["slug"] for item in report.parity.parity_mismatches}
    assert "empty-thread" in mismatch_slugs
    assert report.parity.ok is False
    assert report.ok is False


# --- Completeness (Slice B oracle integration) ----------------------------------


def test_completeness_surfaces_lost_and_extra_blocks(tmp_path: Path) -> None:
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    # Lost block: a bridge file on disk with no INDEX Document: entry.
    (bridge_dir / "lost-thread-001.md").write_text("NEW\n", encoding="utf-8")

    db, service = _service(tmp_path)
    try:
        # Extra block: an INDEX entry with no bridge file on disk.
        text = _index(("extra-thread", [("NEW", 1)]))
        report = gather_cutover_evidence(text, service, project_root=tmp_path)
    finally:
        db.close()

    assert "lost-thread" in report.lost_blocks
    assert "extra-thread" in report.extra_blocks
    assert report.ok is False


# --- Contention-zero / idempotence (ADR D4) -------------------------------------


def test_contention_zero_repeat_plan_writes_nothing(tmp_path: Path) -> None:
    db, service = _service(tmp_path)
    try:
        text = _index(("idem", [("GO", 2), ("NEW", 1)]))
        ingest_bridge_index(text, service, apply=True)  # populate the shadow
        report = gather_cutover_evidence(text, service, project_root=tmp_path)
    finally:
        db.close()

    assert report.contention.contention_zero is True
    assert report.contention.replan_instances_written == 0
    assert report.contention.replan_artifacts_written == 0
    assert report.contention.action_distribution == {"unchanged": 1}


def test_contention_nonzero_when_shadow_unpopulated(tmp_path: Path) -> None:
    db, service = _service(tmp_path)
    try:
        # No apply: the dry-run plan would create the instance, so contention != 0.
        text = _index(("fresh", [("GO", 2), ("NEW", 1)]))
        report = gather_cutover_evidence(text, service, project_root=tmp_path)
    finally:
        db.close()

    assert report.contention.contention_zero is False
    assert report.contention.replan_instances_written == 1
    assert report.contention.action_distribution == {"created": 1}


# --- Flow completion rates ------------------------------------------------------


def test_flow_completion_rate_distribution(tmp_path: Path) -> None:
    db, service = _service(tmp_path)
    try:
        text = _index(
            ("a", [("VERIFIED", 2), ("NEW", 1)]),  # complete
            ("b", [("GO", 1)]),  # in_implementation
            ("c", [("NEW", 1)]),  # in_review (no prior GO)
            ("d", [("NEW", 2), ("GO", 1)]),  # in_verification (NEW after GO)
        )
        report = gather_cutover_evidence(text, service, project_root=tmp_path)
    finally:
        db.close()

    assert report.flow_completion == {
        "complete": 1,
        "in_implementation": 1,
        "in_review": 1,
        "in_verification": 1,
    }


# --- Compatibility-view fidelity (stored shadow vs INDEX latest) ----------------


def test_compatibility_view_round_trips_index_latest_status(tmp_path: Path) -> None:
    db, service = _service(tmp_path)
    try:
        text = _index(("round", [("GO", 2), ("NEW", 1)]), ("adv", [("ADVISORY", 1)]))
        ingest_bridge_index(text, service, apply=True)
        report = gather_cutover_evidence(text, service, project_root=tmp_path)
    finally:
        db.close()

    assert report.fidelity.threads_checked == 2
    assert report.fidelity.fidelity_mismatches == ()
    assert report.fidelity.ok is True


def test_fidelity_mismatch_detected(tmp_path: Path) -> None:
    db, service = _service(tmp_path)
    try:
        # Populate the shadow from v1, then assess a *changed* INDEX (v2). The
        # stored shadow is now stale relative to canonical INDEX latest-status.
        v1 = _index(("evolve", [("NEW", 1)]))
        ingest_bridge_index(v1, service, apply=True)
        v2 = _index(("evolve", [("GO", 2), ("NEW", 1)]))
        report = gather_cutover_evidence(v2, service, project_root=tmp_path)
    finally:
        db.close()

    mismatch_slugs = {item["slug"] for item in report.fidelity.fidelity_mismatches}
    assert "evolve" in mismatch_slugs
    assert report.fidelity.ok is False


# --- GOV-FILE-BRIDGE-AUTHORITY-001: read-only contract --------------------------


def test_cli_cutover_evidence_readonly_json(runner: CliRunner, project_dir: Path) -> None:
    bridge_dir = project_dir / "bridge"
    bridge_dir.mkdir()
    index_file = bridge_dir / "INDEX.md"
    index_file.write_text(_index(("cli-thread", [("GO", 2), ("NEW", 1)])), encoding="utf-8")
    # On-disk bridge files matching the INDEX so completeness is clean (no lost/extra).
    (bridge_dir / "cli-thread-001.md").write_text("NEW\n", encoding="utf-8")
    (bridge_dir / "cli-thread-002.md").write_text("GO\n", encoding="utf-8")

    # Populate the shadow so fidelity + contention-zero are clean.
    db = KnowledgeDB(project_dir / "groundtruth.db")
    try:
        service = TypedArtifactFlowService(db)
        service.seed_reviewed_task_flow_definitions(changed_by="test", change_reason="cli seed")
        ingest_bridge_index(index_file.read_text(encoding="utf-8"), service, apply=True)
    finally:
        db.close()

    index_before = index_file.read_bytes()
    db = KnowledgeDB(project_dir / "groundtruth.db")
    try:
        history_before = len(db.get_flow_instance_history("flow-bridge-cli-thread"))
        artifacts_before = len(db.list_flow_artifacts(flow_instance_id="flow-bridge-cli-thread"))
    finally:
        db.close()

    result = runner.invoke(
        main,
        ["--config", str(project_dir / "groundtruth.toml"), "flow", "cutover-evidence", "--json"],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "ok"
    assert payload["ok"] is True
    assert payload["mutated"] is False
    assert payload["parity"]["derived_instances"] == 1
    assert payload["contention"]["contention_zero"] is True
    assert payload["fidelity"]["ok"] is True

    # The canonical INDEX is byte-identical and the shadow is unchanged.
    assert index_file.read_bytes() == index_before
    db = KnowledgeDB(project_dir / "groundtruth.db")
    try:
        assert len(db.get_flow_instance_history("flow-bridge-cli-thread")) == history_before
        assert len(db.list_flow_artifacts(flow_instance_id="flow-bridge-cli-thread")) == artifacts_before
    finally:
        db.close()


def test_cli_cutover_evidence_write_evidence_under_gtkb_state(runner: CliRunner, project_dir: Path) -> None:
    bridge_dir = project_dir / "bridge"
    bridge_dir.mkdir()
    index_file = bridge_dir / "INDEX.md"
    # Write the fixture as bytes so no platform line-ending translation occurs
    # (Path.write_text translates \n -> \r\n on Windows). The line-281 read-only
    # assertion compares read_bytes() against the LF-encoded expected, so the
    # on-disk fixture must be byte-identical LF.
    index_file.write_bytes(_index(("cli-w", [("NEW", 1)])).encode("utf-8"))
    (bridge_dir / "cli-w-001.md").write_text("NEW\n", encoding="utf-8", newline="\n")

    result = runner.invoke(
        main,
        [
            "--config",
            str(project_dir / "groundtruth.toml"),
            "flow",
            "cutover-evidence",
            "--write-evidence",
            "--json",
        ],
    )
    # exit 1 is acceptable here (unpopulated shadow => evidence gaps); the point is
    # that evidence output lands under .gtkb-state (regenerable, non-canonical).
    assert result.exit_code in (0, 1), result.output
    payload = json.loads(result.output)
    assert payload["mutated"] is False
    evidence_json = Path(payload["evidence_json"])
    assert evidence_json.exists()
    assert (project_dir / ".gtkb-state" / "cutover-evidence") in evidence_json.parents
    assert index_file.read_bytes() == _index(("cli-w", [("NEW", 1)])).encode("utf-8")


def test_cutover_evidence_module_holds_no_canonical_index_path_literal() -> None:
    """The module embeds no canonical-index path literal in executable code.

    Docstring prose that *describes* ``bridge/INDEX.md`` is allowed; the
    prohibition is on a code path literal that would read or write the canonical
    index. We parse the AST and exclude docstrings.
    """
    import ast

    import groundtruth_kb.tafe_cutover_evidence as evidence_module

    source = Path(evidence_module.__file__).read_text(encoding="utf-8")
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
