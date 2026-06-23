# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Structural and parity tests for the dispatcher-control skill.

Verifies SPEC-DISPATCHER-CONTROL-SURFACE-001 acceptance criterion 5 and
DCL-DISPATCHER-CONFIG-CLI-ONLY-001: the skill must surface governed dispatcher
reporting/configuration commands and route operators away from direct
``config/dispatcher/rules.toml`` edits.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CLAUDE_SKILL = _REPO_ROOT / ".claude" / "skills" / "dispatcher-control" / "SKILL.md"
_CODEX_ADAPTER = _REPO_ROOT / ".codex" / "skills" / "dispatcher-control" / "SKILL.md"
_ANTIGRAVITY_ADAPTER = _REPO_ROOT / ".agent" / "skills" / "dispatcher-control" / "SKILL.md"
_REGISTRY = _REPO_ROOT / "config" / "agent-control" / "harness-capability-registry.toml"

_REPORTING_COMMANDS = (
    "gt bridge dispatch report --json",
    "gt bridge dispatch status --json",
    "gt bridge dispatch health --json",
    "gt bridge dispatch config --json",
)

_TRANSACTION_COMMANDS = (
    "gt bridge dispatch config set-eligibility",
    "gt bridge dispatch config set-weights",
    "gt bridge dispatch config set-caps",
    "gt bridge dispatch config set-rule",
    "gt bridge dispatch config add-harness",
    "gt bridge dispatch config remove-harness",
)


def _split_frontmatter(text: str) -> tuple[str, str]:
    assert text.startswith("---"), "SKILL.md must open with YAML frontmatter"
    parts = text.split("---", 2)
    assert len(parts) == 3, "SKILL.md frontmatter block must be closed"
    return parts[1], parts[2]


def _frontmatter_value(frontmatter: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", frontmatter, re.MULTILINE)
    assert match, f"frontmatter is missing {key!r}"
    return match.group(1).strip()


def _registry_capability(cap_id: str) -> dict:
    data = tomllib.loads(_REGISTRY.read_text(encoding="utf-8"))
    for cap in data.get("capabilities", []):
        if cap.get("id") == cap_id:
            return cap
    raise AssertionError(f"registry has no capability {cap_id!r}")


def test_skill_file_exists_with_trigger_frontmatter() -> None:
    """Verifies SPEC-DISPATCHER-CONTROL-SURFACE-001: skill wrapper exists."""
    assert _CLAUDE_SKILL.is_file(), f"missing skill file: {_CLAUDE_SKILL}"
    frontmatter, body = _split_frontmatter(_CLAUDE_SKILL.read_text(encoding="utf-8"))
    assert _frontmatter_value(frontmatter, "name") == "dispatcher-control"
    description = _frontmatter_value(frontmatter, "description").lower()
    for phrase in ("gt bridge dispatch", "report", "config/dispatcher/rules.toml"):
        assert phrase in description
    assert body.strip(), "skill body must not be empty"


def test_skill_surfaces_reporting_and_config_commands() -> None:
    """Verifies SPEC-DISPATCHER-CONTROL-SURFACE-001 acceptance criterion 5."""
    text = _CLAUDE_SKILL.read_text(encoding="utf-8")
    for command in _REPORTING_COMMANDS + _TRANSACTION_COMMANDS:
        assert command in text, f"skill must mention {command!r}"


def test_skill_blocks_direct_file_edit_path() -> None:
    """Verifies DCL-DISPATCHER-CONFIG-CLI-ONLY-001 direct-edit prohibition."""
    text = _CLAUDE_SKILL.read_text(encoding="utf-8").lower()
    assert "do not directly edit `config/dispatcher/rules.toml`" in text
    assert "do not mutate dispatcher runtime json by hand" in text
    assert "gt harness suspend" in text
    assert "dispatcher eligibility" in text


def test_generated_adapters_exist_and_mirror_core_contract() -> None:
    """Verifies cross-harness skill parity for Codex and Antigravity."""
    for adapter in (_CODEX_ADAPTER, _ANTIGRAVITY_ADAPTER):
        assert adapter.is_file(), f"missing generated adapter: {adapter}"
        text = adapter.read_text(encoding="utf-8")
        frontmatter, _ = _split_frontmatter(text)
        assert _frontmatter_value(frontmatter, "name") == "dispatcher-control"
        for command in _REPORTING_COMMANDS + _TRANSACTION_COMMANDS:
            assert command in text, f"{adapter} is missing {command!r}"
        assert "config/dispatcher/rules.toml" in text


def test_registry_declares_all_harness_surfaces() -> None:
    """Verifies dispatcher-control is registered as a cross-harness skill."""
    cap = _registry_capability("skill.dispatcher-control")
    assert cap["kind"] == "skill"
    assert cap["canonical_name"] == "dispatcher-control"
    assert "prime-builder" in cap["required_for_roles"]
    assert "loyal-opposition" in cap["required_for_roles"]
    assert cap["claude"]["surface"] == ".claude/skills/dispatcher-control/SKILL.md"
    assert cap["claude"]["status"] == "native"
    assert cap["codex"]["surface"] == ".codex/skills/dispatcher-control/SKILL.md"
    assert cap["codex"]["status"] == "adapter"
    assert cap["codex"]["adapter_source"] == ".claude/skills/dispatcher-control/SKILL.md"
    assert cap["antigravity"]["surface"] == ".agent/skills/dispatcher-control/SKILL.md"
    assert cap["antigravity"]["status"] == "adapter"
    assert cap["antigravity"]["adapter_source"] == ".claude/skills/dispatcher-control/SKILL.md"
