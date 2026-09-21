"""TEST-11323 - acceptance coverage for the superseded-SOT-leakage evaluator.

Maps to DCL-SUPERSEDED-SOT-LEAKAGE-001 outer assertions SOT-LEAK-A1..A4:

- A1 current formal artifacts + every active-surface class scanned with
  complete currentness evidence; a missing provider cannot PASS.
- A2 historical bridge/deliberation/evidence fixtures stay non-operative and
  raise no critical false positive.
- A3 retired-registry sentinels and active guard references are KEEP only with
  current enforcement evidence and no active-authority effect.
- A4 a stale active reference yields exactly one deduplicated P0 finding with
  deterministic remediation, and blocks the gate.

Work item: WI-5154.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
_MODULE_PATH = REPO_ROOT / "scripts" / "check_superseded_sot_leakage.py"


def _load_module() -> Any:
    spec = importlib.util.spec_from_file_location("check_superseded_sot_leakage", _MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_superseded_sot_leakage"] = module
    spec.loader.exec_module(module)
    return module


mod = _load_module()


class _FakeClient:
    """Native GET response fixture for the existing list route."""

    def __init__(self, specs: list[dict[str, Any]]) -> None:
        self._specs = specs

    def request(self, method, path, *, body=None, query=None):
        assert method == "GET" and path == "/v1/specifications" and body is None
        assert "status" not in query
        return {"records": list(self._specs), "next_after": None}


RETIRED_ID = "GOV-SESSION-ROLE-AUTHORITY-001"
SENTINEL_ID = "RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001"
LIVE_ID = "GOV-FILE-BRIDGE-AUTHORITY-001"


def _client() -> _FakeClient:
    return _FakeClient(
        [
            {"id": RETIRED_ID, "status": "retired", "version": 6, "retired_at": "2026-07-29", "title": "retired"},
            {"id": SENTINEL_ID, "status": "retired", "version": 1, "retired_at": "2026-06-01", "title": "sentinel"},
            {"id": LIVE_ID, "status": "verified", "version": 3, "retired_at": "", "title": "live"},
        ]
    )


def _seed(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# SOT-LEAK-A1
# ---------------------------------------------------------------------------


def test_a1_scans_active_surface_classes_with_currentness_evidence(tmp_path: Path) -> None:
    _seed(tmp_path, ".harness-baseline-configuration/rules/example.md", f"Follow {LIVE_ID} for bridge authority.\n")
    report = mod.scan(tmp_path, client=_client())

    for provider in mod.REQUIRED_PROVIDERS:
        assert provider in report.providers, provider
    assert report.providers[mod.PROVIDER_CURRENT_FORMAL_ARTIFACTS]["resolved"] is True
    assert report.providers[mod.PROVIDER_ACTIVE_SURFACE_CLASSES]["resolved"] is True
    assert report.providers[mod.PROVIDER_CURRENTNESS_EVIDENCE]["resolved"] is True
    # Currentness evidence is bound to the evaluator version and record count.
    assert report.providers[mod.PROVIDER_CURRENTNESS_EVIDENCE]["evaluator_version"] == mod.EVALUATOR_VERSION
    assert report.providers[mod.PROVIDER_CURRENT_FORMAL_ARTIFACTS]["superseded_record_count"] == 2
    # A live id is not a superseded authority.
    assert report.counts["findings"] == 0
    assert report.result == mod.RESULT_PASS
    assert report.gate_blocked is False


def test_a1_missing_provider_never_passes(tmp_path: Path) -> None:
    """No active surface resolves -> PARTIAL + gate blocked, never PASS."""
    report = mod.scan(tmp_path, client=_client())
    assert report.providers[mod.PROVIDER_ACTIVE_SURFACE_CLASSES]["resolved"] is False
    assert mod.MISSING_PROVIDER in report.providers[mod.PROVIDER_ACTIVE_SURFACE_CLASSES]["reason"]
    assert report.result == mod.RESULT_PARTIAL
    assert report.result != mod.RESULT_PASS
    assert report.gate_blocked is True


def test_a1_missing_formal_record_provider_is_unassessed(tmp_path: Path) -> None:
    """An unresolvable native provider yields UNASSESSED, not PASS."""

    class _Broken:
        def request(self, *args, **kwargs):
            raise RuntimeError("native authority unavailable")

    report = mod.scan(tmp_path, client=_Broken())
    assert report.result == mod.RESULT_UNASSESSED
    assert report.gate_blocked is True
    assert mod.MISSING_PROVIDER in report.providers[mod.PROVIDER_CURRENT_FORMAL_ARTIFACTS]["reason"]


# ---------------------------------------------------------------------------
# SOT-LEAK-A2
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("rel", "expected"),
    [
        ("bridge/gtkb-example-001.md", mod.HISTORICAL_BRIDGE),
        ("deliberations/DELIB-1.md", mod.HISTORICAL_DELIBERATION),
        ("archive/old/thing.md", mod.HISTORICAL_ARCHIVE),
        (".gtkb-state/evidence.json", mod.HISTORICAL_EVIDENCE),
        ("bridge/cleanup-evidence/wi1/report.md", mod.HISTORICAL_BRIDGE),
        (".harness-baseline-configuration/rules/live.md", "active"),
    ],
)
def test_a2_lifecycle_classification(rel: str, expected: str) -> None:
    assert mod.classify_lifecycle(rel) == expected


def test_a2_historical_fixture_raises_no_critical_finding(tmp_path: Path) -> None:
    """Append-only history preserving a retired literal is not active residue."""
    _seed(tmp_path, "bridge/gtkb-old-001.md", f"This thread cited {RETIRED_ID} at the time.\n")
    _seed(tmp_path, ".harness-baseline-configuration/rules/live.md", f"See {LIVE_ID}.\n")
    report = mod.scan(tmp_path, client=_client())

    # bridge/ is not an active-surface class, so it contributes no P0 at all.
    assert report.counts[mod.SEVERITY_P0] == 0
    assert report.gate_blocked is False
    assert report.result == mod.RESULT_PASS


# ---------------------------------------------------------------------------
# SOT-LEAK-A3
# ---------------------------------------------------------------------------


def test_a3_retired_registry_sentinel_is_keep(tmp_path: Path) -> None:
    _seed(tmp_path, ".harness-baseline-configuration/rules/registry.md", f"{SENTINEL_ID} tracks the legacy mirror.\n")
    report = mod.scan(tmp_path, client=_client())

    assert len(report.findings) == 1
    finding = report.findings[0]
    assert finding.disposition == mod.KEEP
    assert finding.severity == mod.SEVERITY_INFO
    assert mod.RETIRED_REGISTRY_SENTINEL in finding.authority
    assert mod.NO_ACTIVE_AUTHORITY_EFFECT in finding.authority
    assert mod.CURRENT_ENFORCEMENT_EVIDENCE in finding.remediation
    assert report.gate_blocked is False


def test_a3_active_guard_reference_is_keep_with_enforcement_evidence(tmp_path: Path) -> None:
    """A citing line that enforces retirement cannot direct current behavior."""
    _seed(
        tmp_path,
        ".harness-baseline-configuration/rules/guard.md",
        f"{RETIRED_ID} is retired; do not use it as authority.\n",
    )
    report = mod.scan(tmp_path, client=_client())

    assert len(report.findings) == 1
    finding = report.findings[0]
    assert finding.disposition == mod.KEEP
    assert mod.ACTIVE_GUARD_REFERENCE in finding.authority
    assert mod.CURRENT_ENFORCEMENT_EVIDENCE in finding.remediation
    assert report.gate_blocked is False


def test_a3_keep_requires_enforcement_not_mere_mention(tmp_path: Path) -> None:
    """Without enforcement evidence the same id on the same surface is STRIP/P0."""
    _seed(
        tmp_path,
        ".harness-baseline-configuration/rules/instruct.md",
        f"Resolve the session role through {RETIRED_ID}.\n",
    )
    report = mod.scan(tmp_path, client=_client())

    assert len(report.findings) == 1
    assert report.findings[0].disposition == mod.STRIP
    assert report.findings[0].severity == mod.SEVERITY_P0


# ---------------------------------------------------------------------------
# SOT-LEAK-A4
# ---------------------------------------------------------------------------


def test_a4_stale_active_reference_is_blocking_p0_with_remediation(tmp_path: Path) -> None:
    _seed(
        tmp_path,
        ".harness-baseline-configuration/rules/instruct.md",
        f"Resolve the session role through {RETIRED_ID}.\n",
    )
    report = mod.scan(tmp_path, client=_client())

    assert len(report.findings) == 1
    finding = report.findings[0]
    assert finding.authority == mod.STALE_ACTIVE
    assert finding.severity == mod.SEVERITY_P0
    assert finding.disposition == mod.STRIP
    assert mod.DETERMINISTIC_REMEDIATION in finding.remediation
    assert RETIRED_ID in finding.remediation
    assert "gt assert --spec DCL-SUPERSEDED-SOT-LEAKAGE-001" in finding.recovery_route
    # gate-block
    assert report.result == mod.RESULT_FAIL
    assert report.gate_blocked is True


def test_a4_duplicate_occurrences_deduplicate_to_one_finding(tmp_path: Path) -> None:
    """Repeated occurrences of one subject in one path are a single finding."""
    _seed(
        tmp_path,
        ".harness-baseline-configuration/rules/instruct.md",
        f"Use {RETIRED_ID} now.\nAlso use {RETIRED_ID} here.\nAnd {RETIRED_ID} again.\n",
    )
    report = mod.scan(tmp_path, client=_client())

    assert len(report.findings) == 1, "duplicate inventory paths must not inflate count"
    assert report.counts[mod.SEVERITY_P0] == 1


def test_a4_finding_contract_fields_present(tmp_path: Path) -> None:
    """Every DCL finding-contract field is populated on a real finding."""
    _seed(tmp_path, ".harness-baseline-configuration/rules/instruct.md", f"Resolve through {RETIRED_ID}.\n")
    report = mod.scan(tmp_path, client=_client())
    finding = report.findings[0]

    assert finding.finding_id.startswith("SOTLEAK-")
    assert finding.artifact_identity.endswith(".harness-baseline-configuration/rules/instruct.md")
    assert finding.line == 1
    assert finding.surface_class == "rule"
    assert finding.lifecycle == "active"
    assert finding.subject_version == "6"
    assert finding.subject_hash.startswith("sha256:")
    assert finding.currentness_evidence["subject_status"] == "retired"
    assert finding.affected_gate
    assert finding.disposition in {mod.STRIP, mod.KEEP, mod.QUARANTINE}
    assert finding.remediation and finding.recovery_route


def test_scan_is_deterministic_across_runs(tmp_path: Path) -> None:
    _seed(tmp_path, ".harness-baseline-configuration/rules/instruct.md", f"Resolve through {RETIRED_ID}.\n")
    first = mod.scan(tmp_path, client=_client()).to_dict()
    second = mod.scan(tmp_path, client=_client()).to_dict()
    assert first == second


def test_main_exit_code_blocks_on_stale_active(tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch) -> None:
    """The ordinary CLI reads configured native pages and exits non-zero on leakage."""
    from groundtruth_kb.authority_client import AuthorityClient

    _seed(tmp_path, ".harness-baseline-configuration/rules/instruct.md", f"Resolve through {RETIRED_ID}.\n")
    monkeypatch.setenv("GT_AUTHORITY_URL", "http://127.0.0.1:12345")
    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))
    pages = []
    records = _client()._specs

    def refuse(*args, **kwargs):
        pytest.fail("Leakage scanner must not open SQLite")

    def request(self, method, path, *, body=None, query=None):
        assert method == "GET" and path == "/v1/specifications" and body is None
        assert "status" not in query
        pages.append(query.get("after"))
        return {
            "records": records[:1] if not query.get("after") else records[1:],
            "next_after": "page-1" if not query.get("after") else None,
        }

    monkeypatch.setattr("sqlite3.connect", refuse)
    monkeypatch.setattr(AuthorityClient, "request", request)
    assert mod.main(["--project-root", str(tmp_path)]) == 1
    assert "gate_blocked=True" in capsys.readouterr().out
    assert pages == [None, "page-1"]
    assert sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*")) == before


def test_default_native_provider_outage_never_falls_back_to_local_database(tmp_path, monkeypatch):
    from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError

    sentinel = tmp_path / "groundtruth.db"
    sentinel.write_bytes(b"inert local file")
    monkeypatch.setenv("GT_AUTHORITY_URL", "http://127.0.0.1:12345")

    def refuse(*args, **kwargs):
        pytest.fail("Local database fallback is forbidden")

    def unavailable(self, *args, **kwargs):
        raise AuthorityClientError("authority_unavailable", "Selected authority unavailable")

    monkeypatch.setattr("sqlite3.connect", refuse)
    monkeypatch.setattr(AuthorityClient, "request", unavailable)
    report = mod.scan(tmp_path)
    assert report.result == mod.RESULT_UNASSESSED and report.gate_blocked
    assert "Selected authority unavailable" in report.providers[mod.PROVIDER_CURRENT_FORMAL_ARTIFACTS]["reason"]
    assert sentinel.read_bytes() == b"inert local file"
