"""Tests for the WI-4507 TAFE Bridge-INDEX compatibility-view generator.

Covers (1) renderer purity + non-authoritative-header invariant + shape, (2) the
read-only ``gt flow preview-bridge-index`` CLI (default/stdout/refusal/custom-out
paths), and (3) AST structural guards that prove the renderer module has no
canonical-write surface and the CLI carries the refusal token.

Spec mapping:
- ``SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`` -- TAFE state renderable in the
  bridge-INDEX visual shape.
- ``SPEC-TAFE-R7`` -- MemBase remains canonical; structural guard asserts no
  mutation surface.
- ``SPEC-TAFE-R2`` / ``SPEC-TAFE-R4`` -- stage-claim and required-role context
  surfaced read-only.
- ``GOV-FILE-BRIDGE-AUTHORITY-001`` -- refusal-to-write + non-authoritative
  header keep ``bridge/INDEX.md`` canonical.
"""

from __future__ import annotations

import ast
import json
from datetime import UTC, datetime
from pathlib import Path

from click.testing import CliRunner

import groundtruth_kb.cli as cli_module
import groundtruth_kb.tafe_index_preview as preview_module
from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.tafe_index_preview import (
    NON_AUTHORITATIVE_HEADER,
    BridgeIndexPreview,
    render_tafe_bridge_index_preview,
)
from groundtruth_kb.typed_artifact_flow import TypedArtifactFlowService

FIXED_NOW = datetime(2026, 6, 13, 17, 0, 0, tzinfo=UTC)


def _config_args(project_dir: Path) -> list[str]:
    return ["--config", str(project_dir / "groundtruth.toml")]


def _sample_flows() -> list[dict]:
    return [
        {"id": "FLOWINST-A", "subject_id": "gtkb-alpha"},
        {"id": "FLOWINST-B", "subject_id": "gtkb-beta"},
    ]


def _sample_stages() -> list[dict]:
    return [
        {
            "flow_instance_id": "FLOWINST-A",
            "stage_id": "propose",
            "stage_index": 0,
            "required_role": "prime-builder",
            "status": "completed",
            "claim_status": "unclaimed",
        },
        {
            "flow_instance_id": "FLOWINST-A",
            "stage_id": "review",
            "stage_index": 1,
            "required_role": "loyal-opposition",
            "status": "pending",
            "claim_status": "claimed",
        },
        {
            "flow_instance_id": "FLOWINST-B",
            "stage_id": "propose",
            "stage_index": 0,
            "required_role": "prime-builder",
            "status": "pending",
            "claim_status": "unclaimed",
        },
    ]


def _seed_runtime_instances(project_dir: Path) -> None:
    """Seed a definition + two flow instances + stage instances for CLI tests."""
    db = KnowledgeDB(project_dir / "groundtruth.db")
    try:
        service = TypedArtifactFlowService(db)
        service.create_flow_definition(
            id="FLOW-PREVIEW",
            flow_type="implementation",
            name="Preview flow",
            stages=["propose", "review"],
            required_roles={"propose": "prime-builder", "review": "loyal-opposition"},
            changed_by="test",
            change_reason="seed preview definition",
            source_spec_ids=["SPEC-TAFE-R2", "SPEC-TAFE-R4", "SPEC-TAFE-R7"],
        )
        for suffix, subject in (("A", "gtkb-alpha"), ("B", "gtkb-beta")):
            flow = service.create_flow_instance(
                id=f"FLOWINST-{suffix}",
                flow_definition_id="FLOW-PREVIEW",
                subject_type="bridge-thread",
                subject_id=subject,
                changed_by="test",
                change_reason="seed preview flow",
            )
            service.create_stage_instance(
                id=f"STAGEINST-{suffix}-0",
                flow_instance_id=flow["id"],
                stage_id="propose",
                stage_index=0,
                required_role="prime-builder",
                changed_by="test",
                change_reason="seed propose stage",
            )
            service.create_stage_instance(
                id=f"STAGEINST-{suffix}-1",
                flow_instance_id=flow["id"],
                stage_id="review",
                stage_index=1,
                required_role="loyal-opposition",
                changed_by="test",
                change_reason="seed review stage",
            )
    finally:
        db.close()


def _rendered_text_from_db(project_dir: Path) -> str:
    db = KnowledgeDB(project_dir / "groundtruth.db")
    try:
        service = TypedArtifactFlowService(db)
        return render_tafe_bridge_index_preview(
            service.list_flow_instances(),
            service.list_stage_instances(),
            now=FIXED_NOW,
        ).text
    finally:
        db.close()


# --------------------------------------------------------------------------- #
# Renderer purity / shape
# --------------------------------------------------------------------------- #


def test_non_authoritative_header_is_first_line() -> None:
    preview = render_tafe_bridge_index_preview(_sample_flows(), _sample_stages(), now=FIXED_NOW)
    assert preview.text.splitlines()[0] == NON_AUTHORITATIVE_HEADER


def test_one_section_per_flow_with_descending_stage_order() -> None:
    preview = render_tafe_bridge_index_preview(_sample_flows(), _sample_stages(), now=FIXED_NOW)
    lines = preview.text.splitlines()

    assert lines.count("Document: gtkb-alpha") == 1
    assert lines.count("Document: gtkb-beta") == 1

    alpha_idx = lines.index("Document: gtkb-alpha")
    # Stage lines for FLOWINST-A follow the Document line in descending stage_index:
    # review (index 1) before propose (index 0).
    assert lines[alpha_idx + 1] == "pending: review (role=loyal-opposition, claim=claimed)"
    assert lines[alpha_idx + 2] == "completed: propose (role=prime-builder, claim=unclaimed)"


