"""Native read-only purge-pairing diagnostics and the retained Phase-1 advisory behavior."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _PROJECT_ROOT / "scripts"
for _path in (_SCRIPTS,):
    if _path.is_dir() and str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

import check_obsolete_reference_purge as check  # noqa: E402
import pytest  # noqa: E402
from groundtruth_kb.authority_client import AuthorityClient  # noqa: E402

PAST_DATE = "2000-01-01"
FUTURE_DATE = "2099-01-01"
FIXTURE_SPEC = "RETIRE-SPEC-OBSOLETE-FIXTURE-001"


# ---------------------------------------------------------------------------
# Pure-function unit tests (hermetic; no database)
# ---------------------------------------------------------------------------


def test_is_retirement_class_retired_status():
    ok, reason = check.is_retirement_class({"id": "SPEC-1", "status": "retired"})
    assert ok
    assert "retired" in reason


def test_is_retirement_class_superseded_status():
    ok, _ = check.is_retirement_class({"id": "SPEC-2", "status": "superseded"})
    assert ok


def test_is_retirement_class_retire_spec_prefix():
    ok, reason = check.is_retirement_class({"id": FIXTURE_SPEC, "status": "active"})
    assert ok
    assert "RETIRE-SPEC" in reason


def test_is_retirement_class_adr_supersedes_field():
    ok, reason = check.is_retirement_class(
        {
            "id": "ADR-X-001",
            "status": "active",
            "type": "architecture_decision",
            "description": "Decision body.\nSupersedes: ADR-OLD-LOAD-BEARING-001\nConsequences...",
        }
    )
    assert ok
    assert "Supersedes" in reason


def test_is_retirement_class_definitional_supersedes_not_flagged():
    # Regression: an ADR/DCL whose PROSE contains the word "supersedes" (e.g. the
    # obligation DCL's own definition) but has no structured Supersedes: field must
    # NOT be flagged as retirement-class.
    ok, _ = check.is_retirement_class(
        {
            "id": "DCL-METHODOLOGY-001",
            "status": "active",
            "type": "design_constraint",
            "description": "an ADR/DCL that supersedes a prior load-bearing implementation",
        }
    )
    assert not ok


def test_is_retirement_class_negative_active_spec():
    ok, _ = check.is_retirement_class(
        {"id": "SPEC-3", "status": "active", "type": "requirement", "description": "active"}
    )
    assert not ok


def test_paired_by_source_spec_id():
    work_items = [{"id": "WI-1", "source_spec_id": FIXTURE_SPEC}]
    assert check.paired_work_item(FIXTURE_SPEC, work_items) == "WI-1"


def test_paired_by_purges_token():
    work_items = [{"id": "WI-2", "description": f"purges: {FIXTURE_SPEC} residue"}]
    assert check.paired_work_item(FIXTURE_SPEC, work_items) == "WI-2"


def test_paired_by_purge_project_member():
    work_items = [
        {
            "id": "WI-3",
            "project_name": "PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE",
            "description": f"strip {FIXTURE_SPEC} references",
        }
    ]
    assert check.paired_work_item(FIXTURE_SPEC, work_items) is None
    assert check.paired_work_item(FIXTURE_SPEC, work_items, purge_member_ids={"WI-3"}) == "WI-3"


def test_unpaired_returns_none():
    work_items = [{"id": "WI-9", "description": "unrelated", "project_name": "OTHER"}]
    assert check.paired_work_item(FIXTURE_SPEC, work_items) is None


def test_in_window_boundary():
    start = check._window_start(None)
    assert check.in_window("2026-06-25T00:00:00Z", window_start=start)
    assert not check.in_window("2026-06-01T00:00:00Z", window_start=start)
    assert not check.in_window(None, window_start=start)


# ---------------------------------------------------------------------------
# Native response tests (GET stubs; no canonical mutation)
# ---------------------------------------------------------------------------


def _fixture_native(tmp_path: Path, monkeypatch, *, paired=False):
    monkeypatch.setenv("GT_AUTHORITY_URL", "http://127.0.0.1:12345")
    sentinel = tmp_path / "groundtruth.db"
    sentinel.write_bytes(b"inert leftover")

    def refuse(*args, **kwargs):
        pytest.fail("Purge pairing must not open SQLite")

    monkeypatch.setattr("sqlite3.connect", refuse)

    def request(self, method, path, *, body=None, query=None):
        assert method == "GET" and body is None
        if path == "/v1/specifications":
            rows = [
                {"id": FIXTURE_SPEC, "status": "active", "type": "requirement", "changed_at": "2026-09-19T00:00:00Z"}
            ]
        elif path == "/v1/work-items":
            rows = [{"id": "WI-FIXTURE-PURGE", "source_spec_id": FIXTURE_SPEC}] if paired else []
        else:
            assert path == "/v1/projects"
            rows = []
        return {"records": rows, "next_after": None}

    monkeypatch.setattr(AuthorityClient, "request", request)
    return sentinel


def test_unpaired_retirement_in_window_warns(tmp_path, monkeypatch):
    sentinel = _fixture_native(tmp_path, monkeypatch)
    result = check.evaluate(tmp_path, obligation_effective_date=PAST_DATE)
    assert result["status"] == "warning"
    assert [row["artifact_id"] for row in result["unpaired"]] == [FIXTURE_SPEC]
    assert sentinel.read_bytes() == b"inert leftover"


def test_paired_retirement_passes(tmp_path, monkeypatch):
    _fixture_native(tmp_path, monkeypatch, paired=True)
    result = check.evaluate(tmp_path, obligation_effective_date=PAST_DATE)
    assert result["status"] == "pass"
    assert result["unpaired"] == []
    assert result["paired"][0]["pair_work_item"] == "WI-FIXTURE-PURGE"


def test_pre_obligation_retirement_excluded(tmp_path, monkeypatch):
    _fixture_native(tmp_path, monkeypatch)
    result = check.evaluate(tmp_path, obligation_effective_date=FUTURE_DATE)
    assert result["status"] == "pass"
    assert result["evaluated"] == 0


def test_doctor_surface_warn_pass_failsoft(tmp_path, monkeypatch):
    from groundtruth_kb.project.doctor import _check_obsolete_reference_purge

    _fixture_native(tmp_path, monkeypatch)
    result = _check_obsolete_reference_purge(tmp_path)
    assert result.status == "warning"
    assert FIXTURE_SPEC in result.message
    assert (tmp_path / "groundtruth.db").read_bytes() == b"inert leftover"


def test_check_script_exists_at_declared_path():
    # DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001 assertion 3.
    assert (_PROJECT_ROOT / "scripts" / "check_obsolete_reference_purge.py").is_file()


@pytest.mark.parametrize(
    "memberships",
    [None, [], [{"work_item_id": "WI-PURGE", "project_id": "PROJECT-OBSOLETE-REFERENCE-PURGE", "status": "active"}]],
)
def test_only_native_project_membership_covers_project_pairing(tmp_path, monkeypatch, memberships):
    _fixture_native(tmp_path, monkeypatch)
    original = AuthorityClient.request

    def request(self, method, path, **kwargs):
        if path == "/v1/work-items":
            return {
                "records": [
                    {
                        "id": "WI-PURGE",
                        "project_name": "PROJECT-OBSOLETE-REFERENCE-PURGE",
                        "description": f"Remove {FIXTURE_SPEC} references",
                    }
                ],
                "next_after": None,
            }
        if path == "/v1/projects":
            return {"records": [{"id": "PROJECT-OBSOLETE-REFERENCE-PURGE", "kind": "project"}], "next_after": None}
        if path == "/v1/projects/PROJECT-OBSOLETE-REFERENCE-PURGE":
            return {} if memberships is None else {"memberships": memberships}
        return original(self, method, path, **kwargs)

    monkeypatch.setattr(AuthorityClient, "request", request)
    if memberships is None:
        with pytest.raises(check.AuthorityClientError, match="memberships are malformed"):
            check.evaluate(tmp_path)
    else:
        result = check.evaluate(tmp_path)
        assert result["status"] == ("pass" if memberships else "warning")
