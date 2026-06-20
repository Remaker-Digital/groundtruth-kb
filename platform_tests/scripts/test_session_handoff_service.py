"""Tests for the deterministic handoff-prompt service.

Authority: ``SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001`` (MemBase rowid
8562). Verifies the spec's CLI surface, Python API signature, 4 machine-
checkable assertions, idempotency contract, three output surfaces, input
exclusions, terminology lock, and absence of AI-mediated prompt assembly.

Bridge thread: ``gtkb-handoff-prompt-deterministic-service-impl`` GO at
``-005``.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner
from groundtruth_kb.cli import main as gt_cli
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.session import handoff as handoff_module
from groundtruth_kb.session.handoff import HandoffError, generate

_FIXED_ENVELOPE: dict[str, Any] = {
    "harness_id": "B",
    "harness_name": "claude",
    "role_resolved": "prime-builder",
    "project_id": "PROJECT-GTKB-TEST",
    "active_work_item_id": "WI-4299",
    "work_item_ids": ["WI-4299"],
    "closed_at": "2026-06-05T01-00-00Z",
    "wrap_outcome": "complete",
    "topics": [
        {
            "type": "test-topic",
            "close_outcome": "verified",
            "opened_at": "2026-06-05T00:30:00Z",
            "closed_at": "2026-06-05T00:55:00Z",
        }
    ],
}

_FIXED_BRIDGE_INDEX = """# Bridge Index

Document: gtkb-test-thread-001
GO: bridge/gtkb-test-thread-001-002.md
NEW: bridge/gtkb-test-thread-001-001.md

