"""Tests for the harness-aware `changed_by` resolver.

Authority: bridge/gtkb-kb-attribution-harness-aware-003.md (Codex GO at -004).

Covers the three-source priority order (kwarg / env / single Prime),
fail-closed semantics for mutating callers, and the separate read-only
variant. Also asserts the 4 archive helpers no longer contain the literal
`prime-builder/claude-code` (Codex F1+F2 fix verification).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from unittest import mock

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
ARCHIVE_HELPERS = sorted(SCRIPTS_DIR.glob("_archive_delib_s32*.py"))

sys.path.insert(0, str(PROJECT_ROOT))

from scripts._kb_attribution import (  # noqa: E402
    ENV_VAR_HARNESS_NAME,
    resolve_changed_by,
    resolve_changed_by_or_none,
)


@pytest.fixture(autouse=True)
def mock_harness_state(tmp_path, monkeypatch):
    registry_file = tmp_path / "harness-registry.json"
    identities_file = tmp_path / "harness-identities.json"

    registry_file.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_of_truth": "MemBase harnesses table",
                "harnesses": [
                    {
                        "id": "A",
                        "harness_name": "codex",
                        "harness_type": "codex",
                        "role": ["loyal-opposition"],
                        "status": "active",
                    },
                    {
                        "id": "B",
                        "harness_name": "claude",
                        "harness_type": "claude",
                        "role": ["prime-builder"],
                        "status": "active",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    identities_file.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_of_truth": "GT-KB harness installation identities",
                "harnesses": {
                    "claude": {"id": "B"},
                    "codex": {"id": "A"},
                    "antigravity": {"id": "C"},
                    "ollama": {"id": "D"},
                    "goose": {"id": "E"},
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("GTKB_HARNESS_REGISTRY_PATH", str(registry_file))
    monkeypatch.setenv("GTKB_HARNESS_IDENTITIES_PATH", str(identities_file))


def test_explicit_kwarg_resolves_codex() -> None:
    """Priority 1: explicit kwarg `harness_name` takes precedence."""
    result = resolve_changed_by(harness_name="codex")
    assert result == "loyal-opposition/codex"


def test_explicit_kwarg_resolves_claude() -> None:
    """Priority 1: explicit kwarg works for either harness."""
    result = resolve_changed_by(harness_name="claude")
    assert result == "prime-builder/claude"


def test_env_var_resolves_when_no_kwarg() -> None:
    """Priority 2: GTKB_HARNESS_NAME env var is consulted when kwarg is None."""
    with mock.patch.dict("os.environ", {ENV_VAR_HARNESS_NAME: "codex"}):
        assert resolve_changed_by() == "loyal-opposition/codex"


def test_kwarg_precedes_env_var() -> None:
    """Priority 1 beats priority 2: explicit kwarg overrides env var."""
    with mock.patch.dict("os.environ", {ENV_VAR_HARNESS_NAME: "codex"}):
        assert resolve_changed_by(harness_name="claude") == "prime-builder/claude"


def test_single_prime_fallback_resolves_to_claude() -> None:
    """Priority 3: with kwarg=None and no env var, the sole Prime Builder is used.

    Current role state: claude = prime-builder, codex = loyal-opposition.
    Sole Prime Builder is claude.
    """
    # Ensure env var is unset for this test, preserving others like registry paths
    with mock.patch.dict("os.environ", {}):
        os.environ.pop(ENV_VAR_HARNESS_NAME, None)
        assert resolve_changed_by() == "prime-builder/claude"


def test_unresolvable_harness_raises() -> None:
    """Priority 1 with unknown harness_name raises (no fallback)."""
    with pytest.raises(RuntimeError, match="no entry in"):
        resolve_changed_by(harness_name="nonexistent-harness-xyz")


def test_or_none_returns_none_for_unresolvable() -> None:
    """Read-only variant returns None where the mutating variant raises."""
    assert resolve_changed_by_or_none(harness_name="nonexistent-harness-xyz") is None


def test_or_none_returns_value_when_resolvable() -> None:
    """Read-only variant returns the same string when resolvable."""
    assert resolve_changed_by_or_none(harness_name="claude") == "prime-builder/claude"


def test_no_prime_builder_unknown_fallback() -> None:
    """Resolver never returns 'prime-builder/unknown' (Codex F2 fix).

    Mutating callers must fail closed; there is no documented-default
    fallback that masks unresolved attribution.
    """
    # Probe many code paths and confirm no 'unknown' string ever returned
    for name in ("claude", "codex"):
        result = resolve_changed_by(harness_name=name)
        assert "unknown" not in result.lower()
    for name in ("nonexistent", None):
        try:
            result = resolve_changed_by(harness_name=name)
            assert "unknown" not in result.lower()
        except RuntimeError:
            pass  # Expected fail-closed


# Archive-helper greppable-absence tests (GO Implementation Condition 2)


@pytest.mark.parametrize("helper_path", ARCHIVE_HELPERS, ids=lambda p: p.name)
def test_archive_helpers_no_longer_hardcode_claude_code(helper_path: Path) -> None:
    """Each archive helper must not contain literal `prime-builder/claude-code`.

    Codex GO Implementation Condition 2: greppable absence required.
    """
    text = helper_path.read_text(encoding="utf-8")
    assert "prime-builder/claude-code" not in text, (
        f"{helper_path.name} still contains the hardcoded "
        f"'prime-builder/claude-code' literal; should call resolve_changed_by()"
    )


@pytest.mark.parametrize("helper_path", ARCHIVE_HELPERS, ids=lambda p: p.name)
def test_archive_helpers_call_resolve_changed_by(helper_path: Path) -> None:
    """Each archive helper must call resolve_changed_by() for `changed_by` arg."""
    text = helper_path.read_text(encoding="utf-8")
    assert "resolve_changed_by" in text
    assert "changed_by=resolve_changed_by(" in text


@pytest.mark.parametrize("helper_path", ARCHIVE_HELPERS, ids=lambda p: p.name)
def test_archive_helpers_do_not_use_or_none_variant(helper_path: Path) -> None:
    """Mutating helpers MUST NOT call resolve_changed_by_or_none() (GO Condition 1)."""
    text = helper_path.read_text(encoding="utf-8")
    assert "resolve_changed_by_or_none" not in text, (
        f"{helper_path.name} mutating helper must not use the read-only-test "
        f"variant; use resolve_changed_by() which fails closed"
    )


# ──────────────────────────────────────────────────────────────────────────
# Slice 2: active Prime Builder attribution (ADR-ROLE-STATUS-ORTHOGONALITY-001
# Consequences §1; DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001).
# bridge/gtkb-role-status-orthogonality-dispatch-slice-2-resolver (GO at -002).
#
# Priority-3 attribution resolves to the single ACTIVE Prime Builder. The
# active-status filter is applied upstream by load_role_assignments (it returns
# only status=="active" harnesses), so an inactive same-role harness is filtered
# out. These tests redirect the registry projection read via the
# GTKB_HARNESS_REGISTRY_PATH env override so they never read live state.
# ──────────────────────────────────────────────────────────────────────────


def _write_attribution_registry(path: Path, harnesses: list[dict]) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_of_truth": "MemBase harnesses table (groundtruth.db)",
                "harnesses": harnesses,
            }
        ),
        encoding="utf-8",
    )


def test_active_prime_builder_attribution_filters_inactive(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Priority-3 attribution resolves to the single ACTIVE Prime Builder.

    claude (B) is active prime-builder; antigravity (C) is INACTIVE prime-builder.
    load_role_assignments filters C out, so the priority-3 fallback resolves to
    the single active PB (claude) and does NOT raise on 'two prime builders'.
    Pins ADR-ROLE-STATUS-ORTHOGONALITY-001 Consequences §1.
    """
    registry = tmp_path / "harness-registry.json"
    _write_attribution_registry(
        registry,
        [
            {
                "id": "B",
                "harness_name": "claude",
                "harness_type": "claude",
                "status": "active",
                "role": ["prime-builder"],
            },
            {
                "id": "C",
                "harness_name": "antigravity",
                "harness_type": "antigravity",
                "status": "inactive",
                "role": ["prime-builder"],
            },
            {
                "id": "A",
                "harness_name": "codex",
                "harness_type": "codex",
                "status": "active",
                "role": ["loyal-opposition"],
            },
        ],
    )
    monkeypatch.setenv("GTKB_HARNESS_REGISTRY_PATH", str(registry))
    monkeypatch.delenv(ENV_VAR_HARNESS_NAME, raising=False)
    assert resolve_changed_by() == "prime-builder/claude"


def test_two_active_prime_builders_fail_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Two ACTIVE Prime Builders is a registry misconfiguration: priority-3
    resolution returns None and the mutating resolver fails closed (RuntimeError).
    """
    registry = tmp_path / "harness-registry.json"
    _write_attribution_registry(
        registry,
        [
            {
                "id": "B",
                "harness_name": "claude",
                "harness_type": "claude",
                "status": "active",
                "role": ["prime-builder"],
            },
            {
                "id": "C",
                "harness_name": "antigravity",
                "harness_type": "antigravity",
                "status": "active",
                "role": ["prime-builder"],
            },
        ],
    )
    monkeypatch.setenv("GTKB_HARNESS_REGISTRY_PATH", str(registry))
    monkeypatch.delenv(ENV_VAR_HARNESS_NAME, raising=False)
    with pytest.raises(RuntimeError):
        resolve_changed_by()
