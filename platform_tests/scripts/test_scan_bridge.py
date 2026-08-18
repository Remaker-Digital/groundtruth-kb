"""Unit tests for scripts/skill-helpers/gtkb-bridge/scan_bridge.py."""

from __future__ import annotations

import importlib.util
import json
import sqlite3
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HELPER_PATH = (
    PROJECT_ROOT / "scripts" / "skill-helpers" / "gtkb-bridge" / "scan_bridge.py"
)
TEMPLATE_HELPER_PATH = (
    PROJECT_ROOT
    / "groundtruth-kb"
    / "templates"
    / "skills"
    / "gtkb-bridge"
    / "helpers"
    / "scan_bridge.py"
)


def _load_module(path: Path, module_name: str):
    import sys

    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _load_helper():
    return _load_module(HELPER_PATH, "scan_bridge")


@pytest.fixture(scope="module")
def helper():
    return _load_helper()


def _write_version(
    bridge_dir: Path,
    slug: str,
    version: int,
    status: str,
    *,
    bridge_kind: str | None = None,
) -> None:
    kind_line = f"\nbridge_kind: {bridge_kind}" if bridge_kind else ""
    (bridge_dir / f"{slug}-{version:03d}.md").write_text(
        f"{status}{kind_line}\nDocument: {slug}\nVersion: {version:03d}\n",
        encoding="utf-8",
    )


def _normalized_scan_result(result: dict) -> dict:
    return {
        "role": result["role"],
        "summary": result["summary"],
        "actionable": sorted(
            (thread["document"], thread["latest_status"], thread["latest_path"])
            for thread in result["actionable"]
        ),
        "blocked": sorted(
            (
                thread["document"],
                thread["latest_status"],
                tuple(thread.get("reasons", [])),
            )
            for thread in result["blocked_non_activatable"]
        ),
        "terminal_verified_count": result.get(
            "terminal_verified_count",
            len(result.get("terminal_verified", [])),
        ),
        "excluded_archived_count": result.get(
            "excluded_archived_count",
            len(result.get("excluded_archived", [])),
        ),
    }


def test_t1_empty_index_yields_empty_actionable(helper) -> None:
    result = helper.scan(role="prime-builder", index_text="")
    assert result["actionable"] == []
    assert result["terminal_verified"] == []
    assert result["summary"] == {}
    assert result["role"] == "prime-builder"


def test_t2_latest_new_actionable_for_lo_not_prime(helper) -> None:
    index = """\
Document: gtkb-foo
NEW: bridge/gtkb-foo-001.md
"""
    lo_result = helper.scan(role="loyal-opposition", index_text=index)
    prime_result = helper.scan(role="prime-builder", index_text=index)
    assert len(lo_result["actionable"]) == 1
    assert lo_result["actionable"][0]["document"] == "gtkb-foo"
    assert lo_result["actionable"][0]["latest_status"] == "NEW"
    assert prime_result["actionable"] == []


def test_t3_latest_go_actionable_for_prime_not_lo(helper) -> None:
    index = """\
Document: gtkb-foo
GO: bridge/gtkb-foo-002.md
NEW: bridge/gtkb-foo-001.md
"""
    prime_result = helper.scan(role="prime-builder", index_text=index)
    lo_result = helper.scan(role="loyal-opposition", index_text=index)
    assert len(prime_result["actionable"]) == 1
    assert prime_result["actionable"][0]["latest_status"] == "GO"
    assert prime_result["blocked_non_activatable"] == []
    assert lo_result["actionable"] == []


def test_t4_latest_nogo_actionable_for_prime_not_lo(helper) -> None:
    index = """\
Document: gtkb-foo
NO-GO: bridge/gtkb-foo-002.md
NEW: bridge/gtkb-foo-001.md
"""
    prime_result = helper.scan(role="prime-builder", index_text=index)
    lo_result = helper.scan(role="loyal-opposition", index_text=index)
    assert len(prime_result["actionable"]) == 1
    assert prime_result["actionable"][0]["latest_status"] == "NO-GO"
    assert lo_result["actionable"] == []


