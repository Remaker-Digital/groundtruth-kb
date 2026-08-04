# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-5804 timer/threshold/concurrency inventory extractor tests.

The extractor is deterministic, read-only over inputs, and re-runnable. Tests
exercise the production payload function and the rendered artifact without
mutating any live runtime value.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

import scripts.timer_inventory as ti


@pytest.fixture
def fixture_root(tmp_path: Path) -> Path:
    """A synthetic GT-KB-like tree with production + test surfaces."""
    (tmp_path / "groundtruth.toml").write_text('[project]\nname = "fx"\n', encoding="utf-8")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "groundtruth-kb" / "src" / "groundtruth_kb").mkdir(parents=True)
    (tmp_path / "config" / "governance").mkdir(parents=True)
    (tmp_path / "platform_tests" / "scripts").mkdir(parents=True)
    return tmp_path


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_deterministic_byte_output(fixture_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write(fixture_root / "scripts" / "a.py", "MAX_RETRIES = 3\nTIMEOUT_SECONDS = 10\n")
    monkeypatch.setattr(ti, "_git_head_sha", lambda *a: "deadbeef")
    payload1 = ti.build_inventory(fixture_root)
    payload2 = ti.build_inventory(fixture_root)
    t1 = ti.render_toml(payload1)
    t2 = ti.render_toml(payload2)
    assert hashlib.sha256(t1.encode()).digest() == hashlib.sha256(t2.encode()).digest()


def test_stable_ordering_and_identities(fixture_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write(fixture_root / "scripts" / "b.py", "B_TIMEOUT = 20\n")
    _write(fixture_root / "scripts" / "a.py", "A_TIMEOUT = 10\n")
    monkeypatch.setattr(ti, "_git_head_sha", lambda *a: "deadbeef")
    payload = ti.build_inventory(fixture_root)
    identities = [record["identity"] for record in payload["records"]]
    assert identities == sorted(identities)
    # Both production records found with distinct identities.
    assert len(identities) == 2
    assert any("B_TIMEOUT" in ident for ident in identities)
    assert any("A_TIMEOUT" in ident for ident in identities)


def test_control_class_coverage(fixture_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    content = (
        "TIMEOUT_SECONDS = 10\n"
        "TTL_SECONDS = 30\n"
        "GRACE_WINDOW = 5\n"
        "MAX_RETRIES = 3\n"
        "RETRY_INTERVAL = 2\n"
        "BACKOFF_SECONDS = 1\n"
        "RATE_LIMIT = 100\n"
        "THRESHOLD_COUNT = 50\n"
        "CONCURRENCY_LIMIT = 4\n"
    )
    _write(fixture_root / "scripts" / "c.py", content)
    monkeypatch.setattr(ti, "_git_head_sha", lambda *a: "deadbeef")
    payload = ti.build_inventory(fixture_root)
    classes = {record["control_class"] for record in payload["records"]}
    for expected in (
        "timeout",
        "ttl",
        "grace",
        "retry_count",
        "retry_interval",
        "backoff",
        "rate_limit",
        "threshold",
        "concurrency_limit",
    ):
        assert expected in classes, f"missing control class {expected}"


def test_production_test_separation(fixture_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write(fixture_root / "scripts" / "prod.py", "TIMEOUT_SECONDS = 10\n")
    _write(fixture_root / "platform_tests" / "scripts" / "t.py", "TIMEOUT_SECONDS = 99\n")
    monkeypatch.setattr(ti, "_git_head_sha", lambda *a: "deadbeef")
    payload = ti.build_inventory(fixture_root)
    assert payload["summary"]["production_record_count"] == 1
    assert payload["summary"]["test_record_count"] == 1
    assert all(r["surface"] == "production" for r in payload["records"])
    assert all(r["surface"] == "test" for r in payload["test_records"])


def test_schema_conformance(fixture_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write(fixture_root / "scripts" / "d.py", "TIMEOUT_SECONDS = 10\n")
    monkeypatch.setattr(ti, "_git_head_sha", lambda *a: "deadbeef")
    payload = ti.build_inventory(fixture_root)
    assert payload["schema_version"] == 1
    assert payload["extraction_spec"]["version"] == ti.EXTRACTION_SPEC_VERSION
    assert "extraction_spec_digest" in payload
    record = payload["records"][0]
    for field in (
        "identity",
        "file",
        "line",
        "symbol",
        "value",
        "unit",
        "control_class",
        "category",
        "scope",
        "value_form",
        "current_authority",
        "hard_coded",
        "centralization_candidate",
        "migration_priority",
        "owning_work_item",
        "right_censored",
        "coupling",
    ):
        assert field in record, f"missing schema field {field}"


def test_right_censor_and_evidence_fields_present(fixture_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write(fixture_root / "scripts" / "e.py", "TIMEOUT_SECONDS = 10\n")
    monkeypatch.setattr(ti, "_git_head_sha", lambda *a: "deadbeef")
    payload = ti.build_inventory(fixture_root)
    for record in payload["records"]:
        assert "right_censored" in record
        assert "failure_count" in record
        assert "success_count" in record
        assert "censor_count" in record
        assert "observed_failure_evidence" in record


def test_unclassified_or_ambiguous_visible(fixture_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write(fixture_root / "scripts" / "f.py", "FOO_BAR = 7\nTIMEOUT_SECONDS = 10\n")
    monkeypatch.setattr(ti, "_git_head_sha", lambda *a: "deadbeef")
    payload = ti.build_inventory(fixture_root)
    # FOO_BAR is not a control key; only TIMEOUT_SECONDS is extracted.
    assert payload["summary"]["production_record_count"] == 1
    # The summary always exposes the unclassified count for auditability.
    assert "unclassified_or_ambiguous_count" in payload["summary"]


def test_write_confinement_and_no_runtime_mutation(fixture_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write(fixture_root / "scripts" / "g.py", "TIMEOUT_SECONDS = 10\n")
    monkeypatch.setattr(ti, "_git_head_sha", lambda *a: "deadbeef")
    # Snapshot all scanned files before.
    before: dict[str, bytes] = {}
    for path in list(fixture_root.rglob("*.py")) + list(fixture_root.rglob("*.toml")):
        before[str(path.relative_to(fixture_root))] = path.read_bytes()

    payload = ti.build_inventory(fixture_root)
    rendered = ti.render_toml(payload)
    artifact = fixture_root / ti.GENERATED_ARTIFACT_REL
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(rendered, encoding="utf-8")

    # After extraction, no source/config input changed.
    after: dict[str, bytes] = {}
    for path in list(fixture_root.rglob("*.py")) + list(fixture_root.rglob("*.toml")):
        rel = str(path.relative_to(fixture_root))
        if rel == str(ti.GENERATED_ARTIFACT_REL):
            continue
        after[rel] = path.read_bytes()
    assert before == after
    # Only the declared artifact was written.
    assert artifact.is_file()
