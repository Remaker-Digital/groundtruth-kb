"""Tests for governed document-artifact author provenance."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.check_document_author_metadata import audit_paths, load_config
from scripts.document_author_metadata import (
    REQUIRED_AUTHOR_FIELDS,
    DocumentAuthorConfig,
    format_author_metadata,
    is_governed_document_path,
    validate_author_metadata,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CLAUDE_HOOK = PROJECT_ROOT / ".claude" / "hooks" / "document_author_provenance_gate.py"
CODEX_HOOK = PROJECT_ROOT / ".codex" / "gtkb-hooks" / "document_author_provenance_gate.py"
CODEX_HOOKS_JSON = PROJECT_ROOT / ".codex" / "hooks.json"

AUTHOR_METADATA = {
    "author_identity": "Codex Prime Builder",
    "author_harness_id": "A",
    "author_session_context_id": "session-123",
    "author_model": "GPT-5 Codex",
    "author_model_version": "gpt-5",
    "author_model_configuration": "Codex desktop automation",
}


def _metadata_content() -> str:
    return format_author_metadata(AUTHOR_METADATA) + "\n# Governed Document\n"


def _run_hook(hook: Path, payload: dict[str, object]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(hook)],
        cwd=PROJECT_ROOT,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
    )


def test_complete_author_metadata_is_valid() -> None:
    result = validate_author_metadata(_metadata_content())

    assert result.is_valid
    assert result.gaps == ()
    assert tuple(result.metadata[field] for field in REQUIRED_AUTHOR_FIELDS)


def test_placeholder_author_metadata_is_rejected() -> None:
    content = _metadata_content().replace("author_model: GPT-5 Codex", "author_model: TBD")

    result = validate_author_metadata(content)

    assert not result.is_valid
    assert result.invalid_fields == ("author_model (placeholder/invalid)",)


def test_governance_waiver_is_accepted() -> None:
    result = validate_author_metadata("document_author_provenance_waiver: DELIB-1234 - approved exception\n")

    assert result.is_valid
    assert result.waiver == "DELIB-1234 - approved exception"


def test_governed_document_surface_matching() -> None:
    config = DocumentAuthorConfig(
        governed_surfaces=("bridge/**/*.md", ".claude/rules/**/*.md"),
        exclusions=(".claude/worktrees/**",),
    )

    assert is_governed_document_path("bridge/example-001.md", config)
    assert is_governed_document_path(".claude/rules/example.md", config)
    assert not is_governed_document_path(".claude/worktrees/example/bridge/item.md", config)
    assert not is_governed_document_path("scripts/example.py", config)


def test_audit_reports_missing_metadata(tmp_path: Path) -> None:
    config = DocumentAuthorConfig(governed_surfaces=("docs/**/*.md",), exclusions=())
    good = tmp_path / "docs" / "good.md"
    bad = tmp_path / "docs" / "bad.md"
    good.parent.mkdir()
    good.write_text(_metadata_content(), encoding="utf-8")
    bad.write_text("# Missing\n", encoding="utf-8")

    findings = audit_paths(tmp_path, [good, bad], config)

    assert [finding.path for finding in findings] == ["docs/bad.md"]
    assert findings[0].missing_fields == REQUIRED_AUTHOR_FIELDS


def test_config_loads_live_contract() -> None:
    config = load_config(PROJECT_ROOT)

    assert "bridge/**/*.md" in config.governed_surfaces
    assert ".claude/worktrees/**" in config.exclusions


def test_hook_blocks_new_governed_write_without_metadata() -> None:
    payload = {
        "tool_name": "Write",
        "cwd": str(PROJECT_ROOT),
        "tool_input": {
            "file_path": "bridge/document-author-provenance-test-new.md",
            "content": "# Missing provenance\n",
        },
    }

    result = _run_hook(CLAUDE_HOOK, payload)

    assert result.returncode == 2
    assert json.loads(result.stdout)["decision"] == "block"


def test_hook_allows_new_governed_write_with_metadata() -> None:
    payload = {
        "tool_name": "Write",
        "cwd": str(PROJECT_ROOT),
        "tool_input": {
            "file_path": "bridge/document-author-provenance-test-new.md",
            "content": _metadata_content(),
        },
    }

    result = _run_hook(CLAUDE_HOOK, payload)

    assert result.returncode == 0
    assert json.loads(result.stdout) == {}


def test_hook_blocks_add_file_patch_without_metadata() -> None:
    payload = {
        "tool_name": "apply_patch",
        "cwd": str(PROJECT_ROOT),
        "tool_input": {
            "patch": "*** Begin Patch\n*** Add File: docs/new-contract.md\n+# Missing provenance\n*** End Patch\n"
        },
    }

    result = _run_hook(CLAUDE_HOOK, payload)

    assert result.returncode == 2
    assert "docs/new-contract.md" in json.loads(result.stdout)["reason"]


def test_codex_wrapper_blocks_add_file_patch_without_metadata() -> None:
    payload = {
        "tool_name": "apply_patch",
        "cwd": str(PROJECT_ROOT),
        "tool_input": {
            "patch": "*** Begin Patch\n*** Add File: docs/new-codex-contract.md\n+# Missing provenance\n*** End Patch\n"
        },
    }

    result = _run_hook(CODEX_HOOK, payload)

    assert result.returncode == 2
    assert "docs/new-codex-contract.md" in json.loads(result.stdout)["reason"]


def test_codex_apply_patch_registration_present() -> None:
    hooks = json.loads(CODEX_HOOKS_JSON.read_text(encoding="utf-8"))
    registrations = [
        entry
        for entry in hooks["hooks"]["PreToolUse"]
        if entry.get("matcher") == "apply_patch"
        for hook in entry.get("hooks", [])
        if "document_author_provenance_gate.py" in hook.get("command", "")
    ]

    assert registrations


def test_hook_allows_existing_file_edits_without_metadata(tmp_path: Path) -> None:
    existing = tmp_path / "docs" / "existing.md"
    existing.parent.mkdir()
    existing.write_text("# Existing grandfathered file\n", encoding="utf-8")
    payload = {
        "tool_name": "Write",
        "cwd": str(PROJECT_ROOT),
        "tool_input": {"file_path": str(existing), "content": "# Still grandfathered\n"},
    }

    result = _run_hook(CLAUDE_HOOK, payload)

    assert result.returncode == 0
    assert json.loads(result.stdout) == {}