Document: gtkb-other-thread
VERIFIED: bridge/gtkb-other-thread-003.md
GO: bridge/gtkb-other-thread-002.md
NEW: bridge/gtkb-other-thread-001.md
"""

_HARNESS_IDENTITIES = {
    "harnesses": {
        "claude": {
            "harness_id": "B",
            "status": "active",
        }
    }
}


def _make_project_root(tmp_path: Path, session_id: str | None = None) -> Path:
    """Stage a minimal GT-KB-shaped project root inside tmp_path.

    When ``session_id`` is provided, the staged envelope carries an explicit
    ``session_id`` field so the production session_id-driven archive selector
    (per ``SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001`` § Inputs) finds it.
    """
    root = tmp_path / "gt-kb-root"
    root.mkdir(parents=True)
    (root / "harness-state").mkdir()
    (root / "harness-state" / "harness-identities.json").write_text(
        json.dumps(_HARNESS_IDENTITIES, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    archive = root / "harness-state" / "claude" / "session-envelope-archive"
    archive.mkdir(parents=True)
    envelope_body: dict[str, Any] = dict(_FIXED_ENVELOPE)
    if session_id is not None:
        envelope_body["session_id"] = session_id
    envelope_file = archive / f"{_FIXED_ENVELOPE['closed_at']}-session-envelope.json"
    envelope_file.write_text(
        json.dumps(envelope_body, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (root / "bridge").mkdir()
    (root / "bridge" / "INDEX.md").write_text(_FIXED_BRIDGE_INDEX, encoding="utf-8")
    (root / ".claude").mkdir()
    return root


def _stage_multi_harness_root(
    tmp_path: Path,
    identities: dict[str, Any],
    envelopes: dict[str, list[dict[str, Any]]],
) -> Path:
    root = tmp_path / "multi-harness-root"
    root.mkdir(parents=True)
    (root / "harness-state").mkdir()
    (root / "harness-state" / "harness-identities.json").write_text(
        json.dumps(identities, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    for harness_name, harness_envelopes in envelopes.items():
        archive = root / "harness-state" / harness_name / "session-envelope-archive"
        archive.mkdir(parents=True)
        for index, envelope in enumerate(harness_envelopes, start=1):
            body = dict(_FIXED_ENVELOPE)
            body.update(envelope)
            closed_at = str(body.get("closed_at") or f"2026-06-05T0{index}-00-00Z")
            body["closed_at"] = closed_at
            (archive / f"{closed_at}-session-envelope.json").write_text(
                json.dumps(body, indent=2, sort_keys=True),
                encoding="utf-8",
            )
    (root / "bridge").mkdir()
    (root / "bridge" / "INDEX.md").write_text(_FIXED_BRIDGE_INDEX, encoding="utf-8")
    (root / ".claude").mkdir()
    return root


def _make_db(tmp_path: Path) -> KnowledgeDB:
    db_path = tmp_path / "test.db"
    return KnowledgeDB(db_path=db_path)


# ---------------------------------------------------------------------------
# Spec assertion 1: Python API signature
# ---------------------------------------------------------------------------


def test_handoff_module_exports_generate_function_with_correct_signature() -> None:
    assert callable(generate)
    sig = inspect.signature(generate)
    assert "session_id" in sig.parameters
    # session_id is the first positional parameter per the spec API.
    first_param = next(iter(sig.parameters.values()))
    assert first_param.name == "session_id"


# ---------------------------------------------------------------------------
# Spec assertion 2: CLI subcommand registration
# ---------------------------------------------------------------------------


def test_cli_session_handoff_generate_subcommand_registered() -> None:
    runner = CliRunner()
    result = runner.invoke(gt_cli, ["session", "handoff", "generate", "--help"])
    assert result.exit_code == 0, result.output
    assert "--session-id" in result.output
    assert "--harness-name" in result.output


def test_cli_session_handoff_get_subcommand_registered() -> None:
    runner = CliRunner()
    result = runner.invoke(gt_cli, ["session", "handoff", "get", "--help"])
    assert result.exit_code == 0, result.output
    assert "SESSION_ID" in result.output.upper()


# ---------------------------------------------------------------------------
# Spec assertion 3: session_prompts table schema present
# ---------------------------------------------------------------------------


def test_session_prompts_table_present_in_schema(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    # The schema path cited in the SPEC ("groundtruth_kb/db/schema.py") does
    # not exist; sqlite_master is the spec's "(or equivalent)" verification.
    conn = db._get_conn()
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='session_prompts'",
    ).fetchone()
    assert row is not None
    assert row[0] == "session_prompts"


# ---------------------------------------------------------------------------
# Spec assertion 4: No AI-mediation imports in the service module
# ---------------------------------------------------------------------------


_AI_MEDIATION_TOKENS = (
    "anthropic",
    "openai",
    "litellm",
    "google.generativeai",
    "google.genai",
    "cohere",
    "together",
    "groq",
    "mistralai",
    "langchain",
    "llama_index",
    "haystack",
    "boto3",
)


def test_handoff_module_has_no_ai_mediation_imports() -> None:
    source_path = Path(handoff_module.__file__)
    source = source_path.read_text(encoding="utf-8")
    for token in _AI_MEDIATION_TOKENS:
        assert token not in source, f"Unexpected AI-mediation token {token!r} in handoff.py"


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


def test_handoff_raises_handoff_error_on_missing_archive_dir(tmp_path: Path) -> None:
    root = tmp_path / "missing-archive-root"
    root.mkdir()
    (root / "harness-state").mkdir()
    (root / "harness-state" / "harness-identities.json").write_text(
        json.dumps(_HARNESS_IDENTITIES, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    db = _make_db(tmp_path)
    with pytest.raises(HandoffError):
        generate(project_root=root, db=db)


def test_handoff_raises_handoff_error_on_missing_session_envelope(tmp_path: Path) -> None:
    root = tmp_path / "empty-archive-root"
    root.mkdir()
    (root / "harness-state").mkdir()
    (root / "harness-state" / "harness-identities.json").write_text(
        json.dumps(_HARNESS_IDENTITIES, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (root / "harness-state" / "claude" / "session-envelope-archive").mkdir(parents=True)
    db = _make_db(tmp_path)
    with pytest.raises(HandoffError):
        generate(project_root=root, db=db)


# ---------------------------------------------------------------------------
# Determinism + idempotency
# ---------------------------------------------------------------------------


def test_handoff_generate_deterministic_byte_stability(tmp_path: Path) -> None:
    root_a = _make_project_root(tmp_path / "a-side", session_id="S-DET-1")
    root_b = _make_project_root(tmp_path / "b-side", session_id="S-DET-1")
    db_a = _make_db(tmp_path / "a-side")
    db_b = _make_db(tmp_path / "b-side")
    result_a = generate(session_id="S-DET-1", project_root=root_a, db=db_a)
    result_b = generate(session_id="S-DET-1", project_root=root_b, db=db_b)
    assert result_a["prompt_markdown"] == result_b["prompt_markdown"]


def test_db_get_session_prompt_by_idempotency_key_returns_existing(tmp_path: Path) -> None:
    db = _make_db(tmp_path)
    db.insert_session_prompt(
        "S-IDEM-1",
        "body",
        context={"idempotency_key": "sha256:abc123"},
    )
    row = db.get_session_prompt_by_idempotency_key("S-IDEM-1", "sha256:abc123")
    assert row is not None
    assert row["prompt_text"] == "body"
    assert db.get_session_prompt_by_idempotency_key("S-IDEM-1", "sha256:other") is None


def test_handoff_generate_idempotent_on_same_inputs(tmp_path: Path) -> None:
    root = _make_project_root(tmp_path, session_id="S-IDEM")
    db = _make_db(tmp_path)
    first = generate(session_id="S-IDEM", project_root=root, db=db)
    second = generate(session_id="S-IDEM", project_root=root, db=db)
    assert first["session_prompts_id"] == second["session_prompts_id"]
    count_row = (
        db._get_conn()
        .execute(
            "SELECT COUNT(*) FROM session_prompts WHERE session_id = ?",
            ("S-IDEM",),
        )
        .fetchone()
    )
    assert count_row[0] == 1


# ---------------------------------------------------------------------------
# Output surfaces (3 per spec)
# ---------------------------------------------------------------------------


def test_handoff_writes_session_prompts_row(tmp_path: Path) -> None:
    root = _make_project_root(tmp_path, session_id="S-OUT-DB")
    db = _make_db(tmp_path)
    result = generate(session_id="S-OUT-DB", project_root=root, db=db)
    assert result["session_prompts_id"].startswith("session_prompts:")
    row = db.get_session_prompt("S-OUT-DB")
    assert row is not None
    assert row["prompt_text"] == result["prompt_markdown"]


def test_handoff_writes_handoff_markdown_file(tmp_path: Path) -> None:
    root = _make_project_root(tmp_path, session_id="S-OUT-MD")
    db = _make_db(tmp_path)
    result = generate(session_id="S-OUT-MD", project_root=root, db=db)
    rel = result["output_files"][0]
    md_path = root / rel
    assert md_path.is_file()
    assert md_path.read_text(encoding="utf-8") == result["prompt_markdown"]
    assert md_path.name == "handoff-S-OUT-MD.md"


def test_cli_session_handoff_generate_echoes_prompt_to_stdout(tmp_path: Path) -> None:
    root = _make_project_root(tmp_path, session_id="S-CLI-OUT")
    config_path = root / "groundtruth.toml"
    config_path.write_text(f'[groundtruth]\nproject_root = "{root.as_posix()}"\n', encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(
        gt_cli,
        [
            "--config",
            str(config_path),
            "session",
            "handoff",
            "generate",
            "--session-id",
            "S-CLI-OUT",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "Handoff Prompt" in result.output


# ---------------------------------------------------------------------------
# Input exclusions + terminology lock
# ---------------------------------------------------------------------------


def test_handoff_prompt_body_excludes_deliberation_harvest_and_backlog_rollup(tmp_path: Path) -> None:
    root = _make_project_root(tmp_path, session_id="S-EXCL")
    db = _make_db(tmp_path)
    result = generate(session_id="S-EXCL", project_root=root, db=db)
    body = result["prompt_markdown"].lower()
    # Spec § Inputs limits to envelope + bridge index. DA harvest, backlog
    # rollup, and source-tree state must not appear.
    for forbidden in (
        "deliberation_harvest",
        "deliberation-harvest",
        "backlog rollup",
        "backlog_rollup",
        "source tree state",
        "source-tree state",
    ):
        assert forbidden not in body, f"Prompt body must not include {forbidden!r}"


def test_handoff_prompt_uses_handoff_terminology_not_continuation(tmp_path: Path) -> None:
    root = _make_project_root(tmp_path, session_id="S-TERM")
    db = _make_db(tmp_path)
    result = generate(session_id="S-TERM", project_root=root, db=db)
    body = result["prompt_markdown"].lower()
    assert "handoff prompt" in body
    assert "continuation prompt" not in body


def test_handoff_reads_versioned_bridge_files_when_index_is_absent(tmp_path: Path) -> None:
    root = _make_project_root(tmp_path, session_id="S-NOINDEX")
    index_path = root / "bridge" / "INDEX.md"
    index_path.unlink()
    (root / "bridge" / "gtkb-test-thread-001-001.md").write_text("NEW\n\n# Proposal\n", encoding="utf-8")
    (root / "bridge" / "gtkb-test-thread-001-002.md").write_text("GO\n\n# Verdict\n", encoding="utf-8")
    db = _make_db(tmp_path)

    result = generate(session_id="S-NOINDEX", project_root=root, db=db)

    body = result["prompt_markdown"]
    assert "GO: gtkb-test-thread-001 -> bridge/gtkb-test-thread-001-002.md" in body
    assert "versioned bridge file chain" in body


# ---------------------------------------------------------------------------
# Regression: live identities schema must not select non-present harness
# (NO-GO -007 FINDING-P1-002 — bridge/gtkb-handoff-prompt-deterministic-service-impl-007.md)
# ---------------------------------------------------------------------------


_LIVE_SHAPE_HARNESS_IDENTITIES = {
    "harnesses": {
        "claude": {"id": "B"},
        "codex": {"id": "A"},
        "antigravity": {"id": "C"},
    }
}


def test_resolve_active_harness_skips_registered_but_non_present_harness(
    tmp_path: Path,
) -> None:
    """Live ``harness-identities.json`` omits ``status``; with three harnesses
    registered but only ``claude`` having a session-envelope archive directory,
    the resolver must select ``claude`` and never alphabetically fall back to
    ``antigravity``.
    """
    root = tmp_path / "live-shape-root"
    root.mkdir()
    (root / "harness-state").mkdir()
    (root / "harness-state" / "harness-identities.json").write_text(
        json.dumps(_LIVE_SHAPE_HARNESS_IDENTITIES, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    archive = root / "harness-state" / "claude" / "session-envelope-archive"
    archive.mkdir(parents=True)
    envelope_body = dict(_FIXED_ENVELOPE)
    envelope_body["session_id"] = "S-LIVE-SHAPE"
    envelope_file = archive / f"{_FIXED_ENVELOPE['closed_at']}-session-envelope.json"
    envelope_file.write_text(
        json.dumps(envelope_body, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (root / "bridge").mkdir()
    (root / "bridge" / "INDEX.md").write_text(_FIXED_BRIDGE_INDEX, encoding="utf-8")
    (root / ".claude").mkdir()
    db = _make_db(tmp_path)
    result = generate(session_id="S-LIVE-SHAPE", project_root=root, db=db)
    assert result["prompt_markdown"]
    # The handoff body cites the resolved harness via the envelope's
    # ``harness_name`` field; the fixture's envelope is "claude". A regression
    # to alphabetic fallback would error before reaching prompt assembly
    # (the missing antigravity archive raises HandoffError).
    assert "claude" in result["prompt_markdown"]


def test_resolve_active_harness_errors_when_no_harness_has_archive(
    tmp_path: Path,
) -> None:
    """Three registered harnesses but zero archive directories → HandoffError
    rather than alphabetic selection. This is the production state until
    WI-4293 lands.
    """
    root = tmp_path / "no-archives-root"
    root.mkdir()
    (root / "harness-state").mkdir()
    (root / "harness-state" / "harness-identities.json").write_text(
        json.dumps(_LIVE_SHAPE_HARNESS_IDENTITIES, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    db = _make_db(tmp_path)
    with pytest.raises(HandoffError) as excinfo:
        generate(project_root=root, db=db)
    msg = str(excinfo.value)
    assert "antigravity" not in msg
    assert "session-envelope archive" in msg


def test_resolve_active_harness_errors_on_ambiguous_multiple_archives(
    tmp_path: Path,
) -> None:
    """Two registered harnesses, both with archives, neither marked active
    → HandoffError demanding explicit selection rather than alphabetic pick.
    """
    root = tmp_path / "ambiguous-root"
    root.mkdir()
    (root / "harness-state").mkdir()
    identities = {
        "harnesses": {
            "claude": {"id": "B"},
            "codex": {"id": "A"},
        }
    }
    (root / "harness-state" / "harness-identities.json").write_text(
        json.dumps(identities, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    for name in ("claude", "codex"):
        archive = root / "harness-state" / name / "session-envelope-archive"
        archive.mkdir(parents=True)
        (archive / f"{_FIXED_ENVELOPE['closed_at']}-session-envelope.json").write_text(
            json.dumps(_FIXED_ENVELOPE, indent=2, sort_keys=True),
            encoding="utf-8",
        )
    (root / "bridge").mkdir()
    (root / "bridge" / "INDEX.md").write_text(_FIXED_BRIDGE_INDEX, encoding="utf-8")
    db = _make_db(tmp_path)
    with pytest.raises(HandoffError) as excinfo:
        generate(project_root=root, db=db)
    msg = str(excinfo.value)
    assert "multiple" in msg.lower() or "ambiguous" in msg.lower() or "supply" in msg.lower()


def test_default_path_resolves_session_id_across_archives(tmp_path: Path) -> None:
    identities = {
        "harnesses": {
            "claude": {"id": "B"},
            "antigravity": {"id": "C", "status": "active"},
            "openrouter": {"id": "F", "status": "active"},
            "codex": {"id": "A"},
        }
    }
    root = _stage_multi_harness_root(
        tmp_path,
        identities,
        {
            "claude": [
                {
                    "harness_id": "B",
                    "harness_name": "claude",
                    "session_id": "B-CROSS-ARCHIVE",
                }
            ],
        },
    )
    db = _make_db(tmp_path)

    result = generate(session_id="B-CROSS-ARCHIVE", project_root=root, db=db)

    body = result["prompt_markdown"]
    assert "- harness_name: claude" in body
    assert result["session_id"] == "B-CROSS-ARCHIVE"


def test_default_path_raises_when_session_id_matches_multiple_archives(tmp_path: Path) -> None:
    identities = {
        "harnesses": {
            "claude": {"id": "B"},
            "codex": {"id": "A"},
        }
    }
    root = _stage_multi_harness_root(
        tmp_path,
        identities,
        {
            "claude": [
                {
                    "harness_id": "B",
                    "harness_name": "claude",
                    "session_id": "S-DUPLICATE",
                    "closed_at": "2026-06-05T01-00-00Z",
                }
            ],
            "codex": [
                {
                    "harness_id": "A",
                    "harness_name": "codex",
                    "session_id": "S-DUPLICATE",
                    "closed_at": "2026-06-05T02-00-00Z",
                }
            ],
        },
    )
    db = _make_db(tmp_path)

    with pytest.raises(HandoffError) as excinfo:
        generate(session_id="S-DUPLICATE", project_root=root, db=db)

    msg = str(excinfo.value).lower()
    assert "ambiguous" in msg
    assert "claude" in msg
    assert "codex" in msg


def test_default_path_raises_when_session_id_matches_no_archive(tmp_path: Path) -> None:
    identities = {
        "harnesses": {
            "claude": {"id": "B"},
            "codex": {"id": "A"},
        }
    }
    root = _stage_multi_harness_root(
        tmp_path,
        identities,
        {
            "claude": [{"harness_id": "B", "harness_name": "claude", "session_id": "S-CLAUDE"}],
            "codex": [{"harness_id": "A", "harness_name": "codex", "session_id": "S-CODEX"}],
        },
    )
    db = _make_db(tmp_path)

    with pytest.raises(HandoffError) as excinfo:
        generate(session_id="S-MISSING", project_root=root, db=db)

    msg = str(excinfo.value).lower()
    assert "no archived envelope matches" in msg
    assert "claude" in msg
    assert "codex" in msg


def test_default_path_resolves_active_harness_when_session_id_omitted(tmp_path: Path) -> None:
    identities = {
        "harnesses": {
            "claude": {"id": "B"},
            "antigravity": {"id": "C", "status": "active"},
            "openrouter": {"id": "F", "status": "active"},
        }
    }
    root = _stage_multi_harness_root(
        tmp_path,
        identities,
        {
            "claude": [
                {
                    "harness_id": "B",
                    "harness_name": "claude",
                    "session_id": "S-OMITTED",
                }
            ],
        },
    )
    db = _make_db(tmp_path)

    result = generate(project_root=root, db=db)

    assert "- harness_name: claude" in result["prompt_markdown"]
    assert result["session_id"] == "B-2026-06-05T01-00-00Z"


def test_explicit_harness_name_override_resolves_within_registered_archive(tmp_path: Path) -> None:
    identities = {
        "harnesses": {
            "claude": {"id": "B"},
            "codex": {"id": "A"},
        }
    }
    root = _stage_multi_harness_root(
        tmp_path,
        identities,
        {
            "claude": [
                {
                    "harness_id": "B",
                    "harness_name": "claude",
                    "session_id": "S-OVERRIDE",
                    "closed_at": "2026-06-05T01-00-00Z",
                }
            ],
            "codex": [
                {
                    "harness_id": "A",
                    "harness_name": "codex",
                    "session_id": "S-OVERRIDE",
                    "closed_at": "2026-06-05T02-00-00Z",
                }
            ],
        },
    )
    db = _make_db(tmp_path)

    result = generate(session_id="S-OVERRIDE", project_root=root, db=db, harness_name="claude")

    body = result["prompt_markdown"]
    assert "- harness_name: claude" in body
    assert "- harness_id: B" in body
    assert "2026-06-05T01-00-00Z-session-envelope.json" in body
    assert "- harness_name: codex" not in body


def test_explicit_harness_name_override_with_non_matching_session_id_fails(tmp_path: Path) -> None:
    identities = {
        "harnesses": {
            "claude": {"id": "B"},
            "codex": {"id": "A"},
        }
    }
    root = _stage_multi_harness_root(
        tmp_path,
        identities,
        {
            "claude": [{"harness_id": "B", "harness_name": "claude", "session_id": "S-CLAUDE"}],
            "codex": [{"harness_id": "A", "harness_name": "codex", "session_id": "S-CODEX"}],
        },
    )
    db = _make_db(tmp_path)

    with pytest.raises(HandoffError) as excinfo:
        generate(session_id="S-CODEX", project_root=root, db=db, harness_name="claude")

    msg = str(excinfo.value).lower()
    assert "no archived envelope matches" in msg
    assert "claude" in msg


def test_explicit_harness_name_override_rejects_unknown_name(tmp_path: Path) -> None:
    root = _make_project_root(tmp_path, session_id="S-UNKNOWN")
    db = _make_db(tmp_path)

    with pytest.raises(HandoffError) as excinfo:
        generate(session_id="S-UNKNOWN", project_root=root, db=db, harness_name="unregistered")

    assert "not a registered harness" in str(excinfo.value)


def test_explicit_harness_name_override_rejects_parent_traversal(tmp_path: Path) -> None:
    root = _make_project_root(tmp_path, session_id="S-PARENT")
    db = _make_db(tmp_path)

    for invalid_name in ("..", "../claude"):
        with pytest.raises(HandoffError) as excinfo:
            generate(session_id="S-PARENT", project_root=root, db=db, harness_name=invalid_name)
        assert "invalid harness name" in str(excinfo.value)


def test_explicit_harness_name_override_rejects_path_separators(tmp_path: Path) -> None:
    root = _make_project_root(tmp_path, session_id="S-SEPARATOR")
    db = _make_db(tmp_path)

    for invalid_name in ("claude/extra", "claude\\extra"):
        with pytest.raises(HandoffError) as excinfo:
            generate(session_id="S-SEPARATOR", project_root=root, db=db, harness_name=invalid_name)
        assert "invalid harness name" in str(excinfo.value)


def test_explicit_harness_name_override_rejects_absolute_path(tmp_path: Path) -> None:
    root = _make_project_root(tmp_path, session_id="S-ABSOLUTE")
    db = _make_db(tmp_path)

    for invalid_name in ("C:/claude", "/claude"):
        with pytest.raises(HandoffError) as excinfo:
            generate(session_id="S-ABSOLUTE", project_root=root, db=db, harness_name=invalid_name)
        assert "invalid harness name" in str(excinfo.value)


# ---------------------------------------------------------------------------
# Regression: session_id drives envelope selection
# (NO-GO -009 FINDING-P1-001 — bridge/gtkb-handoff-prompt-deterministic-service-impl-009.md)
# Spec authority: SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001 § Inputs
# (bridge/gtkb-handoff-prompt-deterministic-service-001.md:278) requires
# <harness_name> and <closed_at-ISO> to be resolved from the session_id +
# directory contents at service invocation time.
# ---------------------------------------------------------------------------


def _stage_two_envelopes_root(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    """Stage a root with two archived envelopes (S-OLD, S-NEW) in one harness.

    Returns ``(root, {"old_session_id": ..., "new_session_id": ..., "old_filename": ..., "new_filename": ...})``.
    """
    root = tmp_path / "two-envelope-root"
    root.mkdir(parents=True)
    (root / "harness-state").mkdir()
    (root / "harness-state" / "harness-identities.json").write_text(
        json.dumps(_HARNESS_IDENTITIES, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    archive = root / "harness-state" / "claude" / "session-envelope-archive"
    archive.mkdir(parents=True)

    old_closed_at = "2026-06-05T01-00-00Z"
    new_closed_at = "2026-06-05T02-00-00Z"
    old_envelope = dict(_FIXED_ENVELOPE)
    old_envelope["closed_at"] = old_closed_at
    old_envelope["session_id"] = "S-OLD"
    new_envelope = dict(_FIXED_ENVELOPE)
    new_envelope["closed_at"] = new_closed_at
    new_envelope["session_id"] = "S-NEW"
    old_filename = f"{old_closed_at}-session-envelope.json"
    new_filename = f"{new_closed_at}-session-envelope.json"
    (archive / old_filename).write_text(
        json.dumps(old_envelope, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (archive / new_filename).write_text(
        json.dumps(new_envelope, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (root / "bridge").mkdir()
    (root / "bridge" / "INDEX.md").write_text(_FIXED_BRIDGE_INDEX, encoding="utf-8")
    (root / ".claude").mkdir()
    return root, {
        "old_session_id": "S-OLD",
        "new_session_id": "S-NEW",
        "old_filename": old_filename,
        "new_filename": new_filename,
    }


def test_explicit_session_id_selects_matching_envelope_not_lex_latest(
    tmp_path: Path,
) -> None:
    """With two archived envelopes (S-OLD older than S-NEW), an explicit
    ``session_id='S-OLD'`` must select the S-OLD envelope. Selecting the
    lex-latest envelope (S-NEW) and merely labeling it 'S-OLD' is the
    behavioral bug FINDING-P1-001 documents.
    """
    root, info = _stage_two_envelopes_root(tmp_path)
    db = _make_db(tmp_path)
    result = generate(session_id=info["old_session_id"], project_root=root, db=db)
    body = result["prompt_markdown"]
    assert info["old_filename"] in body, (
        f"Expected handoff body to cite old envelope filename {info['old_filename']!r}; "
        f"got body that lacked it. Repro of NO-GO -009 FINDING-P1-001."
    )
    assert info["new_filename"] not in body, (
        f"Handoff body unexpectedly cited the newer envelope {info['new_filename']!r} "
        "when caller requested S-OLD. Selection still favors lex-latest envelope."
    )


def test_explicit_unknown_session_id_raises_handoff_error(tmp_path: Path) -> None:
    """An explicit ``session_id`` that matches no archived envelope must
    raise ``HandoffError`` rather than silently fall back to the lex-latest
    envelope.
    """
    root, _info = _stage_two_envelopes_root(tmp_path)
    db = _make_db(tmp_path)
    with pytest.raises(HandoffError) as excinfo:
        generate(session_id="S-NONEXISTENT", project_root=root, db=db)
    msg = str(excinfo.value).lower()
    assert "no archived envelope matches" in msg or "no match" in msg
    assert "s-nonexistent" in msg


def test_omitted_session_id_falls_back_to_lex_latest_envelope(tmp_path: Path) -> None:
    """When ``session_id`` is omitted, the service must fall back to the
    most-recently-archived envelope (lex-latest closed_at-ISO) for the active
    harness. This preserves the wrap-procedure call site that hands the just-
    archived envelope to a callee with no prior session_id binding.
    """
    root, info = _stage_two_envelopes_root(tmp_path)
    db = _make_db(tmp_path)
    result = generate(project_root=root, db=db)
    body = result["prompt_markdown"]
    assert info["new_filename"] in body, (
        "Omitted session_id must select the lex-latest envelope; body lacked S-NEW filename."
    )
    # The derived session_id for the S-NEW envelope is "{harness_id}-{closed_at}"
    # per `_derive_session_id`. Verify the body cites the new envelope's
    # canonical session identity.
    assert "S-NEW" in result["session_id"] or "2026-06-05T02-00-00Z" in result["session_id"]
