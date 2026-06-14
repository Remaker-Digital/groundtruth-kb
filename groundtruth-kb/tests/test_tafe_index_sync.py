"""Tests for the WI-4508 Slice-A lossless canonical-INDEX parser/serializer +
text-observable integrity diagnostics.

Covers (1) lossless parse/serialize round-trip byte-fidelity and status-vocabulary
preservation, (2) the three text-observable anomaly classes (malformed line,
duplicate document, version-order anomaly), (3) the read-only
``gt flow index-parity`` CLI (clean/anomalous/missing/refusal paths), and
(4) AST structural guards proving the module has no write surface and the CLI
carries the canonical refusal token.

Spec mapping:
- ``SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`` -- lossless round-trippable view.
- ``GOV-FILE-BRIDGE-AUTHORITY-001`` -- no canonical write surface; refusal guard.
- ``DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`` -- every named test has a
  real in-text oracle; absent-from-text (lost-block) detection is deferred to
  Slice B and is intentionally untested here.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

from click.testing import CliRunner

import groundtruth_kb.cli as cli_module
import groundtruth_kb.tafe_index_sync as sync_module
from groundtruth_kb.cli import main
from groundtruth_kb.tafe_index_sync import (
    parse_bridge_index,
    roundtrip_report,
    serialize_bridge_index,
)

# Live canonical index in this checkout (groundtruth-kb/tests -> GT-KB root).
_LIVE_INDEX = Path(__file__).resolve().parents[2] / "bridge" / "INDEX.md"

_MULTIVERSION_INDEX = (
    "<!-- header comment; preamble preserved verbatim -->\n"
    "\n"
    "Document: alpha\n"
    "GO: bridge/alpha-002.md\n"
    "NEW: bridge/alpha-001.md\n"
    "\n"
    "Document: beta\n"
    "VERIFIED: bridge/beta-003.md\n"
    "NEW: bridge/beta-002.md\n"
    "GO: bridge/beta-001.md\n"
)

_VOCAB_INDEX = (
    "Document: vocab\n"
    "WITHDRAWN: bridge/vocab-010.md\n"
    "DEFERRED: bridge/vocab-009.md\n"
    "ADVISORY: bridge/vocab-008.md\n"
    "VERIFIED: bridge/vocab-007.md\n"
    "NO-GO: bridge/vocab-006.md\n"
    "REVISED: bridge/vocab-005.md\n"
    "GO: bridge/vocab-004.md\n"
    "NEW: bridge/vocab-003.md\n"
    "ACCEPTED: bridge/vocab-002.md\n"
    "BLOCKED: bridge/vocab-001.md\n"
)


def _config_args(project_dir: Path) -> list[str]:
    return ["--config", str(project_dir / "groundtruth.toml")]


# --------------------------------------------------------------------------- #
# Lossless round-trip
# --------------------------------------------------------------------------- #


def test_roundtrip_byte_identical_on_live_index() -> None:
    """The live canonical INDEX must round-trip byte-identically (losslessness)."""
    if not _LIVE_INDEX.is_file():
        # The module is provider-agnostic; if the checkout layout differs the
        # representative-fixture tests still cover the contract.
        return
    text = _LIVE_INDEX.read_text(encoding="utf-8")
    assert serialize_bridge_index(parse_bridge_index(text)) == text


def test_roundtrip_multiversion_blocks() -> None:
    """Multi-block, multi-version text with preamble and blank separators
    round-trips byte-identically and parses the expected structure."""
    parsed = parse_bridge_index(_MULTIVERSION_INDEX)
    assert serialize_bridge_index(parsed) == _MULTIVERSION_INDEX
    assert [block.name for block in parsed.blocks] == ["alpha", "beta"]
    assert [line.version for line in parsed.blocks[0].version_lines] == [2, 1]
    assert [line.version for line in parsed.blocks[1].version_lines] == [3, 2, 1]
    # Preamble header is preserved as non-block content.
    assert parsed.preamble_raw[0].startswith("<!-- header comment")


def test_roundtrip_no_document_blocks_is_pure_preamble() -> None:
    text = "just some text\nwith no document blocks\n"
    parsed = parse_bridge_index(text)
    assert parsed.blocks == ()
    assert serialize_bridge_index(parsed) == text


def test_roundtrip_without_trailing_newline() -> None:
    text = "Document: x\nGO: bridge/x-001.md"
    assert serialize_bridge_index(parse_bridge_index(text)) == text


def test_status_vocabulary_preserved() -> None:
    """Every canonical + historically-present status token round-trips verbatim."""
    parsed = parse_bridge_index(_VOCAB_INDEX)
    assert serialize_bridge_index(parsed) == _VOCAB_INDEX
    statuses = [line.status for line in parsed.blocks[0].version_lines]
    assert statuses == [
        "WITHDRAWN",
        "DEFERRED",
        "ADVISORY",
        "VERIFIED",
        "NO-GO",
        "REVISED",
        "GO",
        "NEW",
        "ACCEPTED",
        "BLOCKED",
    ]
    report = roundtrip_report(_VOCAB_INDEX)
    assert report.ok is True


# --------------------------------------------------------------------------- #
# Text-observable anomaly detection
# --------------------------------------------------------------------------- #


def test_detects_duplicated_block() -> None:
    text = "Document: dup\nGO: bridge/dup-001.md\n\nDocument: dup\nNEW: bridge/dup-002.md\n"
    report = roundtrip_report(text)
    assert report.duplicate_documents == ("dup",)
    assert report.ok is False
    # Byte-fidelity is unaffected by the (semantic) duplicate.
    assert report.byte_identical is True


def test_detects_version_order_anomaly() -> None:
    text = "Document: x\nNEW: bridge/x-001.md\nGO: bridge/x-002.md\n"
    report = roundtrip_report(text)
    assert len(report.version_order_anomalies) == 1
    anomaly = report.version_order_anomalies[0]
    assert anomaly.document == "x"
    assert anomaly.versions == (1, 2)
    assert report.ok is False


def test_detects_malformed_line() -> None:
    text = "Document: m\nGO: bridge/m-002.md\nthis is not a valid line\nNEW: bridge/m-001.md\n"
    report = roundtrip_report(text)
    assert len(report.malformed_lines) == 1
    malformed = report.malformed_lines[0]
    assert malformed.line_number == 3
    assert malformed.text == "this is not a valid line"
    # Descending versions: no order anomaly mixed in.
    assert report.version_order_anomalies == ()
    assert report.ok is False


def test_clean_single_block_is_ok() -> None:
    text = "Document: clean\nGO: bridge/clean-002.md\nNEW: bridge/clean-001.md\n"
    report = roundtrip_report(text)
    assert report.ok is True
    assert report.document_count == 1
    assert report.as_dict()["ok"] is True


# --------------------------------------------------------------------------- #
# Read-only CLI
# --------------------------------------------------------------------------- #


def _write_index(project_dir: Path, text: str) -> Path:
    index = project_dir / "bridge" / "INDEX.md"
    index.parent.mkdir(parents=True, exist_ok=True)
    index.write_text(text, encoding="utf-8")
    return index


def test_cli_index_parity_json(runner: CliRunner, project_dir: Path) -> None:
    _write_index(project_dir, _MULTIVERSION_INDEX)
    result = runner.invoke(main, [*_config_args(project_dir), "flow", "index-parity", "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "ok"
    assert payload["ok"] is True
    assert payload["mutated"] is False
    assert payload["document_count"] == 2
    assert payload["byte_identical"] is True


def test_cli_exits_nonzero_on_anomaly(runner: CliRunner, project_dir: Path) -> None:
    _write_index(project_dir, "Document: x\nNEW: bridge/x-001.md\nGO: bridge/x-002.md\n")
    result = runner.invoke(main, [*_config_args(project_dir), "flow", "index-parity", "--json"])
    assert result.exit_code == 1, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "anomalies_found"
    assert payload["ok"] is False
    assert len(payload["version_order_anomalies"]) == 1


def test_cli_index_not_found(runner: CliRunner, project_dir: Path) -> None:
    result = runner.invoke(main, [*_config_args(project_dir), "flow", "index-parity", "--json"])
    assert result.exit_code == 3, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "index_not_found"
    assert payload["mutated"] is False


def test_cli_refuses_canonical_write_target(runner: CliRunner, project_dir: Path) -> None:
    for target in ("bridge/INDEX.md", "./bridge/INDEX.md", "BRIDGE/index.md"):
        with runner.isolated_filesystem() as fs:
            result = runner.invoke(
                main,
                [*_config_args(project_dir), "flow", "index-parity", "--out", target, "--json"],
            )
            assert result.exit_code != 0, f"{target}: expected non-zero exit"
            payload = json.loads(result.output)
            assert payload["status"] == "refused"
            assert payload["mutated"] is False
            # Nothing was written anywhere in the working tree.
            assert not (Path(fs) / "bridge").exists()


def test_cli_out_writes_report_to_non_canonical_path(runner: CliRunner, project_dir: Path, tmp_path: Path) -> None:
    _write_index(project_dir, _MULTIVERSION_INDEX)
    out = tmp_path / "reports" / "index-parity.json"
    result = runner.invoke(
        main,
        [*_config_args(project_dir), "flow", "index-parity", "--out", str(out), "--json"],
    )
    assert result.exit_code == 0, result.output
    assert out.is_file()
    saved = json.loads(out.read_text(encoding="utf-8"))
    assert saved["ok"] is True
    assert saved["document_count"] == 2


# --------------------------------------------------------------------------- #
# Structural (AST) guards
# --------------------------------------------------------------------------- #

_MEMBASE_MUTATOR_PREFIXES = ("insert_", "update_", "delete_", "resolve_", "promote_", "retire_")
_FILE_WRITE_ATTRS = {"write_text", "write_bytes", "writelines", "write"}


def test_module_has_no_write_surface() -> None:
    """The sync module is pure: no file-write attr, no ``open``, and no bare
    canonical ``bridge/INDEX.md`` path literal."""
    source = Path(sync_module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            assert node.value != "bridge/INDEX.md", "module must not carry the canonical bridge-index path literal"
        if isinstance(node, ast.Attribute):
            assert node.attr not in _FILE_WRITE_ATTRS, f"module must not call file-write attr {node.attr!r}"
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id != "open", "module must not call open()"


def test_ast_purity_no_io_no_subprocess_no_mutation() -> None:
    """The sync module imports/references no subprocess and calls no MemBase mutator."""
    source = Path(sync_module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name != "subprocess", "module must not import subprocess"
        if isinstance(node, ast.ImportFrom):
            assert node.module != "subprocess", "module must not import from subprocess"
        if isinstance(node, ast.Name):
            assert node.id != "subprocess", "module must not reference subprocess"
        if isinstance(node, ast.Attribute):
            assert not node.attr.startswith(_MEMBASE_MUTATOR_PREFIXES), f"module must not call mutator {node.attr!r}"


def test_cli_command_retains_canonical_refusal_token() -> None:
    """The CLI command carries the literal ``bridge/INDEX.md`` token and calls the
    refusal guard so a refactor cannot silently drop the canonical-write guard."""
    source = Path(cli_module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)

    command_fn = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "flow_index_parity_cmd":
            command_fn = node
            break
    assert command_fn is not None, "flow_index_parity_cmd not found in cli.py"

    has_canonical_token = any(
        isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value == "bridge/INDEX.md"
        for n in ast.walk(command_fn)
    )
    assert has_canonical_token, "CLI command must compare against the canonical bridge/INDEX.md token"

    calls_refusal_guard = any(
        isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "_targets_canonical_bridge_index"
        for n in ast.walk(command_fn)
    )
    assert calls_refusal_guard, "CLI command must call the _targets_canonical_bridge_index refusal guard"
