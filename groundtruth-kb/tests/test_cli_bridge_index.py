"""Tests for the deterministic ``gt bridge index`` CLI/API."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from groundtruth_kb.bridge.index_mutation import (
    BridgeIndexMutationError,
    add_document_to_index_text,
    set_status,
    set_status_in_index_text,
)
from groundtruth_kb.cli import main

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WRITER_SOURCE = PROJECT_ROOT / "scripts" / "bridge_index_writer.py"


def _config_path(project_dir: Path) -> Path:
    return project_dir / "groundtruth.toml"


def _install_writer(project_dir: Path) -> None:
    scripts_dir = project_dir / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "bridge_index_writer.py").write_text(WRITER_SOURCE.read_text(encoding="utf-8"), encoding="utf-8")


def _write_index(project_dir: Path, text: str) -> Path:
    bridge_dir = project_dir / "bridge"
    bridge_dir.mkdir(exist_ok=True)
    index = bridge_dir / "INDEX.md"
    index.write_text(text, encoding="utf-8")
    return index


def _write_bridge_file(project_dir: Path, name: str, content: str) -> Path:
    bridge_dir = project_dir / "bridge"
    bridge_dir.mkdir(exist_ok=True)
    path = bridge_dir / name
    path.write_text(content, encoding="utf-8")
    return path


def _deferred_body() -> str:
    return (
        "DEFERRED\n\n"
        "# Deferred Thread\n\n"
        "## Owner Decisions / Input\n\n"
        "- DELIB-20260602-DEFERRED-TEST: owner decision sets this deferral.\n\n"
        "## Status\n\n"
        "Deferral reason: waiting for owner sequencing.\n"
        "Clear condition: owner records reactivation approval.\n"
    )


def _clear_body(status: str = "NEW") -> str:
    return (
        f"{status}\n\n"
        "# Reactivated Thread\n\n"
        "## Owner Decisions / Input\n\n"
        "- DELIB-20260602-DEFERRED-CLEAR-TEST: owner decision clears the DEFERRED status "
        "and resumes bridge work.\n\n"
        "## Specification Links\n\n"
        "- GOV-FILE-BRIDGE-AUTHORITY-001\n"
    )


def _runner_result(project_dir: Path, *args: str):
    return CliRunner().invoke(main, ["--config", str(_config_path(project_dir)), *args])


def test_add_document_transform_inserts_below_preamble() -> None:
    index = "# Bridge Index\n<!-- comment -->\n\nDocument: existing\nNEW: bridge/existing-001.md\n"

    updated = add_document_to_index_text(index, "alpha-thread", "NEW", "bridge/alpha-thread-001.md")

    assert updated.startswith(
        "# Bridge Index\n<!-- comment -->\n\n"
        "Document: alpha-thread\nNEW: bridge/alpha-thread-001.md\n\nDocument: existing\n"
    )


def test_set_status_transform_prepends_to_existing_document() -> None:
    index = "Document: alpha-thread\nNEW: bridge/alpha-thread-001.md\n"

    updated = set_status_in_index_text(index, "alpha-thread", "GO", "bridge/alpha-thread-002.md")

    assert updated == ("Document: alpha-thread\nGO: bridge/alpha-thread-002.md\nNEW: bridge/alpha-thread-001.md\n")


def test_set_status_transform_accepts_deferred_status() -> None:
    index = "Document: alpha-thread\nGO: bridge/alpha-thread-001.md\n"

    updated = set_status_in_index_text(index, "alpha-thread", "DEFERRED", "bridge/alpha-thread-002.md")

    assert updated.splitlines()[:3] == [
        "Document: alpha-thread",
        "DEFERRED: bridge/alpha-thread-002.md",
        "GO: bridge/alpha-thread-001.md",
    ]


def test_invalid_status_fails_closed() -> None:
    index = "Document: alpha-thread\nNEW: bridge/alpha-thread-001.md\n"

    try:
        set_status_in_index_text(index, "alpha-thread", "BOGUS", "bridge/alpha-thread-002.md")
    except BridgeIndexMutationError as exc:
        assert "unknown bridge status" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("expected BridgeIndexMutationError")


def test_missing_document_fails_closed() -> None:
    index = "Document: alpha-thread\nNEW: bridge/alpha-thread-001.md\n"

    try:
        set_status_in_index_text(index, "missing-thread", "GO", "bridge/missing-thread-002.md")
    except BridgeIndexMutationError as exc:
        assert "does not exist" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("expected BridgeIndexMutationError")


def test_duplicate_document_fails_closed() -> None:
    index = (
        "Document: alpha-thread\nNEW: bridge/alpha-thread-001.md\n\n"
        "Document: alpha-thread\nNEW: bridge/alpha-thread-002.md\n"
    )

    try:
        add_document_to_index_text(index, "beta-thread", "NEW", "bridge/beta-thread-001.md")
    except BridgeIndexMutationError as exc:
        assert "duplicate bridge document" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("expected BridgeIndexMutationError")


def test_duplicate_status_path_fails_closed() -> None:
    index = "Document: alpha-thread\nNEW: bridge/alpha-thread-001.md\n"

    try:
        set_status_in_index_text(index, "alpha-thread", "GO", "bridge/alpha-thread-001.md")
    except BridgeIndexMutationError as exc:
        assert "already exists" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("expected BridgeIndexMutationError")


def test_cli_add_document_json_updates_index(project_dir: Path) -> None:
    _install_writer(project_dir)
    index = _write_index(project_dir, "# Bridge Index\n\nDocument: existing\nNEW: bridge/existing-001.md\n")

    result = _runner_result(
        project_dir,
        "bridge",
        "index",
        "add-document",
        "alpha-thread",
        "--path",
        "bridge/alpha-thread-001.md",
        "--json",
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["document"] == "alpha-thread"
    assert "Document: alpha-thread\nNEW: bridge/alpha-thread-001.md" in index.read_text(encoding="utf-8")


def test_cli_set_status_json_updates_index(project_dir: Path) -> None:
    _install_writer(project_dir)
    index = _write_index(project_dir, "Document: alpha-thread\nNEW: bridge/alpha-thread-001.md\n")

    result = _runner_result(
        project_dir,
        "bridge",
        "index",
        "set-status",
        "alpha-thread",
        "GO",
        "--path",
        "bridge/alpha-thread-002.md",
        "--json",
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "GO"
    assert index.read_text(encoding="utf-8").splitlines()[:3] == [
        "Document: alpha-thread",
        "GO: bridge/alpha-thread-002.md",
        "NEW: bridge/alpha-thread-001.md",
    ]


def test_cli_set_status_deferred_rejects_placeholder_owner_evidence(project_dir: Path) -> None:
    _install_writer(project_dir)
    index = _write_index(project_dir, "Document: alpha-thread\nGO: bridge/alpha-thread-001.md\n")
    (project_dir / "bridge" / "alpha-thread-002.md").write_text(
        "DEFERRED\n\n## Owner Decisions / Input\n\nNone\n",
        encoding="utf-8",
    )
    before = index.read_text(encoding="utf-8")

    result = _runner_result(
        project_dir,
        "bridge",
        "index",
        "set-status",
        "alpha-thread",
        "DEFERRED",
        "--path",
        "bridge/alpha-thread-002.md",
    )

    assert result.exit_code == 1
    assert "DEFERRED bridge file" in result.output
    assert index.read_text(encoding="utf-8") == before


def test_cli_set_status_deferred_updates_index_with_explicit_owner_evidence(project_dir: Path) -> None:
    _install_writer(project_dir)
    index = _write_index(project_dir, "Document: alpha-thread\nGO: bridge/alpha-thread-001.md\n")
    (project_dir / "bridge" / "alpha-thread-002.md").write_text(
        "\n".join(
            [
                "DEFERRED",
                "",
                "## Owner Decisions / Input",
                "",
                "- DELIB-TEST-OWNER-DEFERRAL: owner decision to park this thread.",
                "",
                "## Deferral Reason",
                "",
                "Reason: waiting on external decision evidence.",
                "",
                "## Clear Condition",
                "",
                "Clear condition: resume when the owner files the follow-up directive.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = _runner_result(
        project_dir,
        "bridge",
        "index",
        "set-status",
        "alpha-thread",
        "DEFERRED",
        "--path",
        "bridge/alpha-thread-002.md",
        "--json",
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "DEFERRED"
    assert index.read_text(encoding="utf-8").splitlines()[:3] == [
        "Document: alpha-thread",
        "DEFERRED: bridge/alpha-thread-002.md",
        "GO: bridge/alpha-thread-001.md",
    ]


def test_cli_invalid_path_leaves_index_unchanged(project_dir: Path) -> None:
    _install_writer(project_dir)
    index = _write_index(project_dir, "Document: alpha-thread\nNEW: bridge/alpha-thread-001.md\n")
    before = index.read_text(encoding="utf-8")

    result = _runner_result(
        project_dir,
        "bridge",
        "index",
        "set-status",
        "alpha-thread",
        "GO",
        "--path",
        "bridge/other-thread-002.md",
    )

    assert result.exit_code == 1
    assert "path slug does not match" in result.output
    assert index.read_text(encoding="utf-8") == before


def test_cli_set_status_deferred_rejects_missing_owner_evidence(project_dir: Path) -> None:
    _install_writer(project_dir)
    index = _write_index(project_dir, "Document: alpha-thread\nNEW: bridge/alpha-thread-001.md\n")
    _write_bridge_file(
        project_dir,
        "alpha-thread-002.md",
        "DEFERRED\n\n# Deferred Thread\n\nReason: waiting.\n\nClear condition: owner resumes.\n",
    )
    before = index.read_text(encoding="utf-8")

    result = _runner_result(
        project_dir,
        "bridge",
        "index",
        "set-status",
        "alpha-thread",
        "DEFERRED",
        "--path",
        "bridge/alpha-thread-002.md",
    )

    assert result.exit_code == 1
    assert "Owner Decisions" in result.output
    assert index.read_text(encoding="utf-8") == before


def test_cli_set_status_deferred_accepts_owner_evidence(project_dir: Path) -> None:
    _install_writer(project_dir)
    index = _write_index(project_dir, "Document: alpha-thread\nNEW: bridge/alpha-thread-001.md\n")
    _write_bridge_file(project_dir, "alpha-thread-002.md", _deferred_body())

    result = _runner_result(
        project_dir,
        "bridge",
        "index",
        "set-status",
        "alpha-thread",
        "DEFERRED",
        "--path",
        "bridge/alpha-thread-002.md",
        "--json",
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "DEFERRED"
    assert index.read_text(encoding="utf-8").splitlines()[:2] == [
        "Document: alpha-thread",
        "DEFERRED: bridge/alpha-thread-002.md",
    ]


def test_set_status_clearing_deferred_requires_owner_clear_evidence(project_dir: Path) -> None:
    _install_writer(project_dir)
    _write_index(
        project_dir,
        "Document: alpha-thread\nDEFERRED: bridge/alpha-thread-002.md\nNEW: bridge/alpha-thread-001.md\n",
    )
    _write_bridge_file(project_dir, "alpha-thread-002.md", _deferred_body())
    _write_bridge_file(
        project_dir,
        "alpha-thread-003.md",
        "NEW\n\n# Reactivated Thread\n\n## Specification Links\n\n- GOV-FILE-BRIDGE-AUTHORITY-001\n",
    )

    try:
        set_status(project_dir, "alpha-thread", "NEW", bridge_path="bridge/alpha-thread-003.md")
    except BridgeIndexMutationError as exc:
        assert "clearing DEFERRED" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("expected BridgeIndexMutationError")


def test_set_status_clearing_deferred_accepts_owner_clear_evidence(project_dir: Path) -> None:
    _install_writer(project_dir)
    index = _write_index(
        project_dir,
        "Document: alpha-thread\nDEFERRED: bridge/alpha-thread-002.md\nNEW: bridge/alpha-thread-001.md\n",
    )
    _write_bridge_file(project_dir, "alpha-thread-002.md", _deferred_body())
    _write_bridge_file(project_dir, "alpha-thread-003.md", _clear_body("NEW"))

    result = set_status(project_dir, "alpha-thread", "NEW", bridge_path="bridge/alpha-thread-003.md")

    assert result.status == "NEW"
    assert index.read_text(encoding="utf-8").splitlines()[:2] == [
        "Document: alpha-thread",
        "NEW: bridge/alpha-thread-003.md",
    ]


def test_cli_bridge_index_help_resolves() -> None:
    result = CliRunner().invoke(main, ["bridge", "index", "--help"])

    assert result.exit_code == 0, result.output
    assert "Serialized bridge INDEX mutation commands" in result.output