def test_t5_latest_revised_actionable_for_lo_not_prime(helper) -> None:
    index = """\
Document: gtkb-foo
REVISED: bridge/gtkb-foo-003.md
NO-GO: bridge/gtkb-foo-002.md
NEW: bridge/gtkb-foo-001.md
"""
    lo_result = helper.scan(role="loyal-opposition", index_text=index)
    prime_result = helper.scan(role="prime-builder", index_text=index)
    assert len(lo_result["actionable"]) == 1
    assert lo_result["actionable"][0]["latest_status"] == "REVISED"
    assert prime_result["actionable"] == []


def test_latest_no_action_actionable_for_lo_not_prime(helper) -> None:
    index = """\
Document: gtkb-foo
NO-ACTION: bridge/gtkb-foo-003.md
GO: bridge/gtkb-foo-002.md
NEW: bridge/gtkb-foo-001.md
"""
    lo_result = helper.scan(role="loyal-opposition", index_text=index)
    prime_result = helper.scan(role="prime-builder", index_text=index)
    assert len(lo_result["actionable"]) == 1
    assert lo_result["actionable"][0]["latest_status"] == "NO-ACTION"
    assert prime_result["actionable"] == []


def test_t6_latest_verified_in_terminal_not_actionable(helper) -> None:
    index = """\
Document: gtkb-foo
VERIFIED: bridge/gtkb-foo-002.md
NEW: bridge/gtkb-foo-001.md
"""
    for role in ("prime-builder", "loyal-opposition"):
        result = helper.scan(role=role, index_text=index)
        assert result["actionable"] == []
        assert len(result["terminal_verified"]) == 1
        assert result["terminal_verified"][0]["latest_status"] == "VERIFIED"


def test_compact_scan_omits_terminal_payloads_and_version_chains(helper) -> None:
    index = """\
Document: gtkb-go
GO: bridge/gtkb-go-002.md
NEW: bridge/gtkb-go-001.md

Document: gtkb-verified
VERIFIED: bridge/gtkb-verified-003.md
GO: bridge/gtkb-verified-002.md
NEW: bridge/gtkb-verified-001.md
"""

    result = helper.scan(role="prime-builder", index_text=index, compact=True)

    assert result["compact"] is True
    assert result["terminal_verified_count"] == 1
    assert "terminal_verified" not in result
    assert "excluded_archived" not in result
    assert result["actionable"][0]["document"] == "gtkb-go"
    assert "version_chain" not in result["actionable"][0]


@pytest.mark.parametrize("role", ["prime-builder", "loyal-opposition"])
def test_compact_live_scan_bounds_reads_and_matches_full_classification(
    helper,
    monkeypatch,
    tmp_path,
    role,
) -> None:
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    config_dir = tmp_path / "config" / "governance"
    config_dir.mkdir(parents=True)
    (config_dir / "tafe-acknowledged-archived-bridges.toml").write_text(
        'schema_version = 1\n\n[[acknowledged]]\nslug = "gtkb-archived"\nreason = "test fixture"\n',
        encoding="utf-8",
    )

    _write_version(
        bridge_dir, "gtkb-go", 1, "NEW", bridge_kind="implementation_proposal"
    )
    _write_version(bridge_dir, "gtkb-go", 2, "NO-GO")
    _write_version(
        bridge_dir, "gtkb-go", 3, "REVISED", bridge_kind="implementation_proposal"
    )
    _write_version(bridge_dir, "gtkb-go", 4, "GO")
    _write_version(
        bridge_dir, "gtkb-new", 1, "NEW", bridge_kind="implementation_proposal"
    )
    _write_version(
        bridge_dir, "gtkb-archived", 1, "NEW", bridge_kind="implementation_proposal"
    )
    for version in range(1, 13):
        status = "VERIFIED" if version == 12 else ("GO" if version % 2 == 0 else "NEW")
        _write_version(
            bridge_dir,
            "gtkb-terminal-history",
            version,
            status,
            bridge_kind="implementation_proposal" if status == "NEW" else None,
        )

    status_reads: list[str] = []
    original_status_reader = helper._status_from_bridge_file

    def counted_status_reader(path):
        status_reads.append(Path(path).name)
        return original_status_reader(path)

    monkeypatch.setattr(helper, "_status_from_bridge_file", counted_status_reader)
    monkeypatch.setattr(helper, "_go_activatable", lambda _root, _bridge_id: (True, []))
    index_path = bridge_dir / "state.md"

    full = helper.scan(role=role, index_path=index_path)
    full_read_count = len(status_reads)
    status_reads.clear()
    compact = helper.scan(role=role, index_path=index_path, compact=True)
    compact_read_count = len(status_reads)

    assert _normalized_scan_result(compact) == _normalized_scan_result(full)
    assert compact_read_count <= 5
    assert compact_read_count < full_read_count
    assert compact["excluded_archived_count"] == 1
    assert compact["terminal_verified_count"] == 1
    assert "terminal_verified" not in compact
    assert "excluded_archived" not in compact
    assert all("version_chain" not in thread for thread in compact["actionable"])


