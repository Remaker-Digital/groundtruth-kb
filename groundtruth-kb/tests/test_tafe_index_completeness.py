"""Tests for the WI-4508 Slice-B external expected-document oracle + lost-block
detection.

Covers (1) the ``bridge/`` directory scan (slug grouping, version aggregation,
exclusion of ``INDEX.md`` and non-versioned files), (2) the completeness diff
(lost-block = absent-from-text class Slice A deferred; extra-block = phantom
INDEX entry; parity = ok), (3) Slice A parser reuse for the present set, (4) the
read-only ``gt flow index-completeness`` CLI (clean / lost-block / missing /
refusal / out paths), and (5) AST structural guards proving the oracle module
is read-only (no write surface) and the CLI carries the canonical refusal guard.

Spec mapping:
- ``SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`` -- expected-document scan
  completeness (lossless+complete parallel view; Slice B = complete).
- ``GOV-FILE-BRIDGE-AUTHORITY-001`` -- canonical INDEX preserved; no write
  surface; ``--out`` refusal guard.
- ``DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`` -- every named test has a
  real fixture oracle.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

from click.testing import CliRunner

import groundtruth_kb.cli as cli_module
import groundtruth_kb.tafe_index_completeness as completeness_module
from groundtruth_kb.cli import main
from groundtruth_kb.tafe_index_completeness import (
    index_completeness_report,
    scan_expected_documents,
)
from groundtruth_kb.tafe_index_sync import parse_bridge_index


def _config_args(project_dir: Path) -> list[str]:
    return ["--config", str(project_dir / "groundtruth.toml")]


def _write_bridge_file(project_dir: Path, name: str, body: str = "NEW\n") -> Path:
    """Create ``bridge/<name>`` under the project dir (versioned or otherwise)."""
    path = project_dir / "bridge" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _write_index(project_dir: Path, text: str) -> Path:
    index = project_dir / "bridge" / "INDEX.md"
    index.parent.mkdir(parents=True, exist_ok=True)
    index.write_text(text, encoding="utf-8")
    return index


def _index_for(*slugs: str) -> str:
    """Build a minimal canonical INDEX naming each slug as a ``Document:`` block."""
    blocks = []
    for slug in slugs:
        blocks.append(f"Document: {slug}\nNEW: bridge/{slug}-001.md\n")
    return "\n".join(blocks)


# --------------------------------------------------------------------------- #
# scan_expected_documents
# --------------------------------------------------------------------------- #


def test_scan_finds_all_bridge_slugs(project_dir: Path) -> None:
    """The bridge/ scan groups versioned files by slug with latest_version."""
    _write_bridge_file(project_dir, "alpha-001.md")
    _write_bridge_file(project_dir, "alpha-002.md")
    # A slug whose own name contains digits and hyphens (e.g. WI numbers, slices).
    _write_bridge_file(project_dir, "gtkb-wi-4534-guard-slice-a-001.md")

    expected = scan_expected_documents(project_dir)

    assert set(expected) == {"alpha", "gtkb-wi-4534-guard-slice-a"}
    assert expected["alpha"].latest_version == 2
    assert expected["alpha"].files == ("bridge/alpha-001.md", "bridge/alpha-002.md")
    # The trailing -NNN is the version; the rest (digits/hyphens included) is the slug.
    assert expected["gtkb-wi-4534-guard-slice-a"].latest_version == 1


def test_scan_excludes_index_and_nonversioned(project_dir: Path) -> None:
    """INDEX.md and non-``-NNN``-versioned markdown are not expected documents."""
    _write_bridge_file(project_dir, "real-001.md")
    _write_index(project_dir, _index_for("real"))
    _write_bridge_file(project_dir, "BRIDGE-INVENTORY.md")  # non-versioned
    _write_bridge_file(project_dir, "notes.md")  # non-versioned

    expected = scan_expected_documents(project_dir)

    assert set(expected) == {"real"}
    assert "INDEX" not in expected
    assert "BRIDGE-INVENTORY" not in expected
    assert "notes" not in expected


def test_scan_empty_when_no_bridge_dir(tmp_path: Path) -> None:
    """A project root with no bridge/ directory yields an empty expected set."""
    assert scan_expected_documents(tmp_path) == {}


# --------------------------------------------------------------------------- #
# index_completeness_report
# --------------------------------------------------------------------------- #


def test_report_detects_lost_block(project_dir: Path) -> None:
    """A slug with bridge files but no INDEX Document: entry is a lost block.

    This is exactly the absent-from-text class Slice A deferred. (A parked draft
    -- a deliberately uncommitted-to-INDEX file -- surfaces the same way; it is a
    benign review candidate, never a canonical mutation.)
    """
    _write_bridge_file(project_dir, "present-001.md")
    _write_bridge_file(project_dir, "orphan-001.md")  # on disk, absent from INDEX
    index_text = _index_for("present")

    report = index_completeness_report(index_text, project_dir)

    assert report.lost_blocks == ("orphan",)
    assert report.ok is False
    assert "orphan" in report.expected_slugs
    assert "orphan" not in report.present_slugs


def test_report_detects_extra_block(project_dir: Path) -> None:
    """An INDEX Document: entry with no bridge files on disk is an extra block."""
    _write_bridge_file(project_dir, "real-001.md")
    index_text = _index_for("real", "ghost")  # ghost has no bridge/ghost-*.md

    report = index_completeness_report(index_text, project_dir)

    assert report.extra_blocks == ("ghost",)
    assert report.lost_blocks == ()
    # Extra blocks alone do not fail the completeness gate (only lost blocks do).
    assert report.ok is True


def test_report_ok_when_index_matches_bridge_dir(project_dir: Path) -> None:
    """When INDEX names == bridge/ slugs, there are no lost blocks and ok is True."""
    _write_bridge_file(project_dir, "alpha-001.md")
    _write_bridge_file(project_dir, "beta-001.md")
    _write_bridge_file(project_dir, "beta-002.md")
    index_text = _index_for("alpha", "beta")

    report = index_completeness_report(index_text, project_dir)

    assert report.lost_blocks == ()
    assert report.extra_blocks == ()
    assert report.ok is True
    assert report.as_dict()["ok"] is True


def test_uses_slice_a_parser(project_dir: Path) -> None:
    """The present set is exactly what the VERIFIED Slice A parser reports.

    Guards against re-implementing INDEX parsing: present_slugs must equal the
    Document: names parse_bridge_index extracts from the same text.
    """
    _write_bridge_file(project_dir, "alpha-001.md")
    _write_bridge_file(project_dir, "beta-001.md")
    index_text = _index_for("alpha", "beta")

    report = index_completeness_report(index_text, project_dir)
    parser_names = sorted(block.name for block in parse_bridge_index(index_text).blocks)

    assert list(report.present_slugs) == parser_names


# --------------------------------------------------------------------------- #
# Terminal-archived classification (DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001)
# --------------------------------------------------------------------------- #


def test_terminal_latest_token_classified_archived(project_dir: Path) -> None:
    """A terminal-status slug absent from INDEX is archived, not lost (and ok stays True)."""
    _write_bridge_file(project_dir, "present-001.md")
    _write_bridge_file(project_dir, "done-001.md", body="VERIFIED\n")

    report = index_completeness_report(_index_for("present"), project_dir)

    assert report.archived_blocks == ("done",)
    assert report.lost_blocks == ()
    assert report.ok is True


def test_all_terminal_token_variants_archived(project_dir: Path) -> None:
    """Every terminal token (VERIFIED/WITHDRAWN/DEFERRED/ADVISORY/ACCEPTED) => archived."""
    for slug, token in (
        ("v", "VERIFIED"),
        ("w", "WITHDRAWN"),
        ("d", "DEFERRED"),
        ("a", "ADVISORY"),
        ("acc", "ACCEPTED"),
    ):
        _write_bridge_file(project_dir, f"{slug}-001.md", body=f"{token}\n")

    report = index_completeness_report(_index_for(), project_dir)

    assert set(report.archived_blocks) == {"v", "w", "d", "a", "acc"}
    assert report.lost_blocks == ()


def test_non_terminal_tokens_remain_lost(project_dir: Path) -> None:
    """Non-terminal tokens (NEW/REVISED/GO/NO-GO) keep an absent slug in lost_blocks."""
    for slug, token in (("n", "NEW"), ("r", "REVISED"), ("g", "GO"), ("ng", "NO-GO")):
        _write_bridge_file(project_dir, f"{slug}-001.md", body=f"{token}\n")

    report = index_completeness_report(_index_for(), project_dir)

    assert set(report.lost_blocks) == {"n", "r", "g", "ng"}
    assert report.archived_blocks == ()
    assert report.ok is False


def test_heading_marker_prefixed_terminal_archived(project_dir: Path) -> None:
    """A markdown-heading status line (``# VERIFIED: ...``) is read as terminal."""
    _write_bridge_file(project_dir, "hdg-001.md", body="# VERIFIED: closed out\n\nbody\n")

    report = index_completeness_report(_index_for(), project_dir)

    assert report.archived_blocks == ("hdg",)
    assert report.lost_blocks == ()


def test_status_indeterminate_with_terminal_token_archived(project_dir: Path) -> None:
    """First line prose but a later terminal-token line => archived (full-file scan)."""
    _write_bridge_file(project_dir, "old-001.md", body="Some historical note prose.\n\n## VERIFIED\n\ndetails\n")

    report = index_completeness_report(_index_for(), project_dir)

    assert report.archived_blocks == ("old",)
    assert report.lost_blocks == ()


def test_status_indeterminate_without_terminal_token_lost(project_dir: Path) -> None:
    """First line prose and no terminal token anywhere => lost (conservative)."""
    _write_bridge_file(project_dir, "prose-001.md", body="Just a note.\n\nNo status token here.\n")

    report = index_completeness_report(_index_for(), project_dir)

    assert report.lost_blocks == ("prose",)
    assert report.archived_blocks == ()


def test_latest_version_status_decides(project_dir: Path) -> None:
    """Classification uses the latest on-disk version, not earlier ones."""
    _write_bridge_file(project_dir, "evolve-001.md", body="NEW\n")
    _write_bridge_file(project_dir, "evolve-002.md", body="VERIFIED\n")

    report = index_completeness_report(_index_for(), project_dir)

    assert report.archived_blocks == ("evolve",)
    assert report.lost_blocks == ()


def test_present_slug_is_neither_archived_nor_lost(project_dir: Path) -> None:
    """A slug present in INDEX is never classified as archived or lost."""
    _write_bridge_file(project_dir, "here-001.md", body="VERIFIED\n")

    report = index_completeness_report(_index_for("here"), project_dir)

    assert "here" not in report.archived_blocks
    assert "here" not in report.lost_blocks


def test_as_dict_surfaces_archived_blocks(project_dir: Path) -> None:
    """as_dict exposes archived_blocks + archived_count alongside lost_blocks."""
    _write_bridge_file(project_dir, "done-001.md", body="VERIFIED\n")
    _write_bridge_file(project_dir, "orphan-001.md", body="NEW\n")

    payload = index_completeness_report(_index_for(), project_dir).as_dict()

    assert payload["archived_blocks"] == ["done"]
    assert payload["archived_count"] == 1
    assert payload["lost_blocks"] == ["orphan"]


# --------------------------------------------------------------------------- #
# Read-only CLI
# --------------------------------------------------------------------------- #


def test_cli_index_completeness_json(runner: CliRunner, project_dir: Path) -> None:
    """Clean completeness over a matching INDEX + bridge/ dir exits 0, read-only."""
    _write_bridge_file(project_dir, "alpha-001.md")
    _write_bridge_file(project_dir, "beta-001.md")
    _write_index(project_dir, _index_for("alpha", "beta"))

    result = runner.invoke(main, [*_config_args(project_dir), "flow", "index-completeness", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "ok"
    assert payload["ok"] is True
    assert payload["mutated"] is False
    assert payload["lost_blocks"] == []


def test_cli_exits_nonzero_on_lost_block(runner: CliRunner, project_dir: Path) -> None:
    """A lost block makes the CLI exit 1 with status lost_blocks_found."""
    _write_bridge_file(project_dir, "present-001.md")
    _write_bridge_file(project_dir, "orphan-001.md")
    _write_index(project_dir, _index_for("present"))

    result = runner.invoke(main, [*_config_args(project_dir), "flow", "index-completeness", "--json"])

    assert result.exit_code == 1, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "lost_blocks_found"
    assert payload["ok"] is False
    assert payload["lost_blocks"] == ["orphan"]


def test_cli_index_not_found(runner: CliRunner, project_dir: Path) -> None:
    """No bridge index file exits 3 (index_not_found)."""
    result = runner.invoke(main, [*_config_args(project_dir), "flow", "index-completeness", "--json"])
    assert result.exit_code == 3, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "index_not_found"
    assert payload["mutated"] is False


def test_cli_refuses_canonical_write_target(runner: CliRunner, project_dir: Path) -> None:
    """An --out target resolving to the canonical bridge index is refused (exit 2)."""
    _write_bridge_file(project_dir, "alpha-001.md")
    _write_index(project_dir, _index_for("alpha"))
    for target in ("bridge/INDEX.md", "./bridge/INDEX.md", "BRIDGE/index.md"):
        result = runner.invoke(
            main,
            [*_config_args(project_dir), "flow", "index-completeness", "--out", target, "--json"],
        )
        assert result.exit_code == 2, f"{target}: {result.output}"
        payload = json.loads(result.output)
        assert payload["status"] == "refused"
        assert payload["mutated"] is False


def test_cli_out_writes_report_to_non_canonical_path(runner: CliRunner, project_dir: Path, tmp_path: Path) -> None:
    """--out writes the JSON report to a non-canonical path (never the index)."""
    _write_bridge_file(project_dir, "alpha-001.md")
    _write_index(project_dir, _index_for("alpha"))
    out = tmp_path / "reports" / "completeness.json"

    result = runner.invoke(
        main,
        [*_config_args(project_dir), "flow", "index-completeness", "--out", str(out), "--json"],
    )

    assert result.exit_code == 0, result.output
    assert out.is_file()
    saved = json.loads(out.read_text(encoding="utf-8"))
    assert saved["ok"] is True
    assert saved["lost_blocks"] == []


# --------------------------------------------------------------------------- #
# Structural (AST) guards
# --------------------------------------------------------------------------- #

_MEMBASE_MUTATOR_PREFIXES = ("insert_", "update_", "delete_", "resolve_", "promote_", "retire_")
_FILE_WRITE_ATTRS = {"write_text", "write_bytes", "writelines", "write"}


def test_module_is_read_only() -> None:
    """The oracle module never writes: no file-write attr, no open(), no
    bare canonical ``bridge/INDEX.md`` path literal."""
    source = Path(completeness_module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            assert node.value != "bridge/INDEX.md", "module must not carry the canonical bridge-index path literal"
        if isinstance(node, ast.Attribute):
            assert node.attr not in _FILE_WRITE_ATTRS, f"module must not call file-write attr {node.attr!r}"
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id != "open", "module must not call open()"


def test_module_no_subprocess_no_mutation() -> None:
    """The oracle module imports/references no subprocess and calls no MemBase mutator."""
    source = Path(completeness_module.__file__).read_text(encoding="utf-8")
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
        if isinstance(node, ast.FunctionDef) and node.name == "flow_index_completeness_cmd":
            command_fn = node
            break
    assert command_fn is not None, "flow_index_completeness_cmd not found in cli.py"

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