def test_empty_inputs_render_header_only() -> None:
    preview = render_tafe_bridge_index_preview([], [], now=FIXED_NOW)
    assert preview.text == NON_AUTHORITATIVE_HEADER
    assert preview.flow_instance_count == 0
    assert preview.stage_instance_count == 0


def test_preview_is_never_authoritative() -> None:
    preview = render_tafe_bridge_index_preview(_sample_flows(), _sample_stages(), now=FIXED_NOW)
    assert preview.authoritative is False
    assert BridgeIndexPreview("", 0, 0, FIXED_NOW.isoformat()).authoritative is False


def test_counts_and_generated_at_reflect_inputs() -> None:
    preview = render_tafe_bridge_index_preview(_sample_flows(), _sample_stages(), now=FIXED_NOW)
    assert preview.flow_instance_count == 2
    assert preview.stage_instance_count == 3
    assert preview.generated_at == FIXED_NOW.isoformat()


def test_now_accepts_iso_string_and_coerces_utc() -> None:
    preview = render_tafe_bridge_index_preview([], [], now="2026-06-13T17:00:00Z")
    assert preview.generated_at == FIXED_NOW.isoformat()


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def test_cli_default_writes_to_non_canonical_preview_path(runner: CliRunner, project_dir: Path) -> None:
    _seed_runtime_instances(project_dir)
    expected_text = _rendered_text_from_db(project_dir)

    with runner.isolated_filesystem() as fs:
        result = runner.invoke(main, [*_config_args(project_dir), "flow", "preview-bridge-index", "--json"])
        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["status"] == "preview_written"
        assert payload["authoritative"] is False
        assert payload["mutated"] is False
        assert payload["flow_instance_count"] == 2
        assert payload["stage_instance_count"] == 4

        out = Path(fs) / ".gtkb-state" / "tafe-preview" / "bridge-index-preview.md"
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert content.splitlines()[0] == NON_AUTHORITATIVE_HEADER
        assert content == expected_text
        # The canonical bridge index was never created in the working tree.
        assert not (Path(fs) / "bridge" / "INDEX.md").exists()


def test_cli_stdout_prints_and_writes_no_file(runner: CliRunner, project_dir: Path) -> None:
    _seed_runtime_instances(project_dir)
    with runner.isolated_filesystem() as fs:
        result = runner.invoke(main, [*_config_args(project_dir), "flow", "preview-bridge-index", "--stdout"])
        assert result.exit_code == 0, result.output
        assert NON_AUTHORITATIVE_HEADER in result.output
        assert "Document: gtkb-alpha" in result.output
        assert not (Path(fs) / ".gtkb-state").exists()


def test_cli_refuses_canonical_bridge_index_target(runner: CliRunner, project_dir: Path) -> None:
    for target in ("bridge/INDEX.md", "./bridge/INDEX.md", "BRIDGE/index.md"):
        with runner.isolated_filesystem() as fs:
            result = runner.invoke(
                main,
                [*_config_args(project_dir), "flow", "preview-bridge-index", "--out", target, "--json"],
            )
            assert result.exit_code != 0, f"{target}: expected non-zero exit"
            payload = json.loads(result.output)
            assert payload["status"] == "refused"
            assert payload["mutated"] is False
            # Nothing was written anywhere in the working tree.
            assert not (Path(fs) / "bridge").exists()
            assert not (Path(fs) / ".gtkb-state").exists()


def test_cli_custom_out_path_writes_there(runner: CliRunner, project_dir: Path, tmp_path: Path) -> None:
    _seed_runtime_instances(project_dir)
    out = tmp_path / "custom" / "tafe-preview.md"
    result = runner.invoke(
        main,
        [*_config_args(project_dir), "flow", "preview-bridge-index", "--out", str(out), "--json"],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "preview_written"
    assert out.exists()
    assert out.read_text(encoding="utf-8").splitlines()[0] == NON_AUTHORITATIVE_HEADER


# --------------------------------------------------------------------------- #
# Structural (AST) guards
# --------------------------------------------------------------------------- #

_MEMBASE_MUTATOR_PREFIXES = ("insert_", "update_", "delete_", "resolve_", "promote_", "retire_")
_FILE_WRITE_ATTRS = {"write_text", "write_bytes", "writelines", "write"}


def test_renderer_module_has_no_write_surface() -> None:
    """The renderer module is pure: no subprocess, no file I/O, no MemBase
    mutators, and no bare ``bridge/INDEX.md`` canonical-path literal."""
    source = Path(preview_module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name != "subprocess", "renderer must not import subprocess"
        if isinstance(node, ast.ImportFrom):
            assert node.module != "subprocess", "renderer must not import from subprocess"
        if isinstance(node, ast.Name):
            assert node.id != "subprocess", "renderer must not reference subprocess"
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            assert node.value != "bridge/INDEX.md", "renderer must not carry the canonical bridge-index path literal"
        if isinstance(node, ast.Attribute):
            assert node.attr not in _FILE_WRITE_ATTRS, f"renderer must not call file-write attr {node.attr!r}"
            assert not node.attr.startswith(_MEMBASE_MUTATOR_PREFIXES), f"renderer must not call mutator {node.attr!r}"
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id != "open", "renderer must not call open()"


def test_cli_command_retains_canonical_refusal_token() -> None:
    """The CLI command function carries the literal ``bridge/INDEX.md`` token in
    a refusal branch so a future refactor cannot silently delete the guard."""
    source = Path(cli_module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)

    command_fn = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "flow_preview_bridge_index_cmd":
            command_fn = node
            break
    assert command_fn is not None, "flow_preview_bridge_index_cmd not found in cli.py"

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
