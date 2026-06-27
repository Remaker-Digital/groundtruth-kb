"""Tests for the bridge-compliance-gate ``## Cross-Harness Disposition`` gate
(WI-4883, Slice 4 of PROJECT-GTKB-CROSS-HARNESS-PARITY).

Realizes ``DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`` assertion
**PARITY-DISPOSITION-GATE** (ADR-CROSS-HARNESS-PARITY-001 Q8): an implementation
proposal whose ``target_paths`` touch a harness-surface file must include a
non-empty ``## Cross-Harness Disposition`` section. The Write-time gate hard-blocks
the omission; Loyal Opposition NO-GO is the second-line backstop.

Contract carried forward from the GO at
``bridge/gtkb-cross-harness-parity-slice-4-disposition-gate-002.md``:

1. The gate triggers ONLY for NEW/REVISED implementation proposals whose
   target_paths touch a harness-surface marker; off-surface proposals are
   unaffected.
2. Verdict files (GO/NO-GO/VERIFIED first line) are excluded.
3. Placeholder-only / bullet-only sections (``n/a``, bare ``-``, blank bullet)
   do not satisfy the requirement (LO residual-risk #2).
4. The active hook and the activation template must be byte-identical; the
   parametrized ``gate`` fixture exercises BOTH and
   ``test_template_and_active_hook_byte_identical`` asserts parity.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LIVE_HOOK = REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"
TEMPLATE_HOOK = REPO_ROOT / "groundtruth-kb" / "templates" / "hooks" / "bridge-compliance-gate.py"

_DISPOSITION_MARKER = "Cross-Harness Disposition"

_AUTHOR_METADATA = (
    "author_identity: Codex\n"
    "author_harness_id: A\n"
    "author_session_context_id: test-session\n"
    "author_model: GPT-5\n"
    "author_model_version: GPT-5\n"
    "author_model_configuration: test\n"
)
_PROJECT_METADATA = "Project Authorization: PAUTH-TEST-PROJECT-X\nProject: PROJECT-TEST-X\nWork Item: WI-9999\n"
_SPEC_LINKS = "## Specification Links\n\n- GOV-FILE-BRIDGE-AUTHORITY-001\n"
_REQ_SUFF = "## Requirement Sufficiency\n\nExisting requirements sufficient. Rationale prose here.\n"

_HARNESS_SURFACE_TARGET = 'target_paths: [".claude/hooks/bridge-compliance-gate.py"]\n'
_OFF_SURFACE_TARGET = 'target_paths: ["scripts/example.py"]\n'

_CONCRETE_DISPOSITION = (
    "## Cross-Harness Disposition\n\n"
    "- Universal applicability; behaves identically on claude and codex via the "
    "canonical Python hook. No per-harness divergence; no waiver required.\n"
)
_PLACEHOLDER_DISPOSITION = "## Cross-Harness Disposition\n\nn/a\n"
_BULLET_ONLY_DISPOSITION = "## Cross-Harness Disposition\n\n-\n"
_BLANK_BULLET_DISPOSITION = "## Cross-Harness Disposition\n\n*\n"


def _load_gate(path: Path, module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(params=["live", "template"])
def gate(request: pytest.FixtureRequest) -> ModuleType:
    if request.param == "live":
        return _load_gate(LIVE_HOOK, "bcg_disposition_live")
    return _load_gate(TEMPLATE_HOOK, "bcg_disposition_template")


def _proposal(
    *,
    status: str = "NEW",
    bridge_kind: str = "prime_proposal",
    target_paths: str | None = _HARNESS_SURFACE_TARGET,
    disposition: str | None = _CONCRETE_DISPOSITION,
) -> str:
    parts = [status, "", "# Test Proposal", "", _AUTHOR_METADATA, f"bridge_kind: {bridge_kind}", "", _PROJECT_METADATA]
    if target_paths is not None:
        parts.append(target_paths)
    parts.append(_SPEC_LINKS)
    parts.append("")
    parts.append(_REQ_SUFF)
    if disposition is not None:
        parts.append("")
        parts.append(disposition)
    return "\n".join(parts)


def _deny(gate: ModuleType, content: str, cwd: Path) -> str | None:
    return gate._deny_reason_for_content(
        cwd_path=cwd,
        file_path="bridge/test-disposition-001.md",
        content=content,
        run_pending_preflight=False,
    )


# --- Acceptance: deny cases ----------------------------------------------------


def test_harness_surface_without_disposition_denied(gate: ModuleType, tmp_path: Path) -> None:
    reason = _deny(gate, _proposal(disposition=None), tmp_path)
    assert reason is not None
    assert _DISPOSITION_MARKER in reason
    assert "PARITY-DISPOSITION-GATE" in reason


def test_placeholder_disposition_denied(gate: ModuleType, tmp_path: Path) -> None:
    reason = _deny(gate, _proposal(disposition=_PLACEHOLDER_DISPOSITION), tmp_path)
    assert reason is not None and _DISPOSITION_MARKER in reason


def test_bullet_only_disposition_denied(gate: ModuleType, tmp_path: Path) -> None:
    reason = _deny(gate, _proposal(disposition=_BULLET_ONLY_DISPOSITION), tmp_path)
    assert reason is not None and _DISPOSITION_MARKER in reason


def test_blank_bullet_disposition_denied(gate: ModuleType, tmp_path: Path) -> None:
    reason = _deny(gate, _proposal(disposition=_BLANK_BULLET_DISPOSITION), tmp_path)
    assert reason is not None and _DISPOSITION_MARKER in reason


# --- Acceptance: pass cases ----------------------------------------------------


def test_harness_surface_with_concrete_disposition_passes(gate: ModuleType, tmp_path: Path) -> None:
    reason = _deny(gate, _proposal(disposition=_CONCRETE_DISPOSITION), tmp_path)
    assert reason is None


def test_off_surface_without_disposition_not_triggered(gate: ModuleType, tmp_path: Path) -> None:
    reason = _deny(gate, _proposal(target_paths=_OFF_SURFACE_TARGET, disposition=None), tmp_path)
    assert reason is None


def test_verdict_file_touching_surface_excluded(gate: ModuleType, tmp_path: Path) -> None:
    # A GO-first-line body routes down the verdict branch and never reaches the
    # NEW/REVISED disposition clause; whatever else the verdict path may flag,
    # it must NOT be the Cross-Harness Disposition gate.
    go_body = "GO\n\n" + _AUTHOR_METADATA + "bridge_kind: proposal_review\n" + _HARNESS_SURFACE_TARGET
    reason = _deny(gate, go_body, tmp_path)
    assert reason is None or _DISPOSITION_MARKER not in reason


# --- Predicate unit coverage ---------------------------------------------------


@pytest.mark.parametrize(
    "target_line,expected",
    [
        ('target_paths: [".claude/hooks/bridge-compliance-gate.py"]', True),
        ('target_paths: [".codex/gtkb-hooks/foo.py"]', True),
        ('target_paths: [".claude/settings.json"]', True),
        ('target_paths: [".codex/hooks.json"]', True),
        ('target_paths: [".claude/skills/verify/SKILL.md"]', True),
        ('target_paths: ["scripts/example.py", "groundtruth-kb/src/foo.py"]', False),
        ('target_paths: ["docs/readme.md"]', False),
    ],
)
def test_target_paths_touch_harness_surface_predicate(gate: ModuleType, target_line: str, expected: bool) -> None:
    assert gate._target_paths_touch_harness_surface(target_line) is expected


@pytest.mark.parametrize(
    "section,expected",
    [
        (_CONCRETE_DISPOSITION, True),
        (_PLACEHOLDER_DISPOSITION, False),
        (_BULLET_ONLY_DISPOSITION, False),
        (_BLANK_BULLET_DISPOSITION, False),
        ("", False),
    ],
)
def test_has_concrete_cross_harness_disposition_section(gate: ModuleType, section: str, expected: bool) -> None:
    assert gate._has_concrete_cross_harness_disposition_section(section) is expected


# --- Template parity -----------------------------------------------------------


def test_template_and_active_hook_byte_identical() -> None:
    assert LIVE_HOOK.read_bytes() == TEMPLATE_HOOK.read_bytes()
