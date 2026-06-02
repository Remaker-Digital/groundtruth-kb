"""Slice 1 regression tests for the GT-KB MCP surface foundation.

Covers authority schema, boundary enforcement, role-awareness, the
``gt_status_summary`` proof-of-pattern tool, and server-scaffold importability.
Traces to ``bridge/gtkb-mcp-stable-harness-surface-conversion-003.md`` IP-3
(T1-T10).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from groundtruth_kb.mcp_surface.authority import (
    ALL_LABELS,
    AuthorityLabel,
    build_envelope,
)
from groundtruth_kb.mcp_surface.boundary import (
    MCPBoundaryError,
    assert_in_root,
    resolve_safe_path,
)
from groundtruth_kb.mcp_surface.roles import CANONICAL_ROLES, current_role

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# T1 - authority enum schema
# ---------------------------------------------------------------------------


def test_t1_authority_enum_has_six_canonical_labels() -> None:
    expected = {
        "authoritative",
        "generated-summary",
        "advisory",
        "allowed",
        "denied",
        "owner-approval-required",
    }
    assert {label.value for label in AuthorityLabel} == expected
    assert len(ALL_LABELS) == 6
    envelope = build_envelope(
        authority=AuthorityLabel.GENERATED_SUMMARY,
        payload={"hello": "world"},
        source_ref="test://t1",
    )
    assert set(envelope.keys()) == {"authority", "payload", "source_ref", "generated_at"}
    assert envelope["authority"] == "generated-summary"
    assert envelope["payload"] == {"hello": "world"}
    assert envelope["generated_at"].endswith("Z")
    assert json.dumps(envelope)  # round-trips JSON cleanly


# ---------------------------------------------------------------------------
# T2 - in-root paths accepted
# ---------------------------------------------------------------------------


def test_t2_assert_in_root_accepts_in_root_paths() -> None:
    in_root = PROJECT_ROOT / "bridge" / "INDEX.md"
    assert assert_in_root(in_root, root=PROJECT_ROOT) == in_root.resolve()


# ---------------------------------------------------------------------------
# T3 - out-of-root paths rejected
# ---------------------------------------------------------------------------


def test_t3_assert_in_root_rejects_out_of_root_paths() -> None:
    outside = PROJECT_ROOT.parent / "GT-KB-outside-boundary-test-sentinel.txt"
    with pytest.raises(MCPBoundaryError):
        assert_in_root(outside, root=PROJECT_ROOT)


# ---------------------------------------------------------------------------
# T4 - traversal attempts rejected
# ---------------------------------------------------------------------------


def test_t4_assert_in_root_rejects_traversal_attempts() -> None:
    traversal = PROJECT_ROOT / ".." / ".." / "Windows" / "System32"
    with pytest.raises(MCPBoundaryError):
        assert_in_root(traversal, root=PROJECT_ROOT)


# ---------------------------------------------------------------------------
# T5 - relative paths resolved to absolute under root
# ---------------------------------------------------------------------------


def test_t5_resolve_safe_path_resolves_relative_to_root() -> None:
    resolved = resolve_safe_path("bridge/INDEX.md", root=PROJECT_ROOT)
    assert resolved.is_absolute()
    assert resolved == (PROJECT_ROOT / "bridge" / "INDEX.md").resolve()


# ---------------------------------------------------------------------------
# T6 - role resolved from the registry projection
# ---------------------------------------------------------------------------


def test_t6_current_role_reads_role_assignments_json(tmp_path: Path) -> None:
    """WI-3342 IP-4: ``current_role`` resolves the operating role from the
    DB-backed registry projection ``harness-state/harness-registry.json``,
    whose ``harnesses`` field is a LIST of unified records (migrated from the
    retired ``harness-state/role-assignments.json``). The projection ``role``
    field is the list-valued role-set wire form; ``current_role`` collapses a
    singleton role-set to its sole canonical scalar role token (WI-3342 C1).
    Seeded under an isolated ``tmp_path`` so the test never reads the real
    harness-state.
    """
    registry = tmp_path / "harness-registry.json"
    harnesses = [
        {"id": "A", "harness_name": "codex", "role": ["loyal-opposition"]},
        {"id": "B", "harness_name": "claude", "role": ["prime-builder"]},
    ]
    registry.write_text(json.dumps({"harnesses": harnesses}), encoding="utf-8")
    for entry in harnesses:
        # current_role collapses the singleton role-set wire form to its sole
        # scalar token -- a canonical role, not the str() of the list (the
        # latter was the NO-GO -009 F1 defect, closed by WI-3342 C1).
        resolved = current_role(harness_id=entry["id"], role_map_path=registry)
        assert resolved == entry["role"][0]
        assert resolved in CANONICAL_ROLES


# ---------------------------------------------------------------------------
# T6b - multi-element single-harness role-set normalized to primary role
# ---------------------------------------------------------------------------


def test_t6b_current_role_normalizes_multi_role_single_harness_set(
    tmp_path: Path,
) -> None:
    """WI-3342 C1: in single-harness operating mode (per
    ``ADR-SINGLE-HARNESS-OPERATING-MODE-001``) a single harness id holds the
    multi-element role-set ``["prime-builder", "loyal-opposition"]``.
    ``current_role`` collapses that role-set to the deterministic primary role
    -- ``prime-builder`` -- so the MCP scalar status surface always reports a
    canonical role token. Seeded under an isolated ``tmp_path``.
    """
    registry = tmp_path / "harness-registry.json"
    registry.write_text(
        json.dumps(
            {
                "harnesses": [
                    {
                        "id": "B",
                        "harness_name": "claude",
                        "role": ["prime-builder", "loyal-opposition"],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    resolved = current_role(harness_id="B", role_map_path=registry)
    assert resolved == "prime-builder"
    assert resolved in CANONICAL_ROLES


# ---------------------------------------------------------------------------
# T7 - acting-prime-builder READ-accepted (compatibility)
# ---------------------------------------------------------------------------


def test_t7_current_role_accepts_acting_prime_builder_on_read(tmp_path: Path) -> None:
    # WI-3342 IP-4: ``current_role`` reads the registry projection LIST. The
    # legacy scalar role wire form is still READ-accepted per the Acting-Prime
    # Compatibility Contract.
    registry = tmp_path / "harness-registry.json"
    registry.write_text(
        json.dumps(
            {
                "harnesses": [
                    {"id": "Z", "harness_name": "claude", "role": "acting-prime-builder"},
                ]
            }
        ),
        encoding="utf-8",
    )
    assert current_role(harness_id="Z", role_map_path=registry) == "acting-prime-builder"


# ---------------------------------------------------------------------------
# T8 - gt_status_summary returns generated-summary envelope
# ---------------------------------------------------------------------------


def test_t8_gt_status_summary_returns_generated_summary_envelope() -> None:
    from groundtruth_kb.mcp_surface.server import build_status_summary_envelope

    envelope = build_status_summary_envelope(PROJECT_ROOT)
    assert envelope["authority"] == "generated-summary"
    assert envelope["source_ref"] == "bridge/INDEX.md+groundtruth.db"
    assert envelope["generated_at"].endswith("Z")


# ---------------------------------------------------------------------------
# T9 - payload includes expected shape
# ---------------------------------------------------------------------------


def test_t9_gt_status_summary_payload_includes_expected_fields() -> None:
    from groundtruth_kb.mcp_surface.server import gt_status_summary_payload

    payload = gt_status_summary_payload(PROJECT_ROOT)
    assert set(payload.keys()) == {
        "bridge_status_counts",
        "membase_row_counts",
        "project_root",
        "working_tree_clean",
        "current_role",
    }
    assert isinstance(payload["bridge_status_counts"], dict)
    # Live INDEX.md guarantees at least one status is present.
    assert sum(payload["bridge_status_counts"].values()) > 0
    assert isinstance(payload["membase_row_counts"], dict)
    # MemBase row counts MUST come from the current_* views, not the
    # append-only base tables, per bridge gtkb-mcp-stable-harness-surface-
    # conversion REVISED-N (Codex NO-GO at -006 F1).
    assert set(payload["membase_row_counts"].keys()) == {
        "current_work_items",
        "current_specifications",
        "current_deliberations",
    }
    assert payload["project_root"] == str(PROJECT_ROOT)
    assert payload["working_tree_clean"] in (True, False, None)
    assert isinstance(payload["current_role"], str)


# ---------------------------------------------------------------------------
# T11 - membase counts query current views, not base tables (F1 closure)
# ---------------------------------------------------------------------------


def test_t11_membase_row_counts_use_current_views_not_base_tables() -> None:
    """Regression for Codex NO-GO at
    ``bridge/gtkb-mcp-stable-harness-surface-conversion-006.md`` F1.

    The summary surface MUST report current-state counts. The
    append-only base tables overstate workflow state by counting
    historical versions. On a live DB where the two diverge, the payload
    value must equal the current-view count, not the base-table count.
    """
    import sqlite3

    from groundtruth_kb.mcp_surface.server import gt_status_summary_payload

    db_path = PROJECT_ROOT / "groundtruth.db"
    if not db_path.is_file():
        pytest.skip("groundtruth.db not present in test environment")

    connection = sqlite3.connect(db_path)
    try:
        base_count_row = connection.execute("SELECT count(*) FROM work_items").fetchone()
        current_count_row = connection.execute("SELECT count(*) FROM current_work_items").fetchone()
    finally:
        connection.close()

    base_count = int(base_count_row[0]) if base_count_row else 0
    current_count = int(current_count_row[0]) if current_count_row else 0

    payload = gt_status_summary_payload(PROJECT_ROOT)
    payload_value = payload["membase_row_counts"]["current_work_items"]

    assert payload_value == current_count, (
        f"membase_row_counts['current_work_items']={payload_value} must equal "
        f"SELECT count(*) FROM current_work_items={current_count} "
        f"(base table count is {base_count}; divergence indicates the "
        f"implementation regressed to base-table counting)."
    )
    # Sanity check that the test would actually fail if base-table counts
    # were used in production (only meaningful when the live DB has
    # multi-version rows).
    if base_count != current_count:
        assert payload_value != base_count, (
            "payload value matches base-table count; implementation appears "
            "to be using append-only tables instead of current_* views."
        )


# ---------------------------------------------------------------------------
# T12 - default harness id resolves via env-detection + identities map
#       (F2 closure: no hardcoded 'B' fallback)
# ---------------------------------------------------------------------------


def test_t12_default_harness_id_does_not_hardcode_claude(monkeypatch: pytest.MonkeyPatch) -> None:
    """Regression for Codex NO-GO at
    ``bridge/gtkb-mcp-stable-harness-surface-conversion-006.md`` F2.

    With no harness-detection env vars and no explicit ``GTKB_HARNESS_ID``,
    ``_default_harness_id()`` must fail-closed (return empty string) so
    ``current_role`` returns ``"unknown"`` rather than silently
    mis-attributing the role to whichever harness was hardcoded.
    """
    from groundtruth_kb.mcp_surface.roles import _default_harness_id

    # Clear all env vars that would trigger harness detection.
    for name in [
        "GTKB_HARNESS_ID",
        "CLAUDE_PROJECT_DIR",
        "CLAUDE_CODE_SDK",
        "CODEX_HOME",
        "CODEX_CONFIG_DIR",
    ]:
        monkeypatch.delenv(name, raising=False)
    # Also strip any other CLAUDE_CODE* / CODEX_* present in the test
    # environment so the detection logic sees a clean slate.
    for name in list(__import__("os").environ.keys()):
        if name.startswith("CLAUDE_CODE") or name.startswith("CODEX_"):
            monkeypatch.delenv(name, raising=False)

    result = _default_harness_id()
    assert result == "", (
        f"_default_harness_id() must return empty string when no harness "
        f"can be detected (fail-closed); got {result!r}. Hardcoding 'B' (or "
        f"any other ID) silently mis-attributes the role in a Codex session."
    )


def test_t12b_default_harness_id_resolves_claude_via_claude_project_dir(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When ``CLAUDE_PROJECT_DIR`` is set, the active harness resolves to the
    Claude identity (B) via ``harness-state/harness-identities.json``."""
    from groundtruth_kb.mcp_surface.roles import _default_harness_id

    monkeypatch.delenv("GTKB_HARNESS_ID", raising=False)
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(PROJECT_ROOT))

    assert _default_harness_id() == "B"


def test_t12c_default_harness_id_resolves_codex_via_codex_home(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When ``CODEX_HOME`` is set, the active harness resolves to the Codex
    identity (A) via ``harness-state/harness-identities.json``, NOT to the
    hardcoded Claude default (B) that the prior implementation used."""
    from groundtruth_kb.mcp_surface.roles import _default_harness_id

    monkeypatch.delenv("GTKB_HARNESS_ID", raising=False)
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    # Strip Claude-detection vars from inherited env.
    for name in list(__import__("os").environ.keys()):
        if name.startswith("CLAUDE_CODE"):
            monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("CODEX_HOME", "/tmp/codex-test")

    assert _default_harness_id() == "A"


# ---------------------------------------------------------------------------
# T10 - server scaffold imports + registers cleanly
# ---------------------------------------------------------------------------


def test_t10_server_scaffold_imports_and_registers_tool() -> None:
    from groundtruth_kb.mcp_surface.server import SERVER, SERVER_NAME, build_server

    assert SERVER_NAME == "gt-kb-mcp"
    # SERVER should be a constructed Server instance (truthy, non-None).
    assert SERVER is not None
    # Re-building should succeed without crashing (idempotent constructor).
    second = build_server()
    assert second is not None