@pytest.mark.parametrize("role", ["prime-builder", "loyal-opposition"])
def test_template_compact_scan_bounds_reads_and_matches_full_classification(
    monkeypatch,
    tmp_path,
    role,
) -> None:
    template_helper = _load_module(
        TEMPLATE_HELPER_PATH, f"scan_bridge_template_compact_{role}"
    )
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    statuses = {
        "gtkb-template-new": "NEW",
        "gtkb-template-revised": "REVISED",
        "gtkb-template-advisory": "ADVISORY",
        "gtkb-template-verified": "VERIFIED",
    }
    for slug, latest_status in statuses.items():
        for version in range(1, 9):
            _write_version(
                bridge_dir,
                slug,
                version,
                latest_status,
                bridge_kind="implementation_proposal"
                if latest_status in {"NEW", "REVISED"}
                else None,
            )

    status_reads: list[str] = []
    original_status_reader = template_helper._status_from_bridge_file

    def counted_status_reader(path):
        status_reads.append(Path(path).name)
        return original_status_reader(path)

    monkeypatch.setattr(
        template_helper, "_status_from_bridge_file", counted_status_reader
    )
    index_path = bridge_dir / "state.md"

    full = template_helper.scan(role=role, index_path=index_path)
    full_read_count = len(status_reads)
    status_reads.clear()
    compact = template_helper.scan(role=role, index_path=index_path, compact=True)

    assert _normalized_scan_result(compact) == _normalized_scan_result(full)
    assert len(status_reads) == len(statuses)
    assert len(status_reads) < full_read_count
    assert compact["terminal_verified_count"] == 1
    assert "terminal_verified" not in compact
    assert all("version_chain" not in thread for thread in compact["actionable"])


def test_t7_mixed_index_partitions_correctly(helper) -> None:
    index = """\
Document: gtkb-a
GO: bridge/gtkb-a-002.md
NEW: bridge/gtkb-a-001.md

Document: gtkb-b
NEW: bridge/gtkb-b-001.md

Document: gtkb-c
VERIFIED: bridge/gtkb-c-003.md
GO: bridge/gtkb-c-002.md
NEW: bridge/gtkb-c-001.md

Document: gtkb-d
NO-GO: bridge/gtkb-d-002.md
NEW: bridge/gtkb-d-001.md

Document: gtkb-e
REVISED: bridge/gtkb-e-003.md
NO-GO: bridge/gtkb-e-002.md
NEW: bridge/gtkb-e-001.md
"""
    prime_result = helper.scan(role="prime-builder", index_text=index)
    lo_result = helper.scan(role="loyal-opposition", index_text=index)

    prime_docs = {t["document"] for t in prime_result["actionable"]}
    lo_docs = {t["document"] for t in lo_result["actionable"]}

    assert prime_docs == {"gtkb-a", "gtkb-d"}  # GO + NO-GO
    assert lo_docs == {"gtkb-b", "gtkb-e"}  # NEW + REVISED

    assert {t["document"] for t in prime_result["terminal_verified"]} == {"gtkb-c"}
    assert prime_result["summary"] == {
        "GO": 1,
        "NEW": 1,
        "VERIFIED": 1,
        "NO-GO": 1,
        "REVISED": 1,
    }


def test_t8_comment_header_skipped(helper) -> None:
    index = """\
# Bridge Index

<!-- Prime inserts new document entries at the top of the list below. -->
<!-- Codex scans for NEW/REVISED statuses and adds GO/NO-GO/VERIFIED versions. -->

Document: gtkb-foo
NEW: bridge/gtkb-foo-001.md
"""
    result = helper.scan(role="loyal-opposition", index_text=index)
    assert len(result["actionable"]) == 1
    assert result["actionable"][0]["document"] == "gtkb-foo"


def test_invalid_role_raises(helper) -> None:
    with pytest.raises(ValueError):
        helper.scan(role="other", index_text="")


