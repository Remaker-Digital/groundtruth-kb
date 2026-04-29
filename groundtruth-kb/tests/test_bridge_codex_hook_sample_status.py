# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the Codex SessionStart hook sample.

Per ``bridge/gtkb-bridge-poller-p2-registry-implementation-2026-04-28-003.md``
section 1.2.3, the Codex hook sample must:
1. Parse as valid JSON.
2. Contain a top-level ``_verification_warning`` referencing
   ADR-CODEX-HOOK-PARITY-FALLBACK-001.
3. Use the canonical registry CLI command path
   ``python -m groundtruth_kb.bridge.registry register --harness-kind codex``.

Companion Claude sample is also verified for parse validity and command path.
Bridge imports are lazy per tests/test_bridge_import_hygiene rule (this file
is not test_bridge_*; the rule does not apply, but no bridge imports are
needed anyway — the tests parse JSON only).
"""

from __future__ import annotations

import json
from pathlib import Path

_SAMPLES_DIR = Path(__file__).resolve().parents[1] / "samples"


# NOTE: Sample subdirs are named `dot-claude` / `dot-codex` instead of
# `.claude` / `.codex` because the latter are gitignored at the repo root.
# Adopters rename `dot-claude` -> `.claude` (etc.) at copy time.
_CODEX_SAMPLE_REL = "codex/dot-codex/hooks-bridge-poller.json"
_CLAUDE_SAMPLE_REL = "claude/dot-claude/settings-bridge-poller.json"


def _load_sample(rel_path: str) -> dict:
    sample = _SAMPLES_DIR / rel_path
    assert sample.is_file(), f"Expected sample at {sample}"
    return json.loads(sample.read_text(encoding="utf-8"))


def test_codex_hook_sample_is_valid_json() -> None:
    payload = _load_sample(_CODEX_SAMPLE_REL)
    assert isinstance(payload, dict)


def test_codex_hook_sample_carries_verification_warning() -> None:
    payload = _load_sample(_CODEX_SAMPLE_REL)
    assert "_verification_warning" in payload
    warning = payload["_verification_warning"]
    assert isinstance(warning, str)
    assert "ADR-CODEX-HOOK-PARITY-FALLBACK-001" in warning


def test_codex_hook_sample_command_uses_registry_module() -> None:
    payload = _load_sample(_CODEX_SAMPLE_REL)
    cmd = payload["hooks"]["SessionStart"][0]["command"]
    assert "python -m groundtruth_kb.bridge.registry register" in cmd
    assert "--harness-kind codex" in cmd


def test_claude_hook_sample_is_valid_json() -> None:
    payload = _load_sample(_CLAUDE_SAMPLE_REL)
    assert isinstance(payload, dict)


def test_claude_hook_sample_command_uses_registry_module() -> None:
    payload = _load_sample(_CLAUDE_SAMPLE_REL)
    cmd = payload["hooks"]["SessionStart"][0]["command"]
    assert "python -m groundtruth_kb.bridge.registry register" in cmd
    assert "--harness-kind claude-code" in cmd
