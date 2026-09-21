"""Tests for governed document-artifact author provenance."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_document_author_metadata import audit_paths, load_config
from scripts.document_author_metadata import (
    REQUIRED_AUTHOR_FIELDS,
    DocumentAuthorConfig,
    format_author_metadata,
    is_governed_document_path,
    validate_author_metadata,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CLAUDE_HOOK = PROJECT_ROOT / ".harness-baseline-configuration" / "hooks" / "document_author_provenance_gate.py"
# Both native registrations run the authored gate through their native adapters.
CODEX_HOOK = PROJECT_ROOT / ".harness-baseline-configuration" / "hooks" / "document_author_provenance_gate.py"
BASELINE_HOOK = PROJECT_ROOT / ".harness-baseline-configuration" / "hooks" / "document_author_provenance_gate.py"
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
        [sys.executable, "-B", str(hook)],
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


@pytest.mark.parametrize(
    "identifier",
    ["GOV-EXAMPLE-001", "SPEC-EXAMPLE-001", "DCL-EXAMPLE-001", "DELIB-1234", "bridge/example.md", "PAUTH-1234"],
)
@pytest.mark.parametrize("metadata", ["missing", "placeholder"])
def test_waiver_cannot_bypass_required_metadata(identifier: str, metadata: str) -> None:
    content = (
        "" if metadata == "missing" else _metadata_content().replace("author_model: GPT-5 Codex", "author_model: TBD")
    )
    content += f"document_author_provenance_waiver: {identifier} - claimed exception\n"

    result = validate_author_metadata(content)

    assert not result.is_valid
    if metadata == "missing":
        assert result.missing_fields == REQUIRED_AUTHOR_FIELDS
    else:
        assert result.invalid_fields == ("author_model (placeholder/invalid)",)


@pytest.mark.parametrize(
    "identifier",
    ["GOV-EXAMPLE-001", "SPEC-EXAMPLE-001", "DCL-EXAMPLE-001", "DELIB-1234", "bridge/example.md", "PAUTH-1234"],
)
def test_stray_waiver_does_not_change_valid_metadata(identifier: str) -> None:
    original = validate_author_metadata(_metadata_content())
    result = validate_author_metadata(
        _metadata_content() + f"document_author_provenance_waiver: {identifier} - ignored\n"
    )

    assert result == original
    assert result.is_valid


def test_governed_document_surface_matching() -> None:
    config = DocumentAuthorConfig(
        governed_surfaces=(
            "bridge/**/*.md",
            ".harness-baseline-configuration/rules/**/*.md",
            "independent-progress-assessments/**/*.md",
        ),
        exclusions=(".claude/worktrees/**",),
    )

    assert is_governed_document_path("bridge/example-001.md", config)
    assert is_governed_document_path(".harness-baseline-configuration/rules/example.md", config)
    assert is_governed_document_path("independent-progress-assessments/example.md", config)
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
    assert ".harness-baseline-configuration/rules/**/*.md" in config.governed_surfaces
    assert "independent-progress-assessments/**/*.md" in config.governed_surfaces
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


def _codex_apply_patch_payload(path: str) -> dict[str, object]:
    """Codex's native apply_patch payload: the patch text is the tool's command (see
    test_codex_native_hook_adapter.py); the legacy wrapper's `patch` key is not what the adapter forwards."""
    return {
        "tool_name": "apply_patch",
        "cwd": str(PROJECT_ROOT),
        "tool_input": {"command": f"*** Begin Patch\n*** Add File: {path}\n+# Missing provenance\n*** End Patch\n"},
    }


def test_baseline_gate_blocks_codex_add_file_patch_without_metadata() -> None:
    """The neutral gate reads the patch from `tool_input.command`; before this it saw an apply_patch call, extracted
    no patch text and allowed the governed document (fail-open on the native Codex path)."""
    result = _run_hook(BASELINE_HOOK, _codex_apply_patch_payload("docs/new-codex-contract.md"))

    assert result.returncode == 2
    assert "docs/new-codex-contract.md" in json.loads(result.stdout)["reason"]


def test_codex_authored_gate_blocks_add_file_patch_without_metadata() -> None:
    result = _run_hook(CODEX_HOOK, _codex_apply_patch_payload("docs/new-codex-contract.md"))

    assert result.returncode == 2
    assert "docs/new-codex-contract.md" in json.loads(result.stdout)["reason"]


def test_codex_apply_patch_registration_present() -> None:
    """Codex registers the gate once for its file-write and shell-exec intents through the native adapter."""
    hooks = json.loads(CODEX_HOOKS_JSON.read_text(encoding="utf-8"))
    registrations = [
        entry
        for entry in hooks["hooks"]["PreToolUse"]
        if "apply_patch" in entry.get("matcher", "").split("|")
        for hook in entry.get("hooks", [])
        if "codex_hook_adapter.py" in hook.get("command", "")
        and ".harness-baseline-configuration/hooks/document_author_provenance_gate.py" in hook.get("command", "")
    ]

    assert len(registrations) == 1


def test_hook_allows_existing_file_edits_without_metadata(tmp_path: Path) -> None:
    existing = tmp_path / "docs" / "existing.md"
    existing.parent.mkdir()
    existing.write_text("# Existing grandfathered file\n", encoding="utf-8")
    payload = {
        "tool_name": "Write",
        "cwd": str(tmp_path),
        "tool_input": {"file_path": str(existing), "content": "# Still grandfathered\n"},
    }

    result = _run_hook(CLAUDE_HOOK, payload)

    assert result.returncode == 0
    assert json.loads(result.stdout) == {}


@pytest.mark.parametrize("with_metadata", [False, True])
@pytest.mark.parametrize(
    "surface", ["docs", "independent-progress-assessments", ".harness-baseline-configuration/rules"]
)
def test_checker_cli_applies_provenance_without_waivers(tmp_path: Path, with_metadata: bool, surface: str) -> None:
    document = tmp_path / surface / "new.md"
    document.parent.mkdir(parents=True)
    content = _metadata_content() if with_metadata else "# Missing metadata\n"
    document.write_text(content + "document_author_provenance_waiver: DELIB-1234 - ignored\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-B",
            str(PROJECT_ROOT / "scripts/check_document_author_metadata.py"),
            "--project-root",
            str(tmp_path),
            "--config",
            str(PROJECT_ROOT / "config/governance/document-author-provenance.toml"),
            "--json",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == (0 if with_metadata else 1), result.stderr
    report = json.loads(result.stdout)
    assert report["finding_count"] == (0 if with_metadata else 1)
    if not with_metadata:
        assert report["findings"][0]["path"] == f"{surface}/new.md"
        assert report["findings"][0]["missing_fields"] == list(REQUIRED_AUTHOR_FIELDS)


@pytest.mark.parametrize("with_metadata", [False, True])
def test_real_hook_ignores_document_waiver(tmp_path: Path, with_metadata: bool) -> None:
    content = _metadata_content() if with_metadata else "# Missing metadata\n"
    payload = {
        "tool_name": "Write",
        "cwd": str(tmp_path),
        "tool_input": {
            "file_path": "docs/new.md",
            "content": content + "document_author_provenance_waiver: DELIB-1234 - ignored\n",
        },
    }

    result = _run_hook(BASELINE_HOOK, payload)

    assert result.returncode == (0 if with_metadata else 2), result.stderr
    reply = json.loads(result.stdout)
    if with_metadata:
        assert reply == {}
    else:
        assert reply["decision"] == "block"
        assert "docs/new.md" in reply["reason"]
        assert "Use document_author_provenance_waiver" not in reply["reason"]
    assert not (tmp_path / "docs/new.md").exists()