def test_version_chain_preserves_order(helper) -> None:
    """Version chain reports versions latest-first per INDEX convention."""
    index = """\
Document: gtkb-foo
REVISED: bridge/gtkb-foo-005.md
NO-GO: bridge/gtkb-foo-004.md
REVISED: bridge/gtkb-foo-003.md
NO-GO: bridge/gtkb-foo-002.md
NEW: bridge/gtkb-foo-001.md
"""
    result = helper.scan(role="loyal-opposition", index_text=index)
    chain = result["actionable"][0]["version_chain"]
    assert [v["status"] for v in chain] == [
        "REVISED",
        "NO-GO",
        "REVISED",
        "NO-GO",
        "NEW",
    ]
    assert chain[0]["path"] == "bridge/gtkb-foo-005.md"


def test_generated_at_iso_format(helper) -> None:
    result = helper.scan(role="prime-builder", index_text="")
    assert result["generated_at"].endswith("Z")
    assert "T" in result["generated_at"]


# --- Terminal-kind GO filtering (WI-4278; gtkb-manual-bridge-scan-terminal-go-filter) ---


def _write_bridge_thread(
    bridge_dir: Path, slug: str, operative_kind: str, latest_status: str
) -> None:
    """Write the operative Prime proposal file for a thread.

    Only the operative (NEW) file needs to exist; classification reads
    ``bridge_kind`` from the operative Prime version, not the verdict file.
    """
    operative = bridge_dir / f"{slug}-001.md"
    operative.write_text(
        f"NEW\n\nbridge_kind: {operative_kind}\nDocument: {slug}\nVersion: 001\n",
        encoding="utf-8",
    )


def _write_current_work_items(root: Path, rows: dict[str, str]) -> None:
    with sqlite3.connect(root / "groundtruth.db") as con:
        con.execute(
            "CREATE TABLE current_work_items (id TEXT PRIMARY KEY, resolution_status TEXT)"
        )
        con.executemany(
            "INSERT INTO current_work_items (id, resolution_status) VALUES (?, ?)",
            sorted(rows.items()),
        )


def _write_work_item_bridge_thread(
    bridge_dir: Path,
    slug: str,
    latest_status: str,
    work_item_id: str,
) -> None:
    (bridge_dir / f"{slug}-001.md").write_text(
        f"NEW\n\nbridge_kind: implementation_proposal\nWork Item: {work_item_id}\n",
        encoding="utf-8",
    )
    (bridge_dir / f"{slug}-002.md").write_text(
        f"{latest_status}\n\nWork Item: {work_item_id}\n",
        encoding="utf-8",
    )


def test_terminal_kind_go_excluded_from_prime(helper, tmp_path) -> None:
    """A latest GO with terminal-kind bridge_kind is excluded from Prime work,
    while a non-terminal GO and a terminal-kind NO-GO are preserved."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    _write_bridge_thread(bridge_dir, "gtkb-gov", "governance_review", "GO")
    _write_bridge_thread(bridge_dir, "gtkb-impl", "implementation_proposal", "GO")
    _write_bridge_thread(bridge_dir, "gtkb-gov-nogo", "governance_review", "NO-GO")
    index = (
        "Document: gtkb-gov\n"
        "GO: bridge/gtkb-gov-002.md\n"
        "NEW: bridge/gtkb-gov-001.md\n"
        "\n"
        "Document: gtkb-impl\n"
        "GO: bridge/gtkb-impl-002.md\n"
        "NEW: bridge/gtkb-impl-001.md\n"
        "\n"
        "Document: gtkb-gov-nogo\n"
        "NO-GO: bridge/gtkb-gov-nogo-002.md\n"
        "NEW: bridge/gtkb-gov-nogo-001.md\n"
    )
    index_path = bridge_dir / "state.md"

    prime = helper.scan(role="prime-builder", index_text=index, index_path=index_path)
    prime_docs = {t["document"] for t in prime["actionable"]}

    # Terminal-kind GO excluded; non-terminal GO and terminal-kind NO-GO kept.
    assert prime_docs == {"gtkb-impl", "gtkb-gov-nogo"}
    assert "gtkb-gov" not in prime_docs


def test_template_terminal_work_item_go_moved_to_blocked_bucket(tmp_path) -> None:
    """The managed helper template excludes GO/NO-GO entries whose MemBase WI is terminal."""
    template_helper = _load_module(
        TEMPLATE_HELPER_PATH, "scan_bridge_template_terminal_wi"
    )
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    _write_work_item_bridge_thread(bridge_dir, "gtkb-terminal-wi", "NO-GO", "WI-5002")
    _write_current_work_items(tmp_path, {"WI-5002": "retired"})
    index = "Document: gtkb-terminal-wi\nNO-GO: bridge/gtkb-terminal-wi-002.md\nNEW: bridge/gtkb-terminal-wi-001.md\n"
    index_path = bridge_dir / "state.md"

    result = template_helper.scan(
        role="prime-builder", index_text=index, index_path=index_path
    )

    assert result["actionable"] == []
    assert len(result["blocked_non_activatable"]) == 1
    assert result["blocked_non_activatable"][0]["document"] == "gtkb-terminal-wi"
    assert result["blocked_non_activatable"][0]["latest_status"] == "NO-GO"
    assert result["blocked_non_activatable"][0]["reasons"] == [
        "referenced work item terminal (WI-5002=retired)"
    ]


def test_terminal_kind_does_not_affect_lo(helper, tmp_path) -> None:
    """Loyal Opposition actionability (NEW/REVISED) is unaffected by kind."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    _write_bridge_thread(bridge_dir, "gtkb-gov", "governance_review", "NEW")
    index = "Document: gtkb-gov\nNEW: bridge/gtkb-gov-001.md\n"
    index_path = bridge_dir / "state.md"

    lo = helper.scan(role="loyal-opposition", index_text=index, index_path=index_path)
    assert {t["document"] for t in lo["actionable"]} == {"gtkb-gov"}


