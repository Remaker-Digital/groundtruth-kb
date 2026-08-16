"""Spec-derived tests for the registry publication diagnostics module (WI-6177).

The load-bearing assertion is ``test_blocking_error_set_matches_gate_source``:
it binds the module's publication-blocking classification to the conditions the
real gate raises on, by introspecting the gate source. Without that binding the
classifier is a hand-maintained duplicate of the gate and will drift the first
time the gate changes -- which is the same class of defect WI-6177 exists to fix.

Approved at
``bridge/gtkb-wi6177-registry-publication-diagnostic-classification-002.md``.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import inspect
import re
import sqlite3
from pathlib import Path

import pytest
from groundtruth_kb.project import registry_control_plane as rcp
from groundtruth_kb.project import registry_publication_diagnostics as rpd

PROJECT_ROOT = Path(__file__).resolve().parents[3]


# --------------------------------------------------------------------------
# Anti-drift binding: DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
# --------------------------------------------------------------------------


def _raised_exception_names(func) -> set[str]:
    """Return the exception type names syntactically raised inside ``func``."""
    source = inspect.getsource(func)
    return set(re.findall(r"\braise\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", source))


def test_blocking_error_set_matches_gate_source() -> None:
    """The blocking set exactly matches the real gate plus its fallback code.

    This is the anti-drift binding. If either gate check adds or removes a
    typed failure, this test fails until the classifier is dispositioned. The
    only non-exception entry is ``registry_not_coherent``, the explicit generic
    fallback emitted by ``validate_registry`` when inspection supplies no
    typed error.
    """
    snapshot_raised = _raised_exception_names(rcp._load_snapshot_unlocked)
    journal_raised = _raised_exception_names(rcp._ensure_no_nonterminal_journal)
    expected = snapshot_raised | journal_raised | {"registry_not_coherent"}

    assert snapshot_raised == {"RegistryControlPlaneError", "RegistryProjectionMismatch"}
    assert journal_raised == {"RegistryTransactionInProgress"}
    assert expected == rpd.PUBLICATION_BLOCKING_ERROR_CODES


def test_audit_only_codes_are_not_gate_conditions() -> None:
    """The gate must not consult membership or identity state.

    If a future edit makes the gate read either, these codes stop being
    audit-only and this test fails, forcing the classification to be revisited.
    """
    gate_source = inspect.getsource(rcp._load_snapshot_unlocked).lower()

    assert "membership" not in gate_source
    assert "identity_state" not in gate_source


def test_blocking_and_audit_sets_are_disjoint() -> None:
    assert not (rpd.PUBLICATION_BLOCKING_ERROR_CODES & rpd.AUDIT_ONLY_ERROR_CODES)


def test_validate_registry_emits_only_classified_codes() -> None:
    """Codes literally emitted by validate_registry must all be classified."""
    source = inspect.getsource(rcp.validate_registry)
    literals = set(re.findall(r'errors\.append\(\s*"([a-z_]+)"', source))
    known = rpd.PUBLICATION_BLOCKING_ERROR_CODES | rpd.AUDIT_ONLY_ERROR_CODES

    assert literals, "expected validate_registry to append at least one literal code"
    assert literals <= known, f"unclassified validate_registry codes: {sorted(literals - known)}"


# --------------------------------------------------------------------------
# Probe behaviour: GOV-SOURCE-OF-TRUTH-FRESHNESS-001 / GOV-FILE-BRIDGE-AUTHORITY-001
# --------------------------------------------------------------------------


def test_probe_reports_not_blocked_when_gate_passes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rpd._rcp, "_ensure_no_nonterminal_journal", lambda _db: None)
    monkeypatch.setattr(rpd._rcp, "_load_snapshot_unlocked", lambda _paths: object())

    state = rpd.publication_gate_state(project_root=PROJECT_ROOT)

    assert state.publication_blocking is False
    assert state.blocking_code is None
    assert state.checks == {"nonterminal_journal": "pass", "snapshot_load": "pass"}


def test_probe_reports_blocked_on_parity_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    """A parity failure is the condition that genuinely blocks publication."""

    def _boom(_paths):
        raise rcp.RegistryProjectionMismatch("registry declaration/projection parity failure: ...")

    monkeypatch.setattr(rpd._rcp, "_ensure_no_nonterminal_journal", lambda _db: None)
    monkeypatch.setattr(rpd._rcp, "_load_snapshot_unlocked", _boom)

    state = rpd.publication_gate_state(project_root=PROJECT_ROOT)

    assert state.publication_blocking is True
    assert state.blocking_code == "RegistryProjectionMismatch"
    assert "parity" in (state.blocking_reason or "")
    assert state.checks["snapshot_load"] == "fail"


def test_probe_reports_blocked_on_nonterminal_journal(monkeypatch: pytest.MonkeyPatch) -> None:
    """The journal check runs before the snapshot load and short-circuits it."""

    def _boom(_db):
        raise rcp.RegistryTransactionInProgress("registry transaction in progress")

    sentinel: list[str] = []
    monkeypatch.setattr(rpd._rcp, "_ensure_no_nonterminal_journal", _boom)
    monkeypatch.setattr(rpd._rcp, "_load_snapshot_unlocked", lambda _paths: sentinel.append("reached"))

    state = rpd.publication_gate_state(project_root=PROJECT_ROOT)

    assert state.publication_blocking is True
    assert state.blocking_code == "RegistryTransactionInProgress"
    assert state.checks == {"nonterminal_journal": "fail"}
    assert sentinel == [], "snapshot load must not run after the journal check fails"


def test_probe_runs_against_the_live_registry() -> None:
    """End-to-end smoke: the probe resolves real paths and returns a verdict."""
    state = rpd.publication_gate_state(project_root=PROJECT_ROOT)

    assert isinstance(state.publication_blocking, bool)
    assert state.checks["nonterminal_journal"] in {"pass", "fail"}
    assert set(state.to_dict()) == {
        "publication_blocking",
        "blocking_code",
        "blocking_reason",
        "checks",
    }


def test_probe_is_side_effect_free() -> None:
    """GOV-PLATFORM-SOT-REGISTRY-001: a diagnostic read must not mutate state."""
    paths = rcp.RegistryPaths.resolve(project_root=PROJECT_ROOT)

    registry_before = paths.registry_path.read_bytes()
    db_stat_before = paths.db_path.stat().st_mtime_ns

    def _capability_rows() -> int:
        con = sqlite3.connect(f"file:{paths.db_path}?mode=ro", uri=True, timeout=10)
        try:
            cur = con.execute("SELECT COUNT(*) FROM sot_registry_bridge_publication_capabilities")
            return int(cur.fetchone()[0])
        except sqlite3.Error:
            return -1
        finally:
            con.close()

    rows_before = _capability_rows()

    rpd.publication_gate_state(project_root=PROJECT_ROOT)

    assert paths.registry_path.read_bytes() == registry_before
    assert paths.db_path.stat().st_mtime_ns == db_stat_before
    assert _capability_rows() == rows_before


def test_probe_does_not_acquire_the_registry_lock(monkeypatch: pytest.MonkeyPatch) -> None:
    """The probe is a read, not a publication attempt; it must not take the lock."""
    taken: list[str] = []

    class _Tripwire:
        def __init__(self, *args, **kwargs):
            taken.append("acquired")

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    monkeypatch.setattr(rpd._rcp, "_RegistryFileLock", _Tripwire)

    rpd.publication_gate_state(project_root=PROJECT_ROOT)

    assert taken == []


# --------------------------------------------------------------------------
# Classifier: GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001
# --------------------------------------------------------------------------


def test_membership_incomplete_alone_does_not_block_publication() -> None:
    """The headline WI-6177 case: INVALID that does not mean 'publication blocked'."""
    result = rpd.classify_validate_errors(["registry_membership_incomplete"])

    assert result.audit_only == ("registry_membership_incomplete",)
    assert result.publication_blocking == ()
    assert result.blocks_publication is False


def test_parity_failure_is_classified_blocking() -> None:
    result = rpd.classify_validate_errors(["RegistryProjectionMismatch", "registry_membership_incomplete"])

    assert result.publication_blocking == ("RegistryProjectionMismatch",)
    assert result.audit_only == ("registry_membership_incomplete",)
    assert result.blocks_publication is True


def test_unknown_codes_are_conservatively_blocking() -> None:
    """Under-reporting a blocker is the more dangerous error, so unknown blocks."""
    result = rpd.classify_validate_errors(["registry_some_future_condition"])

    assert result.unclassified == ("registry_some_future_condition",)
    assert result.blocks_publication is True


def test_classifier_collapses_duplicates_and_preserves_order() -> None:
    result = rpd.classify_validate_errors(
        [
            "registry_membership_incomplete",
            "registry_identity_failure",
            "registry_membership_incomplete",
        ]
    )

    assert result.audit_only == ("registry_membership_incomplete", "registry_identity_failure")


def test_classifier_is_pure() -> None:
    codes = ["registry_membership_incomplete", "RegistryProjectionMismatch"]

    first = rpd.classify_validate_errors(codes)
    second = rpd.classify_validate_errors(codes)

    assert first == second
    assert codes == ["registry_membership_incomplete", "RegistryProjectionMismatch"]


def test_empty_error_list_does_not_block() -> None:
    result = rpd.classify_validate_errors([])

    assert result.blocks_publication is False
    assert result.to_dict()["blocks_publication"] is False
