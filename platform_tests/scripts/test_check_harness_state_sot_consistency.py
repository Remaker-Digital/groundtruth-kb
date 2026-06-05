"""Platform-tests integration check for the harness-state SoT doctor surface.

Per WI-4327 / WI-4329 Phase-1 Foundation proposal §Summary: platform-tests
check the ``_check_harness_state_sot_consistency`` doctor surface end-to-end
against the live project. This sits at the platform_tests layer rather than
groundtruth-kb/tests/ so it exercises the live project root that the doctor
would inspect during ``gt project doctor``.

These tests are deliberately gentle: they verify the doctor surface returns
a ``ToolCheck`` object, that the 3-layer scan runs to completion without
crashing, and that the severity is one of the documented values. The
substantive layer-specific assertions live in
``groundtruth-kb/tests/test_doctor_harness_state_sot.py`` against
synthetic fixtures.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def doctor_module() -> object:
    """Import the doctor module against the live repo root."""
    from groundtruth_kb.project import doctor  # noqa: PLC0415

    return doctor


def test_check_surface_returns_tool_check(doctor_module: object) -> None:
    """Doctor surface returns a ``ToolCheck`` (does not raise)."""
    check_fn = doctor_module._check_harness_state_sot_consistency  # type: ignore[attr-defined]
    result = check_fn(_REPO_ROOT)
    assert isinstance(result, doctor_module.ToolCheck)  # type: ignore[attr-defined]
    assert result.name == "harness-state SoT consistency"
    assert result.required is False  # WARN-only initial severity per proposal §AC #8


def test_check_severity_is_valid(doctor_module: object) -> None:
    """Severity is ``pass`` (clean) or ``warning`` (any L1/L2/L3 finding).

    ``fail`` is reserved for after WI-4336 (mirror retirement) lands per
    proposal §AC #8.
    """
    check_fn = doctor_module._check_harness_state_sot_consistency  # type: ignore[attr-defined]
    result = check_fn(_REPO_ROOT)
    assert result.status in {"pass", "warning"}


def test_check_message_contains_layer_token_when_warning(doctor_module: object) -> None:
    """A warning result must name at least one layer in its message."""
    check_fn = doctor_module._check_harness_state_sot_consistency  # type: ignore[attr-defined]
    result = check_fn(_REPO_ROOT)
    if result.status != "warning":
        pytest.skip("Live project surface is clean; layer-token assertion not applicable")
    assert any(token in result.message for token in ("L1", "L2", "L3"))


def test_doctor_check_does_not_mutate_filesystem(doctor_module: object, tmp_path: Path) -> None:
    """The doctor check is read-only — invoking it MUST NOT write under target."""
    check_fn = doctor_module._check_harness_state_sot_consistency  # type: ignore[attr-defined]
    sentinel = tmp_path / "sentinel.txt"
    sentinel.write_text("pre-check sentinel", encoding="utf-8")
    pre_listing = sorted(p.name for p in tmp_path.iterdir())
    pre_sentinel = sentinel.read_text(encoding="utf-8")
    _ = check_fn(tmp_path)
    post_listing = sorted(p.name for p in tmp_path.iterdir())
    post_sentinel = sentinel.read_text(encoding="utf-8")
    assert post_listing == pre_listing
    assert post_sentinel == pre_sentinel