def test_unreadable_operative_go_stays_actionable(helper, tmp_path) -> None:
    """Fail-open: a GO whose operative file is missing stays Prime-actionable."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    # No operative file written -> classification fails open to actionable.
    index = "Document: gtkb-ghost\nGO: bridge/gtkb-ghost-002.md\nNEW: bridge/gtkb-ghost-001.md\n"
    index_path = bridge_dir / "state.md"

    prime = helper.scan(role="prime-builder", index_text=index, index_path=index_path)
    assert {t["document"] for t in prime["actionable"]} == {"gtkb-ghost"}


def test_terminal_tokens_parity_with_canonical_notify(helper) -> None:
    """The mirrored terminal-token set must match the canonical notify set to
    prevent classifier drift."""
    from groundtruth_kb.bridge import notify

    assert set(helper._KIND_TERMINAL_TOKENS) == set(notify._KIND_TERMINAL_TOKENS)


def test_archive_terminal_tokens_parity_with_versioned_file_classifier(helper) -> None:
    from groundtruth_kb.bridge import versioned_files

    assert helper._ARCHIVE_TERMINAL_STATUSES == versioned_files._TERMINAL_STATUS_TOKENS


def test_actionable_status_sets_parity_with_shared_disposition(helper) -> None:
    """Manual scans and notification routing must share the same status matrix."""
    from groundtruth_kb.bridge import disposition

    assert helper.PRIME_ACTIONABLE_STATUSES == disposition.PRIME_ACTIONABLE_STATUSES
    assert (
        helper.LO_ACTIONABLE_STATUSES
        == disposition.LOYAL_OPPOSITION_ACTIONABLE_STATUSES
    )


def test_template_terminal_tokens_parity_with_live_helper(helper) -> None:
    """The managed template helper must not drift from the live helper."""
    template_helper = _load_module(TEMPLATE_HELPER_PATH, "scan_bridge_template")

    assert set(template_helper._KIND_TERMINAL_TOKENS) == set(
        helper._KIND_TERMINAL_TOKENS
    )


def test_advisory_actionable_for_prime_not_lo(helper) -> None:
    """ADVISORY status entries surface in the Prime actionable list (so manual
    `/bridge` scans show them for owner-deliberation/UAQ disposition) but never
    surface for Loyal Opposition. Per gtkb-advisory-prime-actionability-
    surfacing-002 (Codex GO 2026-06-14) Condition 1.
    """
    index = """\
