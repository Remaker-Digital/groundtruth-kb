"""Spec-derived tests for ``gt flow regen-verify`` (WI-4510 Phase 2).

Derived from ``ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001`` (the shadow-verify exit
criterion) and ``GOV-FILE-BRIDGE-AUTHORITY-001`` (the canonical INDEX is never
written):

* equal verdict + exit 0 on an in-sync shadow (canonical single-thread INDEX);
* divergent verdict + non-zero exit when the canonical INDEX diverges from the
  stored shadow (a changed status token);
* refuses an ``--evidence-dir`` that resolves to the canonical bridge index;
* the canonical ``bridge/INDEX.md`` is byte-unchanged by a verify run;
* ``--write-evidence`` emits a regenerable, non-canonical verdict JSON.

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
from groundtruth_kb.typed_artifact_flow import TypedArtifactFlowService

_HEADER = "# Bridge INDEX\n\n"


def _index(*blocks: tuple[str, list[tuple[str, int]]]) -> str:
    """Build canonical ``bridge/INDEX.md`` text from (slug, [(status, version)])."""
    parts = [_HEADER]
    for slug, lines in blocks:
        parts.append(f"Document: {slug}\n")
        for status, version in lines:
            parts.append(f"{status}: bridge/{slug}-{version:03d}.md\n")
        parts.append("\n")
    return "".join(parts)


def _seed_definitions(project_dir: Path) -> None:
    """Seed the implementation flow_definition the apply-refresh ingest needs."""
    db = KnowledgeDB(project_dir / "groundtruth.db")
    try:
        TypedArtifactFlowService(db).seed_reviewed_task_flow_definitions(
            changed_by="test", change_reason="regen-verify cli seed"
        )
    finally:
        db.close()


def _write_index(project_dir: Path, text: str) -> Path:
    bridge_dir = project_dir / "bridge"
    bridge_dir.mkdir(exist_ok=True)
    index_file = bridge_dir / "INDEX.md"
    index_file.write_text(text, encoding="utf-8")
    return index_file


def test_cli_regen_verify_equal_on_in_sync_shadow(runner: CliRunner, project_dir: Path) -> None:
    index_file = _write_index(project_dir, _index(("solo-thread", [("GO", 2), ("NEW", 1)])))
    before = index_file.read_bytes()
    _seed_definitions(project_dir)

    result = runner.invoke(
        main,
        ["--config", str(project_dir / "groundtruth.toml"), "flow", "regen-verify", "--apply-refresh", "--json"],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["ok"] is True
    assert payload["status"] == "byte_identical"
    assert payload["semantic_equal"] is True
    assert payload["byte_identical"] is True
    assert payload["shadow_refreshed"] is True
    assert index_file.read_bytes() == before  # canonical INDEX byte-identical


def test_cli_regen_verify_divergent_nonzero_exit(runner: CliRunner, project_dir: Path) -> None:
    index_file = _write_index(project_dir, _index(("drift-thread", [("GO", 2), ("NEW", 1)])))
    _seed_definitions(project_dir)

    # Populate the shadow from the GO-latest INDEX.
    seed = runner.invoke(
        main,
        ["--config", str(project_dir / "groundtruth.toml"), "flow", "regen-verify", "--apply-refresh", "--json"],
    )
    assert seed.exit_code == 0, seed.output

    # Now the canonical INDEX changes the latest token; the stored shadow is stale.
    index_file.write_text(_index(("drift-thread", [("NO-GO", 2), ("NEW", 1)])), encoding="utf-8")

    result = runner.invoke(
        main,
        ["--config", str(project_dir / "groundtruth.toml"), "flow", "regen-verify", "--json"],
    )
    assert result.exit_code == 1, result.output
    payload = json.loads(result.output)
    assert payload["ok"] is False
    assert payload["status"] == "divergent"
    assert payload["version_line_mismatches"]
    assert payload["version_line_mismatches"][0]["slug"] == "drift-thread"


def test_cli_regen_verify_refuses_canonical_index(runner: CliRunner, project_dir: Path) -> None:
    _write_index(project_dir, _index(("any-thread", [("NEW", 1)])))

    result = runner.invoke(
        main,
        [
            "--config",
            str(project_dir / "groundtruth.toml"),
            "flow",
            "regen-verify",
            "--write-evidence",
            "--evidence-dir",
            "bridge/INDEX.md",
            "--json",
        ],
    )
    assert result.exit_code == 2, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "refused"
    assert payload["mutated"] is False


def test_cli_regen_verify_index_not_found(runner: CliRunner, project_dir: Path) -> None:
    # No bridge/INDEX.md created.
    result = runner.invoke(
        main,
        ["--config", str(project_dir / "groundtruth.toml"), "flow", "regen-verify", "--json"],
    )
    assert result.exit_code == 3, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "index_not_found"


def test_cli_regen_verify_writes_evidence(runner: CliRunner, project_dir: Path) -> None:
    index_file = _write_index(project_dir, _index(("evid-thread", [("VERIFIED", 1)])))
    before = index_file.read_bytes()
    _seed_definitions(project_dir)

    result = runner.invoke(
        main,
        [
            "--config",
            str(project_dir / "groundtruth.toml"),
            "flow",
            "regen-verify",
            "--apply-refresh",
            "--write-evidence",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    verdict_json = Path(payload["verdict_json"])
    assert verdict_json.is_file()
    written = json.loads(verdict_json.read_text(encoding="utf-8"))
    assert written["ok"] is True
    # Evidence lands under the non-canonical regen-verify evidence dir.
    assert "regen-verify" in str(verdict_json)
    assert index_file.read_bytes() == before  # canonical INDEX byte-identical


# --- WI-4510 Refined Option B: extra-thread partition through the real oracle ---
# The append-only shadow retains threads the protocol trimmed from the live INDEX.
# regen-verify must tolerate legitimate terminal-archived residue (ungated) while
# still gating on phantom / non-terminal shadow rows. The CLI wires in the shared
# tafe_index_completeness._candidate_is_archived oracle
# (DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001).


def _write_bridge_file(project_dir: Path, slug: str, version: int, first_line: str) -> Path:
    bridge_dir = project_dir / "bridge"
    bridge_dir.mkdir(exist_ok=True)
    path = bridge_dir / f"{slug}-{version:03d}.md"
    path.write_text(f"{first_line}\n\n# {slug}\n", encoding="utf-8")
    return path


def test_cli_regen_verify_terminal_archived_extra_non_gating(runner: CliRunner, project_dir: Path) -> None:
    # Seed shadow with kept + archived-thread, then trim archived-thread from the
    # INDEX while its on-disk latest version is VERIFIED (terminal-archived per rule 1).
    # The extra must be tolerated (ungated).
    _write_index(project_dir, _index(("kept-thread", [("NEW", 1)]), ("archived-thread", [("VERIFIED", 1)])))
    _seed_definitions(project_dir)
    seed = runner.invoke(
        main,
        ["--config", str(project_dir / "groundtruth.toml"), "flow", "regen-verify", "--apply-refresh", "--json"],
    )
    assert seed.exit_code == 0, seed.output
    _write_bridge_file(project_dir, "archived-thread", 1, "VERIFIED")  # on-disk terminal (rule 1)
    _write_index(project_dir, _index(("kept-thread", [("NEW", 1)])))  # trim archived-thread from INDEX

    result = runner.invoke(
        main,
        ["--config", str(project_dir / "groundtruth.toml"), "flow", "regen-verify", "--json"],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["ok"] is True
    assert "archived-thread" in payload["extra_archived_in_generated"]
    assert "archived-thread" not in payload["extra_divergent_in_generated"]


def test_cli_regen_verify_phantom_extra_gates(runner: CliRunner, project_dir: Path) -> None:
    # Seed shadow with kept + phantom-thread, then trim phantom-thread from the INDEX.
    # phantom-thread has NO on-disk file and is NOT acknowledged => it gates (the
    # central must-still-gate case; the sp1-dispatch-reliability-prime-handoff shape).
    _write_index(project_dir, _index(("kept-thread", [("NEW", 1)]), ("phantom-thread", [("ADVISORY", 1)])))
    _seed_definitions(project_dir)
    seed = runner.invoke(
        main,
        ["--config", str(project_dir / "groundtruth.toml"), "flow", "regen-verify", "--apply-refresh", "--json"],
    )
    assert seed.exit_code == 0, seed.output
    _write_index(project_dir, _index(("kept-thread", [("NEW", 1)])))  # trim; no on-disk file for phantom-thread

    result = runner.invoke(
        main,
        ["--config", str(project_dir / "groundtruth.toml"), "flow", "regen-verify", "--json"],
    )
    assert result.exit_code == 1, result.output
    payload = json.loads(result.output)
    assert payload["ok"] is False
    assert payload["status"] == "divergent"
    assert "phantom-thread" in payload["extra_divergent_in_generated"]
    assert "phantom-thread" not in payload["extra_archived_in_generated"]


def test_cli_regen_verify_acknowledged_archived_extra_non_gating(runner: CliRunner, project_dir: Path) -> None:
    # Same phantom shape (no on-disk file), but the slug is owner-acknowledged in
    # config/governance/tafe-acknowledged-archived-bridges.toml (rule 3) => tolerated.
    _write_index(project_dir, _index(("kept-thread", [("NEW", 1)]), ("ack-thread", [("ADVISORY", 1)])))
    _seed_definitions(project_dir)
    seed = runner.invoke(
        main,
        ["--config", str(project_dir / "groundtruth.toml"), "flow", "regen-verify", "--apply-refresh", "--json"],
    )
    assert seed.exit_code == 0, seed.output
    _write_index(project_dir, _index(("kept-thread", [("NEW", 1)])))
    ack_dir = project_dir / "config" / "governance"
    ack_dir.mkdir(parents=True, exist_ok=True)
    (ack_dir / "tafe-acknowledged-archived-bridges.toml").write_text(
        '[[acknowledged]]\nslug = "ack-thread"\n', encoding="utf-8"
    )

    result = runner.invoke(
        main,
        ["--config", str(project_dir / "groundtruth.toml"), "flow", "regen-verify", "--json"],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["ok"] is True
    assert "ack-thread" in payload["extra_archived_in_generated"]