Document: gtkb-foo-advisory
ADVISORY: bridge/gtkb-foo-advisory-001.md
"""
    prime_result = helper.scan(role="prime-builder", index_text=index)
    lo_result = helper.scan(role="loyal-opposition", index_text=index)
    assert len(prime_result["actionable"]) == 1
    assert prime_result["actionable"][0]["document"] == "gtkb-foo-advisory"
    assert prime_result["actionable"][0]["latest_status"] == "ADVISORY"
    assert lo_result["actionable"] == []


def test_non_activatable_go_moved_to_blocked_bucket(helper, monkeypatch) -> None:
    monkeypatch.setattr(
        helper,
        "_go_activatable",
        lambda _root, _bridge_id: (False, ["missing spec links"]),
    )
    index = """\
Document: gtkb-dead-end
GO: bridge/gtkb-dead-end-002.md
NEW: bridge/gtkb-dead-end-001.md
"""

    result = helper.scan(role="prime-builder", index_text=index)

    assert result["actionable"] == []
    assert len(result["blocked_non_activatable"]) == 1
    assert result["blocked_non_activatable"][0]["document"] == "gtkb-dead-end"
    assert (
        result["blocked_non_activatable"][0]["go_file"] == "bridge/gtkb-dead-end-002.md"
    )
    assert result["blocked_non_activatable"][0]["reasons"] == ["missing spec links"]


def test_activatable_go_remains_actionable(helper, monkeypatch) -> None:
    monkeypatch.setattr(helper, "_go_activatable", lambda _root, _bridge_id: (True, []))
    index = """\
Document: gtkb-ready
GO: bridge/gtkb-ready-002.md
NEW: bridge/gtkb-ready-001.md
"""

    result = helper.scan(role="prime-builder", index_text=index)

    assert [thread["document"] for thread in result["actionable"]] == ["gtkb-ready"]
    assert result["blocked_non_activatable"] == []


def test_blocked_go_carries_begin_gate_reasons(helper, monkeypatch, tmp_path) -> None:
    def fail_packet(_project_root, _bridge_id):
        raise helper.AuthorizationError(
            "missing spec links; missing ## Requirement Sufficiency"
        )

    monkeypatch.setattr(helper, "create_authorization_packet", fail_packet)

    activatable, reasons = helper._go_activatable(tmp_path, "gtkb-blocked")

    assert activatable is False
    assert reasons == ["missing spec links", "missing ## Requirement Sufficiency"]


def test_prefix_named_go_still_runs_activatability(
    helper, monkeypatch, tmp_path
) -> None:
    def fail_packet(_project_root, _bridge_id):
        raise helper.AuthorizationError("self-review refused")

    monkeypatch.setattr(helper, "create_authorization_packet", fail_packet)

    activatable, reasons = helper._go_activatable(tmp_path, "test-blocked")

    assert activatable is False
    assert reasons == ["self-review refused"]


def test_dispatch_terminal_go_still_filtered_before_activatability(
    helper, monkeypatch, tmp_path
) -> None:
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    _write_bridge_thread(bridge_dir, "gtkb-gov", "governance_review", "GO")
    index = (
        "Document: gtkb-gov\nGO: bridge/gtkb-gov-002.md\nNEW: bridge/gtkb-gov-001.md\n"
    )
    index_path = bridge_dir / "state.md"

    def should_not_run(_root, _bridge_id):
        raise AssertionError("terminal GO should not reach activatability")

    monkeypatch.setattr(helper, "_go_activatable", should_not_run)

    result = helper.scan(role="prime-builder", index_text=index, index_path=index_path)

    assert result["actionable"] == []
    assert result["blocked_non_activatable"] == []


def test_nogo_and_advisory_actionability_unchanged(helper, monkeypatch) -> None:
    def should_not_run(_root, _bridge_id):
        raise AssertionError("activatability applies only to GO entries")

    monkeypatch.setattr(helper, "_go_activatable", should_not_run)
    index = """\
Document: gtkb-nogo
NO-GO: bridge/gtkb-nogo-002.md
NEW: bridge/gtkb-nogo-001.md

Document: gtkb-advisory
ADVISORY: bridge/gtkb-advisory-001.md
"""

    result = helper.scan(role="prime-builder", index_text=index)

    assert {thread["document"] for thread in result["actionable"]} == {
        "gtkb-nogo",
        "gtkb-advisory",
    }
    assert result["blocked_non_activatable"] == []


def test_many_version_compact_cli_completes_in_bound_and_prints_json(
    helper, tmp_path, monkeypatch, capsys
) -> None:
    """WI-6607 (a): many-version compact scan completes inside the bound and prints JSON."""
    monkeypatch.setenv(helper._COMPLETION_BOUND_ENV, "60")
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    for index in range(25):
        slug = f"gtkb-many-{index:03d}"
        for version in range(1, 13):
            if version == 1:
                status = "NEW"
            elif version == 12:
                status = "GO"
            else:
                status = "REVISED" if version % 2 else "NO-GO"
            _write_version(
                bridge_dir,
                slug,
                version,
                status,
                bridge_kind="implementation_proposal"
                if status in {"NEW", "REVISED"}
                else None,
            )
    index_path = bridge_dir / "state.md"

    rc = helper.main(
        [
            "--role",
            "prime-builder",
            "--compact",
            "--format",
            "json",
            "--index-path",
            str(index_path),
        ]
    )
    captured = capsys.readouterr()

    assert rc == 0
    assert captured.err == ""
    payload = json.loads(captured.out)
    assert payload["compact"] is True
    assert payload["role"] == "prime-builder"
    assert len(payload["actionable"]) == 25
    assert all(thread["latest_status"] == "GO" for thread in payload["actionable"])


def test_compact_prime_scan_does_not_call_create_authorization_packet(
    helper, monkeypatch, tmp_path
) -> None:
    """WI-6607 (b): compact Prime listing does not mint packets or call _go_activatable."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    _write_version(
        bridge_dir, "gtkb-ready", 1, "NEW", bridge_kind="implementation_proposal"
    )
    _write_version(bridge_dir, "gtkb-ready", 2, "GO")
    index_path = bridge_dir / "state.md"

    def boom_packet(*_args, **_kwargs):
        raise AssertionError("create_authorization_packet must not run in compact mode")

    def boom_activatable(*_args, **_kwargs):
        raise AssertionError("_go_activatable must not run in compact mode")

    monkeypatch.setattr(helper, "create_authorization_packet", boom_packet)
    monkeypatch.setattr(helper, "_go_activatable", boom_activatable)

    result = helper.scan(role="prime-builder", index_path=index_path, compact=True)

    assert [thread["document"] for thread in result["actionable"]] == ["gtkb-ready"]
    assert result["blocked_non_activatable"] == []


def test_expired_deadline_fails_closed_named_stderr_empty_stdout(
    helper, tmp_path, monkeypatch, capsys
) -> None:
    """WI-6607 (c): expired bound fails closed with named stderr and no stdout."""
    monkeypatch.setenv(helper._COMPLETION_BOUND_ENV, "0")
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    _write_version(
        bridge_dir, "gtkb-timeout", 1, "NEW", bridge_kind="implementation_proposal"
    )
    index_path = bridge_dir / "state.md"

    with pytest.raises(helper.ScanBridgeCompletionBoundExceeded) as excinfo:
        helper.scan(role="prime-builder", index_path=index_path, compact=True)
    assert helper.SCAN_BRIDGE_COMPLETION_BOUND_EXCEEDED in str(excinfo.value)

    rc = helper.main(
        [
            "--role",
            "prime-builder",
            "--compact",
            "--format",
            "json",
            "--index-path",
            str(index_path),
        ]
    )
    captured = capsys.readouterr()

    assert rc != 0
    assert captured.out == ""
    assert helper.SCAN_BRIDGE_COMPLETION_BOUND_EXCEEDED in captured.err
    assert "elapsed" in captured.err
    assert "limit" in captured.err


def test_status_reads_do_not_consume_bytes_past_header_budget(
    helper, tmp_path, monkeypatch
) -> None:
    """WI-6607 (d): status reads cap at _HEADER_READ_BUDGET_BYTES."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    oversized = "NEW\n" + ("x" * (helper._HEADER_READ_BUDGET_BYTES * 4))
    path = bridge_dir / "gtkb-header-budget-001.md"
    path.write_text(oversized, encoding="utf-8")

    read_sizes: list[int] = []
    original_open = Path.open

    def wrapping_open(self, *args, **kwargs):
        handle = original_open(self, *args, **kwargs)
        orig_read = handle.read

        def counted_read(size=-1):
            read_sizes.append(size)
            return orig_read(size)

        handle.read = counted_read
        return handle

    monkeypatch.setattr(Path, "open", wrapping_open)

    assert helper._status_from_bridge_file(path) == "NEW"
    assert read_sizes
    assert all(
        size != -1 and size <= helper._HEADER_READ_BUDGET_BYTES for size in read_sizes
    )
